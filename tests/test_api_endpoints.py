"""Endpoint tests for FastAPI routes exposed from app.api."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from fastapi.testclient import TestClient

import app.api.chat as chat_routes
from app.agents.answer import GroundedAnswer
from app.main import app
from app.retrieval.step03_assemble_context import EvidenceBlock


def test_health_endpoint_returns_liveness_payload() -> None:
    """GET /health should return the local liveness payload."""
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "app": "travel-and-expense-copilot",
    }


def test_chat_endpoint_returns_grounded_answer_without_model_call(monkeypatch: Any) -> None:
    """POST /api/chat should serialize the grounded answer returned by the agent."""
    monkeypatch.setattr(chat_routes, "get_settings", lambda: object())
    monkeypatch.setattr(
        chat_routes,
        "answer_policy_question",
        lambda *_args, **_kwargs: _grounded_answer(),
    )
    client = TestClient(app)

    response = client.post(
        "/api/chat",
        json={"question": "Can I take a taxi from Prague airport after 21:00?"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["question"] == "Can I take a taxi from Prague airport after 21:00?"
    assert payload["answer"] == "Yes, if the after-hours threshold applies. [1]"
    assert payload["citations"] == ["[1]"]
    assert payload["confidence"] == "high"
    assert payload["abstained"] is False
    assert payload["evidence_blocks"][0]["citation_id"] == "[1]"
    assert payload["debug"]["context_text"] == "[1] Test context"


def test_streaming_chat_endpoint_returns_sse_events(monkeypatch: Any) -> None:
    """POST /api/chat/stream should expose streaming events as SSE text."""
    monkeypatch.setattr(chat_routes, "get_settings", lambda: object())
    monkeypatch.setattr(
        chat_routes,
        "stream_grounded_answer_events",
        _fake_stream_grounded_answer_events,
    )
    client = TestClient(app)

    response = client.post(
        "/api/chat/stream",
        json={"question": "Can I take a taxi from Prague airport after 21:00?"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "event: retrieval_started" in response.text
    assert "event: answer_delta" in response.text
    assert '"delta": "Yes. [1]"' in response.text


def _fake_stream_grounded_answer_events(
    *_args: Any,
    **_kwargs: Any,
) -> Iterator[tuple[str, dict[str, Any]]]:
    yield "retrieval_started", {"question": "Can I take a taxi from Prague airport after 21:00?"}
    yield "answer_delta", {"delta": "Yes. [1]"}


def _grounded_answer() -> GroundedAnswer:
    return GroundedAnswer(
        question="Can I take a taxi from Prague airport after 21:00?",
        answer="Yes, if the after-hours threshold applies. [1]",
        citations=["[1]"],
        confidence="high",
        abstained=False,
        evidence_blocks=[_evidence_block()],
        context_text="[1] Test context",
        raw_model_output='{"answer":"Yes, if the after-hours threshold applies. [1]"}',
        validation_warnings=[],
    )


def _evidence_block() -> EvidenceBlock:
    return EvidenceBlock(
        citation_id="[1]",
        chunk_id="chunk-1",
        source_path="data/raw/per_diem_caps.xlsx",
        doc_type="xlsx",
        title="Per Diem Caps",
        section_path="Taxi",
        page_label=None,
        sheet_label="Taxi",
        row_number=42,
        cosine_distance=0.1,
        approximate_cosine_similarity=0.9,
        rerank_score=0.8,
        text="Prague taxi after-hours threshold is 21:00.",
    )
