"""Generate grounded policy answers from retrieved evidence context.

This module owns the first end-to-end answer path: it calls the existing
retrieval pipeline, sends the assembled evidence context to an OpenAI chat
model through LangChain, and returns a structured answer with citations,
confidence, and abstention state. It does not search Chroma directly outside
the retrieval modules and it does not implement the future judge step.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.core.config import ROOT_DIR, Settings
from app.retrieval.step01_search_chunks import RetrievalFilters, search_chunks
from app.retrieval.step02_rerank_chunks import rerank_chunks
from app.retrieval.step03_assemble_context import (
    AssembledContext,
    EvidenceBlock,
    assemble_context,
)


PROMPTS_DIR = ROOT_DIR / "app" / "prompts"
WEAK_EVIDENCE_MIN_RERANK_SCORE = 0.05


class AnswerGenerationError(RuntimeError):
    """Raised when answer generation cannot produce a usable answer result."""


class AnswerModelOutput(BaseModel):
    """Schema returned by the answer model before deterministic validation."""

    answer: str = Field(description="Concise policy answer with citation markers.")
    citations: list[str] = Field(
        description="Citation IDs used in the answer, such as [1] or [2]."
    )
    confidence: Literal["high", "medium", "low"] = Field(
        description="How directly the retrieved evidence supports the answer."
    )
    abstained: bool = Field(
        description="Whether the model refused to answer due to weak evidence."
    )


@dataclass(frozen=True)
class GroundedAnswer:
    """Structured answer-generation result for CLI, API, and future UI callers."""

    question: str
    answer: str
    citations: list[str]
    confidence: str
    abstained: bool
    evidence_blocks: list[EvidenceBlock]
    context_text: str
    raw_model_output: str | None = None
    validation_warnings: list[str] | None = None


def answer_policy_question(
    settings: Settings,
    question: str,
    *,
    filters: RetrievalFilters | None = None,
    search_k: int | None = None,
) -> GroundedAnswer:
    """Retrieve policy evidence and generate a grounded answer from it."""
    assembled_context = retrieve_answer_context(
        settings,
        question,
        filters=filters,
        search_k=search_k,
    )
    weak_evidence_reason = _weak_evidence_reason(assembled_context)
    if weak_evidence_reason is not None:
        return _build_abstention_answer(
            question=question,
            assembled_context=assembled_context,
            reason=weak_evidence_reason,
            validation_warnings=[weak_evidence_reason],
        )

    model_output, raw_output = _invoke_answer_model(
        settings,
        question,
        assembled_context.context_text,
    )
    return build_grounded_answer_from_model_output(
        question=question,
        assembled_context=assembled_context,
        model_output=model_output,
        raw_model_output=raw_output,
    )


def build_grounded_answer_from_model_output(
    *,
    question: str,
    assembled_context: AssembledContext,
    model_output: AnswerModelOutput,
    raw_model_output: str | None,
) -> GroundedAnswer:
    """Validate parsed model output and return the final grounded answer."""
    validation_warnings = _validate_model_output(
        model_output,
        evidence_blocks=assembled_context.evidence_blocks,
    )
    if validation_warnings:
        return _build_abstention_answer(
            question=question,
            assembled_context=assembled_context,
            reason=(
                "The answer model produced output that failed grounding "
                "validation, so I am abstaining instead of returning it."
            ),
            raw_model_output=raw_model_output,
            validation_warnings=validation_warnings,
        )

    return GroundedAnswer(
        question=question,
        answer=model_output.answer.strip(),
        citations=_normalize_citations(model_output.citations),
        confidence=model_output.confidence,
        abstained=model_output.abstained,
        evidence_blocks=assembled_context.evidence_blocks,
        context_text=assembled_context.context_text,
        raw_model_output=raw_model_output,
        validation_warnings=[],
    )


def retrieve_answer_context(
    settings: Settings,
    question: str,
    *,
    filters: RetrievalFilters | None = None,
    search_k: int | None = None,
) -> AssembledContext:
    """Run the existing retrieval pipeline and return assembled evidence context."""
    retrieved_chunks = search_chunks(
        settings,
        question,
        k=search_k,
        filters=filters,
    )
    reranked_chunks = rerank_chunks(
        question,
        retrieved_chunks,
        model_name=settings.rerank_model,
        top_k=settings.retrieval_rerank_k,
    )
    return assemble_context(
        reranked_chunks,
        max_blocks=settings.retrieval_context_k,
        max_total_tokens=settings.retrieval_context_max_tokens,
        max_block_tokens=settings.retrieval_context_max_block_tokens,
    )


def _invoke_answer_model(
    settings: Settings,
    question: str,
    context_text: str,
) -> tuple[AnswerModelOutput, str | None]:
    try:
        from langchain_openai import ChatOpenAI
    except ImportError as exc:
        raise AnswerGenerationError(
            "Answer generation requires langchain-openai. Run "
            "`python -m pip install -e .` from the project root."
        ) from exc

    model = ChatOpenAI(model=settings.answer_model)
    structured_model = model.with_structured_output(
        AnswerModelOutput,
        include_raw=True,
    )
    response = structured_model.invoke(build_answer_messages(question, context_text))

    if not isinstance(response, dict):
        raise AnswerGenerationError(
            "Answer model returned an unexpected structured-output response."
        )

    raw_response = response.get("raw")
    parsing_error = response.get("parsing_error")
    if parsing_error is not None:
        raise AnswerGenerationError(
            f"Answer model failed structured-output parsing: {parsing_error}"
        )

    parsed = response.get("parsed")
    if not isinstance(parsed, AnswerModelOutput):
        raise AnswerGenerationError(
            "Answer model did not return the expected answer schema."
        )
    return parsed, _raw_response_to_text(raw_response)


def build_answer_messages(question: str, context_text: str) -> list[dict[str, str]]:
    """Build the chat messages used by non-streaming and streaming answers."""
    return [
        {"role": "system", "content": _read_prompt("system.md")},
        {
            "role": "user",
            "content": _build_answer_prompt(question, context_text),
        },
    ]


def parse_answer_model_json(raw_text: str) -> AnswerModelOutput:
    """Parse JSON text returned by a streamed answer model response."""
    candidate = _strip_json_fences(raw_text.strip())
    try:
        payload = json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise AnswerGenerationError(
            f"Answer model returned invalid JSON: {exc.msg}."
        ) from exc
    return AnswerModelOutput.model_validate(payload)


def build_abstention_answer(
    *,
    question: str,
    assembled_context: AssembledContext,
    reason: str,
    raw_model_output: str | None = None,
    validation_warnings: list[str] | None = None,
) -> GroundedAnswer:
    """Return a deterministic abstention answer for shared callers."""
    return _build_abstention_answer(
        question=question,
        assembled_context=assembled_context,
        reason=reason,
        raw_model_output=raw_model_output,
        validation_warnings=validation_warnings,
    )


def weak_evidence_reason(assembled_context: AssembledContext) -> str | None:
    """Return a deterministic reason when retrieved evidence is too weak."""
    return _weak_evidence_reason(assembled_context)


def _build_answer_prompt(question: str, context_text: str) -> str:
    fewshot = _read_prompt("answer_fewshot.md")
    return (
        f"{fewshot}\n\n"
        "## Current User Question\n\n"
        f"{question.strip()}\n\n"
        "## Retrieved Evidence\n\n"
        f"{context_text.strip()}\n\n"
        "Return only the JSON object for the current user question."
    )


def _strip_json_fences(text: str) -> str:
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _read_prompt(filename: str) -> str:
    path = PROMPTS_DIR / filename
    return path.read_text(encoding="utf-8").strip()


def _message_content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
        return "\n".join(parts).strip()
    return str(content).strip()


def _raw_response_to_text(raw_response: Any) -> str | None:
    if raw_response is None:
        return None
    content = getattr(raw_response, "content", None)
    if content not in (None, ""):
        return _message_content_to_text(content)
    return repr(raw_response)


def _normalize_citations(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    citations: list[str] = []
    for item in value:
        citation = str(item).strip()
        if re.fullmatch(r"\[\d+\]", citation):
            citations.append(citation)
    return citations


def _weak_evidence_reason(assembled_context: AssembledContext) -> str | None:
    if not assembled_context.evidence_blocks:
        return "No retrieved evidence blocks were available for this question."

    rerank_scores = [
        block.rerank_score
        for block in assembled_context.evidence_blocks
        if block.rerank_score is not None
    ]
    if rerank_scores and max(rerank_scores) < WEAK_EVIDENCE_MIN_RERANK_SCORE:
        return (
            "Retrieved evidence was below the minimum relevance threshold "
            f"({WEAK_EVIDENCE_MIN_RERANK_SCORE:.2f})."
        )
    return None


def _validate_model_output(
    output: AnswerModelOutput,
    *,
    evidence_blocks: list[EvidenceBlock],
) -> list[str]:
    warnings: list[str] = []
    valid_citations = {block.citation_id for block in evidence_blocks}
    normalized_citations = _normalize_citations(output.citations)
    answer_citations = set(re.findall(r"\[\d+\]", output.answer))

    if output.answer.strip() == "":
        warnings.append("Answer text is empty.")

    invalid_citations = [
        citation
        for citation in normalized_citations
        if citation not in valid_citations
    ]
    if invalid_citations:
        warnings.append(
            "Answer cited evidence IDs that were not in the assembled context: "
            f"{', '.join(invalid_citations)}."
        )

    listed_but_missing = [
        citation
        for citation in normalized_citations
        if citation not in answer_citations
    ]
    if listed_but_missing:
        warnings.append(
            "Answer listed citations that do not appear in the answer text: "
            f"{', '.join(listed_but_missing)}."
        )

    unlisted_answer_citations = [
        citation
        for citation in sorted(answer_citations)
        if citation not in normalized_citations
    ]
    if unlisted_answer_citations:
        warnings.append(
            "Answer text contains citations missing from the citations field: "
            f"{', '.join(unlisted_answer_citations)}."
        )

    if not output.abstained and not normalized_citations:
        warnings.append("Non-abstained answers must include at least one citation.")

    if output.abstained and output.confidence != "low":
        warnings.append("Abstained answers must use low confidence.")

    return warnings


def _build_abstention_answer(
    *,
    question: str,
    assembled_context: AssembledContext,
    reason: str,
    raw_model_output: str | None = None,
    validation_warnings: list[str] | None = None,
) -> GroundedAnswer:
    return GroundedAnswer(
        question=question,
        answer=f"{reason} I cannot make a grounded policy decision from this evidence.",
        citations=[],
        confidence="low",
        abstained=True,
        evidence_blocks=assembled_context.evidence_blocks,
        context_text=assembled_context.context_text,
        raw_model_output=raw_model_output,
        validation_warnings=validation_warnings or [],
    )
