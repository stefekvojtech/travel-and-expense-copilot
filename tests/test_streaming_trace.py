"""Unit tests for streaming progress trace events."""

from __future__ import annotations

import sys
from types import SimpleNamespace
from typing import Any

import app.streaming.chat as streaming_chat
from app.retrieval.step01_search_chunks import RetrievedChunk
from app.retrieval.step02_rerank_chunks import RerankedChunk


def test_streaming_chat_emits_collectible_trace_events(monkeypatch: Any) -> None:
    """The streaming path should expose detailed steps separately from status."""
    monkeypatch.setattr(
        streaming_chat,
        "embed_query",
        lambda *_args, **_kwargs: [0.1, 0.2, 0.3],
    )
    monkeypatch.setattr(
        streaming_chat,
        "search_chunks_by_query_embedding",
        lambda *_args, **_kwargs: [_retrieved_chunk()],
    )
    monkeypatch.setattr(
        streaming_chat,
        "rerank_chunks",
        lambda *_args, **_kwargs: [_reranked_chunk()],
    )
    monkeypatch.setitem(
        sys.modules,
        "langchain_openai",
        SimpleNamespace(ChatOpenAI=_FakeChatOpenAI),
    )

    events = list(
        streaming_chat.stream_grounded_answer_events(
            _settings(),
            "Can I take a taxi from Prague airport after 21:00?",
        )
    )

    event_names = [event for event, _data in events]
    assert "status_changed" in event_names
    assert "trace_started" in event_names
    assert "trace_complete" in event_names

    started_labels = [
        data["label"]
        for event, data in events
        if event == "trace_step_started"
    ]
    assert started_labels == [
        "Embedding query...",
        "Searching vector index...",
        "Reranking retrieved chunks...",
        "Assembling cited context...",
        "Streaming grounded answer...",
    ]

    completed_steps = [
        data
        for event, data in events
        if event == "trace_step_completed"
    ]
    assert [step["step"] for step in completed_steps] == [
        "embedding_query",
        "search_vector_index",
        "rerank_retrieved_chunks",
        "assemble_cited_context",
        "stream_grounded_answer",
    ]
    assert all(step["duration_ms"] >= 0 for step in completed_steps)
    assert completed_steps[0]["metadata"]["dimensions"] == 3

    answer_complete = next(data for event, data in events if event == "answer_complete")
    assert answer_complete["answer"] == "Yes. [1]"
    assert answer_complete["processing_ms"] >= 0


class _FakeChatOpenAI:
    def __init__(self, *_args: Any, **_kwargs: Any) -> None:
        pass

    def stream(self, _messages: Any) -> list[SimpleNamespace]:
        return [
            SimpleNamespace(content='{"answer":"Yes. '),
            SimpleNamespace(
                content='[1]","citations":["[1]"],'
                '"confidence":"high","abstained":false}'
            ),
        ]


def _settings() -> SimpleNamespace:
    return SimpleNamespace(
        embedding_model="text-embedding-3-small",
        retrieval_top_k=12,
        rerank_model="ms-marco-MiniLM-L-12-v2",
        retrieval_rerank_k=6,
        retrieval_context_k=4,
        retrieval_context_max_tokens=1800,
        retrieval_context_max_block_tokens=700,
        answer_model="gpt-5.5",
    )


def _retrieved_chunk() -> RetrievedChunk:
    return RetrievedChunk(
        text="Prague taxi after-hours threshold is 21:00.",
        metadata={
            "chunk_id": "chunk-1",
            "source_path": "data/raw/per_diem_caps.xlsx",
            "doc_type": "xlsx",
            "title": "Per Diem Caps",
            "section_path": "TaxiRules",
        },
        cosine_distance=0.1,
    )


def _reranked_chunk() -> RerankedChunk:
    return RerankedChunk(
        retrieved_chunk=_retrieved_chunk(),
        rerank_score=0.9,
    )
