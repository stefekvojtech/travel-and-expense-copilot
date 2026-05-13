"""Streaming orchestration for grounded chat answers.

This module keeps transport-agnostic streaming behavior outside the FastAPI
route layer. It emits small event payloads that the API can serialize as
server-sent events for the future browser UI.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from app.agents.answer import (
    AnswerGenerationError,
    build_abstention_answer,
    build_answer_messages,
    build_grounded_answer_from_model_output,
    parse_answer_model_json,
    retrieve_answer_context,
    weak_evidence_reason,
)
from app.core.config import Settings
from app.core.openai_clients import build_openai_http_client
from app.retrieval.step01_search_chunks import RetrievalFilters
from app.retrieval.step03_assemble_context import EvidenceBlock


ChatStreamEvent = tuple[str, dict[str, Any]]


def stream_grounded_answer_events(
    settings: Settings,
    question: str,
    *,
    filters: RetrievalFilters | None = None,
    search_k: int | None = None,
) -> Iterator[ChatStreamEvent]:
    """Yield retrieval, answer-token, and final-result events for one question."""
    yield "retrieval_started", {"question": question}

    assembled_context = retrieve_answer_context(
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
        yield "answer_complete", _grounded_answer_to_dict(answer)
        return

    try:
        from langchain_openai import ChatOpenAI
    except ImportError as exc:
        raise AnswerGenerationError(
            "Streaming answer generation requires langchain-openai. Run "
            "`python -m pip install -e .` from the project root."
        ) from exc

    yield "answer_started", {"model": settings.answer_model}

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

    if answer.answer.startswith(emitted_answer):
        remaining_delta = answer.answer[len(emitted_answer):]
        if remaining_delta:
            yield "answer_delta", {"delta": remaining_delta}
    elif answer.answer != emitted_answer:
        yield "answer_replaced", {
            "answer": answer.answer,
            "reason": "Final validation changed the streamed draft.",
        }

    yield "answer_complete", _grounded_answer_to_dict(answer)


def _grounded_answer_to_dict(answer: Any) -> dict[str, Any]:
    return {
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


def _evidence_block_to_dict(block: EvidenceBlock) -> dict[str, Any]:
    return {
        "citation_id": block.citation_id,
        "chunk_id": block.chunk_id,
        "source_path": block.source_path,
        "doc_type": block.doc_type,
        "title": block.title,
        "section_path": block.section_path,
        "page_label": block.page_label,
        "sheet_label": block.sheet_label,
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
