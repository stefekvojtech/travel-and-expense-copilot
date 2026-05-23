"""FastAPI routes for grounded chat and streaming chat responses."""

from __future__ import annotations

from collections.abc import Iterator

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.agents.answer import answer_policy_question
from app.api.demo_guardrails import check_public_demo_rate_limit
from app.api.schemas import ChatRequest, ChatResponse, HealthResponse
from app.core.config import Settings, get_settings
from app.streaming.chat import stream_grounded_answer_events
from app.streaming.sse import format_sse_event


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Return a minimal liveness response for local runtime checks."""
    return HealthResponse()


@router.post("/api/chat", response_model=ChatResponse)
def chat(request: Request, body: ChatRequest) -> ChatResponse:
    """Generate a grounded answer with citations in one JSON response."""
    settings = get_settings()
    _raise_if_rate_limited(settings, request)
    try:
        result = answer_policy_question(
            settings,
            body.question,
            filters=body.to_retrieval_filters(),
            search_k=None,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=_public_safe_error_message(settings, exc),
        ) from exc
    return ChatResponse.from_grounded_answer(result)


@router.post("/api/chat/stream")
def chat_stream(request: Request, body: ChatRequest) -> StreamingResponse:
    """Stream retrieval progress, answer deltas, and final grounded answer data."""
    settings = get_settings()
    _raise_if_rate_limited(settings, request)
    return StreamingResponse(
        _chat_sse_events(settings, body),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


def _chat_sse_events(settings: Settings, request: ChatRequest) -> Iterator[str]:
    try:
        for event, data in stream_grounded_answer_events(
            settings,
            request.question,
            filters=request.to_retrieval_filters(),
            search_k=None,
        ):
            yield format_sse_event(event, data)
    except Exception as exc:
        yield format_sse_event("status_changed", {"status": "error", "label": "Error"})
        yield format_sse_event(
            "error",
            {"message": _public_safe_error_message(settings, exc)},
        )


def _raise_if_rate_limited(settings: Settings, request: Request) -> None:
    decision = check_public_demo_rate_limit(settings, request)
    if decision.allowed:
        return
    raise HTTPException(
        status_code=429,
        detail=decision.message,
        headers={"Retry-After": str(decision.retry_after_seconds)},
    )


def _public_safe_error_message(settings: Settings, exc: Exception) -> str:
    if not settings.public_demo_mode:
        return str(exc)
    return (
        "The public demo could not complete this request. "
        "Please try again later."
    )
