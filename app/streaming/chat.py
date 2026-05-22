"""Streaming orchestration for grounded chat answers.

This module keeps transport-agnostic streaming behavior outside the FastAPI
route layer. It emits small event payloads that the API can serialize as
server-sent events for the future browser UI.
"""

from __future__ import annotations

from collections.abc import Generator, Iterator
from dataclasses import dataclass
from time import perf_counter
from typing import Any

from app.agents.answer import (
    AnswerGenerationError,
    build_abstention_answer,
    build_answer_messages,
    build_grounded_answer_from_model_output,
    parse_answer_model_json,
    weak_evidence_reason,
)
from app.core.config import Settings
from app.core.openai_clients import build_openai_http_client
from app.retrieval.step01_search_chunks import (
    RetrievalFilters,
    embed_query,
    search_chunks_by_query_embedding,
)
from app.retrieval.step02_rerank_chunks import rerank_chunks
from app.retrieval.step03_assemble_context import (
    AssembledContext,
    EvidenceBlock,
    assemble_context,
)


ChatStreamEvent = tuple[str, dict[str, Any]]


def stream_grounded_answer_events(
    settings: Settings,
    question: str,
    *,
    filters: RetrievalFilters | None = None,
    search_k: int | None = None,
) -> Iterator[ChatStreamEvent]:
    """Yield retrieval, answer-token, and final-result events for one question."""
    trace = _StreamTrace()

    yield "status_changed", {"status": "retrieving", "label": "Retrieving"}
    yield "retrieval_started", {"question": question}
    yield "trace_started", trace.started_payload()

    assembled_context = yield from _retrieve_answer_context_with_trace(
        trace,
        settings,
        question,
        filters=filters,
        search_k=search_k,
    )
    yield "retrieval_complete", {
        "evidence_blocks": [
            _evidence_block_to_dict(block)
            for block in assembled_context.evidence_blocks
        ],
        "context_text": assembled_context.context_text,
    }

    reason = weak_evidence_reason(assembled_context)
    if reason is not None:
        answer = build_abstention_answer(
            question=question,
            assembled_context=assembled_context,
            reason=reason,
            validation_warnings=[reason],
        )
        yield "answer_delta", {"delta": answer.answer}
        processing_ms = trace.elapsed_ms()
        yield "trace_complete", trace.complete_payload()
        yield "status_changed", {
            "status": "complete",
            "label": "Complete",
            "elapsed_ms": processing_ms,
        }
        yield "answer_complete", _grounded_answer_to_dict(
            answer,
            processing_ms=processing_ms,
        )
        return

    try:
        from langchain_openai import ChatOpenAI
    except ImportError as exc:
        raise AnswerGenerationError(
            "Streaming answer generation requires langchain-openai. Run "
            "`python -m pip install -e .` from the project root."
        ) from exc

    yield "status_changed", {"status": "answering", "label": "Answering"}
    yield "answer_started", {"model": settings.answer_model}
    answer_step = trace.start_step(
        step="stream_grounded_answer",
        label="Streaming grounded answer...",
        phase="answer",
        metadata={"model": settings.answer_model},
    )
    yield answer_step.started_event

    raw_text = ""
    emitted_answer = ""
    model = ChatOpenAI(
        model=settings.answer_model,
        http_client=build_openai_http_client(),
    )
    for chunk in model.stream(
        build_answer_messages(question, assembled_context.context_text)
    ):
        raw_text += _chunk_to_text(chunk)
        partial_answer = _extract_partial_json_string_field(raw_text, "answer")
        if partial_answer is None or not partial_answer.startswith(emitted_answer):
            continue

        delta = partial_answer[len(emitted_answer):]
        if delta:
            emitted_answer = partial_answer
            yield "answer_delta", {"delta": delta}

    model_output = parse_answer_model_json(raw_text)
    answer = build_grounded_answer_from_model_output(
        question=question,
        assembled_context=assembled_context,
        model_output=model_output,
        raw_model_output=raw_text,
    )
    yield trace.complete_step(
        answer_step,
        metadata={
            "model": settings.answer_model,
            "abstained": answer.abstained,
            "citation_count": len(answer.citations),
        },
    )

    if answer.answer.startswith(emitted_answer):
        remaining_delta = answer.answer[len(emitted_answer):]
        if remaining_delta:
            yield "answer_delta", {"delta": remaining_delta}
    elif answer.answer != emitted_answer:
        yield "answer_replaced", {
            "answer": answer.answer,
            "reason": "Final validation changed the streamed draft.",
        }

    processing_ms = trace.elapsed_ms()
    yield "trace_complete", trace.complete_payload()
    yield "status_changed", {
        "status": "complete",
        "label": "Complete",
        "elapsed_ms": processing_ms,
    }
    yield "answer_complete", _grounded_answer_to_dict(
        answer,
        processing_ms=processing_ms,
    )


