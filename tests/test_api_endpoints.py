"""Endpoint tests for FastAPI routes exposed from app.api."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from fastapi.testclient import TestClient

import app.api.chat as chat_routes
import app.api.ui as ui_routes
from app.agents.answer import GroundedAnswer
from app.api.demo_guardrails import reset_public_demo_rate_limits
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
    captured_kwargs: dict[str, Any] = {}
    monkeypatch.setattr(chat_routes, "get_settings", _demo_settings)
    monkeypatch.setattr(
        chat_routes,
        "answer_policy_question",
        lambda *_args, **kwargs: _capture_grounded_answer(captured_kwargs, kwargs),
    )
    client = TestClient(app)

    response = client.post(
        "/api/chat",
        json={
            "question": "Can I take a taxi from Prague airport after 21:00?",
            "search_k": 50,
        },
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
    assert captured_kwargs["search_k"] is None


def test_streaming_chat_endpoint_returns_sse_events(monkeypatch: Any) -> None:
    """POST /api/chat/stream should expose streaming events as SSE text."""
    captured_kwargs: dict[str, Any] = {}
    monkeypatch.setattr(chat_routes, "get_settings", _demo_settings)
    monkeypatch.setattr(
        chat_routes,
        "stream_grounded_answer_events",
        lambda *_args, **kwargs: _fake_stream_grounded_answer_events(
            captured_kwargs,
            kwargs,
        ),
    )
    client = TestClient(app)

    response = client.post(
        "/api/chat/stream",
        json={
            "question": "Can I take a taxi from Prague airport after 21:00?",
            "search_k": 50,
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "event: retrieval_started" in response.text
    assert "event: answer_delta" in response.text
    assert '"delta": "Yes. [1]"' in response.text
    assert captured_kwargs["search_k"] is None


def test_chat_endpoint_rejects_questions_over_public_limit() -> None:
    """POST /api/chat should reject questions longer than the UI limit."""
    client = TestClient(app)

    response = client.post("/api/chat", json={"question": "x" * 1001})

    assert response.status_code == 422


def test_public_demo_mode_rate_limits_by_client_ip(monkeypatch: Any) -> None:
    """Demo mode should cap callers at ten chat requests per ten minutes."""
    reset_public_demo_rate_limits()
    monkeypatch.setattr(chat_routes, "get_settings", _public_demo_settings)
    monkeypatch.setattr(
        chat_routes,
        "answer_policy_question",
        lambda *_args, **_kwargs: _grounded_answer(),
    )
    client = TestClient(app)

    for _ in range(10):
        response = client.post("/api/chat", json={"question": "Can I claim a taxi?"})
        assert response.status_code == 200

    response = client.post("/api/chat", json={"question": "Can I claim a taxi?"})

    assert response.status_code == 429
    assert response.json()["detail"].startswith(
        "You have reached the public demo limit of 10 requests per 10 minutes."
    )
    assert "Retry-After" in response.headers
    reset_public_demo_rate_limits()


def test_ui_config_endpoint_returns_author_links(monkeypatch: Any) -> None:
    """GET /api/ui/config should expose non-sensitive author metadata."""
    monkeypatch.setattr(
        ui_routes,
        "get_settings",
        lambda: type(
            "Settings",
            (),
            {
                "author_name": "Vojtech Stefek",
                "author_linkedin_url": "https://www.linkedin.com/in/vojtech-stefek/",
                "author_github_url": "https://github.com/stefekvojtech",
            },
        )(),
    )
    client = TestClient(app)

    response = client.get("/api/ui/config")

    assert response.status_code == 200
    assert response.json() == {
        "author_name": "Vojtech Stefek",
        "author_linkedin_url": "https://www.linkedin.com/in/vojtech-stefek/",
        "author_github_url": "https://github.com/stefekvojtech",
    }


def _fake_stream_grounded_answer_events(
    captured_kwargs: dict[str, Any],
    kwargs: dict[str, Any],
) -> Iterator[tuple[str, dict[str, Any]]]:
    captured_kwargs.update(kwargs)
    yield "retrieval_started", {"question": "Can I take a taxi from Prague airport after 21:00?"}
    yield "answer_delta", {"delta": "Yes. [1]"}


def _capture_grounded_answer(
    captured_kwargs: dict[str, Any],
    kwargs: dict[str, Any],
) -> GroundedAnswer:
    captured_kwargs.update(kwargs)
    return _grounded_answer()


def _demo_settings() -> Any:
    return type(
        "Settings",
        (),
        {
            "public_demo_mode": False,
            "public_demo_rate_limit_requests": 10,
            "public_demo_rate_limit_window_seconds": 600,
        },
    )()


def _public_demo_settings() -> Any:
    return type(
        "Settings",
        (),
        {
            "public_demo_mode": True,
            "public_demo_rate_limit_requests": 10,
            "public_demo_rate_limit_window_seconds": 600,
        },
    )()


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
        row_number=42,
        cosine_distance=0.1,
        approximate_cosine_similarity=0.9,
        rerank_score=0.8,
        text="Prague taxi after-hours threshold is 21:00.",
    )
