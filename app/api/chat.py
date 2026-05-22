"""FastAPI routes for grounded chat and streaming chat responses."""

from __future__ import annotations

from collections.abc import Iterator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.agents.answer import answer_policy_question
from app.api.schemas import ChatRequest, ChatResponse, HealthResponse
from app.core.config import get_settings
from app.streaming.chat import stream_grounded_answer_events
from app.streaming.sse import format_sse_event


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Return a minimal liveness response for local runtime checks."""
    return HealthResponse()


@router.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Generate a grounded answer with citations in one JSON response."""
    try:
        result = answer_policy_question(
            get_settings(),
            request.question,
            filters=request.to_retrieval_filters(),
            search_k=request.search_k,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return ChatResponse.from_grounded_answer(result)


@router.post("/api/chat/stream")
def chat_stream(request: ChatRequest) -> StreamingResponse:
    """Stream retrieval progress, answer deltas, and final grounded answer data."""
    return StreamingResponse(
        _chat_sse_events(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


def _chat_sse_events(request: ChatRequest) -> Iterator[str]:
    try:
        for event, data in stream_grounded_answer_events(
            get_settings(),
            request.question,
            filters=request.to_retrieval_filters(),
            search_k=request.search_k,
        ):
            yield format_sse_event(event, data)
    except Exception as exc:
        yield format_sse_event("status_changed", {"status": "error", "label": "Error"})
        yield format_sse_event("error", {"message": str(exc)})
