"""Pydantic request and response schemas for the copilot API."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.agents.answer import GroundedAnswer
from app.retrieval.step01_search_chunks import RetrievalFilters
from app.retrieval.step03_assemble_context import EvidenceBlock


Confidence = Literal["high", "medium", "low"]


class HealthResponse(BaseModel):
    """Minimal backend liveness response."""

    status: Literal["ok"] = "ok"
    app: str = "travel-and-expense-copilot"


class UiConfigResponse(BaseModel):
    """Non-sensitive UI configuration exposed to the browser."""

    author_name: str
    author_linkedin_url: str
    author_github_url: str


class RetrievalFiltersRequest(BaseModel):
    """Exact metadata filters for the first vector-retrieval pass."""

    doc_type: str | None = None
    source_path: str | None = None
    section_path: str | None = None

    def to_retrieval_filters(self) -> RetrievalFilters:
        """Convert API filter values into the retrieval module's dataclass."""
        return RetrievalFilters(
            doc_type=self.doc_type,
            source_path=self.source_path,
            section_path=self.section_path,
        )


class ChatRequest(BaseModel):
    """Question payload for grounded answer generation."""

    question: str = Field(min_length=1)
    search_k: int | None = Field(
        default=None,
        ge=1,
        le=50,
        description="Optional number of vector candidates to retrieve.",
    )
    filters: RetrievalFiltersRequest | None = None

    def to_retrieval_filters(self) -> RetrievalFilters | None:
        """Return retrieval filters when the request includes any filter values."""
        if self.filters is None:
            return None
        filters = self.filters.to_retrieval_filters()
        if not any([filters.doc_type, filters.source_path, filters.section_path]):
            return None
        return filters


class EvidenceBlockResponse(BaseModel):
    """Citation-ready evidence block returned to API and UI clients."""

    model_config = ConfigDict(from_attributes=True)

    citation_id: str
    chunk_id: str | None
    source_path: str | None
    doc_type: str | None
    title: str | None
    section_path: str | None
    page_label: str | None
    sheet_label: str | None
    row_number: int | None
    cosine_distance: float
    approximate_cosine_similarity: float
    rerank_score: float | None
    text: str

    @classmethod
    def from_evidence_block(cls, block: EvidenceBlock) -> "EvidenceBlockResponse":
        """Build an API-safe evidence payload from the retrieval dataclass."""
        return cls.model_validate(block)


class ChatDebugResponse(BaseModel):
    """Debug details useful for the future UI inspection panel."""

    context_text: str
    raw_model_output: str | None = None
    validation_warnings: list[str] = Field(default_factory=list)


class ChatResponse(BaseModel):
    """Grounded answer response returned by the chat endpoint."""

    question: str
    answer: str
    citations: list[str]
    confidence: Confidence
    abstained: bool
    evidence_blocks: list[EvidenceBlockResponse]
    judge_result: dict[str, Any] | None = None
    debug: ChatDebugResponse

    @classmethod
    def from_grounded_answer(cls, answer: GroundedAnswer) -> "ChatResponse":
        """Build the HTTP response model from the core answer dataclass."""
        return cls(
            question=answer.question,
            answer=answer.answer,
            citations=answer.citations,
            confidence=answer.confidence,  # type: ignore[arg-type]
            abstained=answer.abstained,
            evidence_blocks=[
                EvidenceBlockResponse.from_evidence_block(block)
                for block in answer.evidence_blocks
            ],
            judge_result=None,
            debug=ChatDebugResponse(
                context_text=answer.context_text,
                raw_model_output=answer.raw_model_output,
                validation_warnings=answer.validation_warnings or [],
            ),
        )