def _retrieve_answer_context_with_trace(
    trace: "_StreamTrace",
    settings: Settings,
    question: str,
    *,
    filters: RetrievalFilters | None,
    search_k: int | None,
) -> Generator[ChatStreamEvent, None, AssembledContext]:
    search_limit = search_k if search_k is not None else settings.retrieval_top_k

    embedding_step = trace.start_step(
        step="embedding_query",
        label="Embedding query...",
        phase="retrieval",
        metadata={"model": settings.embedding_model},
    )
    yield embedding_step.started_event
    query_embedding = embed_query(settings, question)
    yield trace.complete_step(
        embedding_step,
        metadata={
            "model": settings.embedding_model,
            "dimensions": len(query_embedding),
        },
    )

    search_step = trace.start_step(
        step="search_vector_index",
        label="Searching vector index...",
        phase="retrieval",
        metadata={
            "requested_k": search_limit,
            "filters": _filters_to_dict(filters),
        },
    )
    yield search_step.started_event
    retrieved_chunks = search_chunks_by_query_embedding(
        settings,
        query_embedding,
        k=search_k,
        filters=filters,
    )
    yield trace.complete_step(
        search_step,
        metadata={
            "requested_k": search_limit,
            "result_count": len(retrieved_chunks),
            "filters": _filters_to_dict(filters),
        },
    )

    rerank_step = trace.start_step(
        step="rerank_retrieved_chunks",
        label="Reranking retrieved chunks...",
        phase="retrieval",
        metadata={
            "model": settings.rerank_model,
            "input_count": len(retrieved_chunks),
            "top_k": settings.retrieval_rerank_k,
        },
    )
    yield rerank_step.started_event
    reranked_chunks = rerank_chunks(
        question,
        retrieved_chunks,
        model_name=settings.rerank_model,
        top_k=settings.retrieval_rerank_k,
    )
    yield trace.complete_step(
        rerank_step,
        metadata={
            "model": settings.rerank_model,
            "input_count": len(retrieved_chunks),
            "result_count": len(reranked_chunks),
        },
    )

    context_step = trace.start_step(
        step="assemble_cited_context",
        label="Assembling cited context...",
        phase="retrieval",
        metadata={
            "max_blocks": settings.retrieval_context_k,
            "max_total_tokens": settings.retrieval_context_max_tokens,
        },
    )
    yield context_step.started_event
    assembled_context = assemble_context(
        reranked_chunks,
        max_blocks=settings.retrieval_context_k,
        max_total_tokens=settings.retrieval_context_max_tokens,
        max_block_tokens=settings.retrieval_context_max_block_tokens,
    )
    yield trace.complete_step(
        context_step,
        metadata={
            "evidence_block_count": len(assembled_context.evidence_blocks),
            "context_characters": len(assembled_context.context_text),
        },
    )

    return assembled_context


def _grounded_answer_to_dict(
    answer: Any,
    *,
    processing_ms: int | None = None,
) -> dict[str, Any]:
    payload = {
        "question": answer.question,
        "answer": answer.answer,
        "citations": answer.citations,
        "confidence": answer.confidence,
        "abstained": answer.abstained,
        "evidence_blocks": [
            _evidence_block_to_dict(block)
            for block in answer.evidence_blocks
        ],
        "judge_result": None,
        "debug": {
            "context_text": answer.context_text,
            "raw_model_output": answer.raw_model_output,
            "validation_warnings": answer.validation_warnings or [],
        },
    }
    if processing_ms is not None:
        payload["processing_ms"] = processing_ms
    return payload


