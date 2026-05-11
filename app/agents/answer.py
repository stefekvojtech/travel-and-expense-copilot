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
from typing import Any

from app.core.config import ROOT_DIR, Settings
from app.retrieval.step01_search_chunks import RetrievalFilters, search_chunks
from app.retrieval.step02_rerank_chunks import rerank_chunks
from app.retrieval.step03_assemble_context import (
    AssembledContext,
    EvidenceBlock,
    assemble_context,
)


PROMPTS_DIR = ROOT_DIR / "app" / "prompts"


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
    if not assembled_context.evidence_blocks:
        return GroundedAnswer(
            question=question,
            answer=(
                "I do not have enough policy evidence to answer this from the "
                "local corpus."
            ),
            citations=[],
            confidence="low",
            abstained=True,
            evidence_blocks=[],
            context_text="",
            raw_model_output=None,
        )

    raw_output = _invoke_answer_model(settings, question, assembled_context.context_text)
    parsed = _parse_answer_json(raw_output)
    return GroundedAnswer(
        question=question,
        answer=str(parsed.get("answer", "")).strip(),
        citations=_normalize_citations(parsed.get("citations")),
        confidence=str(parsed.get("confidence", "low")).strip().lower() or "low",
        abstained=bool(parsed.get("abstained", False)),
        evidence_blocks=assembled_context.evidence_blocks,
        context_text=assembled_context.context_text,
        raw_model_output=raw_output,
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


def _invoke_answer_model(settings: Settings, question: str, context_text: str) -> str:
    try:
        from langchain_openai import ChatOpenAI
    except ImportError as exc:
        raise RuntimeError(
            "Answer generation requires langchain-openai. Run "
            "`python -m pip install -e .` from the project root."
        ) from exc

    model = ChatOpenAI(model=settings.answer_model)
    response = model.invoke(
        [
            {"role": "system", "content": _read_prompt("system.md")},
            {
                "role": "user",
                "content": _build_answer_prompt(question, context_text),
            },
        ]
    )
    return _message_content_to_text(response.content)


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


def _parse_answer_json(raw_output: str) -> dict[str, Any]:
    cleaned_output = _strip_json_fence(raw_output)
    try:
        parsed = json.loads(cleaned_output)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Answer model did not return valid JSON. Raw output:\n"
            f"{raw_output}"
        ) from exc
    if not isinstance(parsed, dict):
        raise RuntimeError("Answer model returned JSON, but not a JSON object.")
    return parsed


def _strip_json_fence(raw_output: str) -> str:
    stripped = raw_output.strip()
    if not stripped.startswith("```"):
        return stripped

    match = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", stripped, flags=re.DOTALL)
    return match.group(1).strip() if match else stripped


def _normalize_citations(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    citations: list[str] = []
    for item in value:
        citation = str(item).strip()
        if re.fullmatch(r"\[\d+\]", citation):
            citations.append(citation)
    return citations