@dataclass(frozen=True)
class _TraceStep:
    sequence: int
    step: str
    label: str
    phase: str
    started_at: float
    started_event: ChatStreamEvent


class _StreamTrace:
    def __init__(self) -> None:
        self.started_at = perf_counter()
        self._sequence = 0

    def elapsed_ms(self) -> int:
        return _duration_ms(self.started_at)

    def started_payload(self) -> dict[str, Any]:
        return {
            "label": "Processed",
            "elapsed_ms": 0,
        }

    def complete_payload(self) -> dict[str, Any]:
        return {
            "label": "Processed",
            "elapsed_ms": self.elapsed_ms(),
        }

    def start_step(
        self,
        *,
        step: str,
        label: str,
        phase: str,
        metadata: dict[str, Any] | None = None,
    ) -> _TraceStep:
        self._sequence += 1
        started_at = perf_counter()
        started_event = (
            "trace_step_started",
            {
                "sequence": self._sequence,
                "step": step,
                "label": label,
                "phase": phase,
                "status": "running",
                "elapsed_ms": self.elapsed_ms(),
                "metadata": metadata or {},
            },
        )
        return _TraceStep(
            sequence=self._sequence,
            step=step,
            label=label,
            phase=phase,
            started_at=started_at,
            started_event=started_event,
        )

    def complete_step(
        self,
        trace_step: _TraceStep,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> ChatStreamEvent:
        return (
            "trace_step_completed",
            {
                "sequence": trace_step.sequence,
                "step": trace_step.step,
                "label": trace_step.label,
                "phase": trace_step.phase,
                "status": "completed",
                "elapsed_ms": self.elapsed_ms(),
                "duration_ms": _duration_ms(trace_step.started_at),
                "metadata": metadata or {},
            },
        )


def _duration_ms(started_at: float) -> int:
    return max(round((perf_counter() - started_at) * 1000), 0)


def _filters_to_dict(filters: RetrievalFilters | None) -> dict[str, str]:
    if filters is None:
        return {}
    return {
        key: value
        for key, value in {
            "doc_type": filters.doc_type,
            "source_path": filters.source_path,
            "section_path": filters.section_path,
        }.items()
        if value
    }


def _evidence_block_to_dict(block: EvidenceBlock) -> dict[str, Any]:
    return {
        "citation_id": block.citation_id,
        "chunk_id": block.chunk_id,
        "source_path": block.source_path,
        "doc_type": block.doc_type,
        "title": block.title,
        "section_path": block.section_path,
        "page_label": block.page_label,
        "row_number": block.row_number,
        "cosine_distance": block.cosine_distance,
        "approximate_cosine_similarity": block.approximate_cosine_similarity,
        "rerank_score": block.rerank_score,
        "text": block.text,
    }


def _chunk_to_text(chunk: Any) -> str:
    content = getattr(chunk, "content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    parts.append(text)
        return "".join(parts)
    return str(content) if content is not None else ""


def _extract_partial_json_string_field(buffer: str, field_name: str) -> str | None:
    marker = f'"{field_name}"'
    marker_index = buffer.find(marker)
    if marker_index == -1:
        return None

    colon_index = buffer.find(":", marker_index + len(marker))
    if colon_index == -1:
        return None

    index = colon_index + 1
    while index < len(buffer) and buffer[index].isspace():
        index += 1
    if index >= len(buffer) or buffer[index] != '"':
        return None

    return _read_json_string_prefix(buffer[index + 1 :])


def _read_json_string_prefix(value: str) -> str:
    result: list[str] = []
    index = 0
    while index < len(value):
        char = value[index]
        if char == '"':
            break
        if char == "\\":
            if index + 1 >= len(value):
                break
            escaped = value[index + 1]
            if escaped == "n":
                result.append("\n")
            elif escaped == "r":
                result.append("\r")
            elif escaped == "t":
                result.append("\t")
            elif escaped == "b":
                result.append("\b")
            elif escaped == "f":
                result.append("\f")
            elif escaped == "u":
                hex_value = value[index + 2 : index + 6]
                if len(hex_value) < 4:
                    break
                try:
                    result.append(chr(int(hex_value, 16)))
                except ValueError:
                    break
                index += 4
            else:
                result.append(escaped)
            index += 2
            continue
        result.append(char)
        index += 1
    return "".join(result)
