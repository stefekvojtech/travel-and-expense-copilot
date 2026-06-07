"""Tests for environment-backed settings defaults."""

from __future__ import annotations

from typing import Any

from app.core.config import ROOT_DIR, get_settings


CONFIG_ENV_KEYS = (
    "EMBEDDING_MODEL",
    "VISION_MODEL",
    "ANSWER_MODEL",
    "ANSWER_MAX_TOKENS",
    "QUESTION_MAX_CHARACTERS",
    "RAW_DATA_DIR",
    "PROCESSED_DATA_DIR",
    "VECTOR_COLLECTION_NAME",
    "RETRIEVAL_TOP_K",
    "RETRIEVAL_RERANK_K",
    "RETRIEVAL_CONTEXT_K",
    "RETRIEVAL_CONTEXT_MAX_TOKENS",
    "RETRIEVAL_CONTEXT_MAX_BLOCK_TOKENS",
    "RERANK_MODEL",
    "CHUNK_SIZE",
    "CHUNK_OVERLAP",
    "MAX_CHUNK_TOKENS",
    "PUBLIC_DEMO_MODE",
    "PUBLIC_DEMO_RATE_LIMIT_REQUESTS",
    "PUBLIC_DEMO_RATE_LIMIT_WINDOW_SECONDS",
    "AUTHOR_NAME",
    "AUTHOR_LINKEDIN_URL",
    "AUTHOR_GITHUB_URL",
)


def test_get_settings_has_defaults_without_env_file_values(monkeypatch: Any) -> None:
    """Non-secret settings should not require a local .env file."""
    get_settings.cache_clear()
    for key in CONFIG_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)

    settings = get_settings()

    assert settings.embedding_model == "text-embedding-3-large"
    assert settings.vision_model == "gpt-5.4"
    assert settings.answer_model == "gpt-4.1-mini"
    assert settings.answer_max_tokens == 500
    assert settings.question_max_characters == 1000
    assert settings.raw_data_dir == ROOT_DIR / "data" / "raw"
    assert settings.processed_data_dir == ROOT_DIR / "data" / "processed"
    assert settings.vector_store_dir == ROOT_DIR / "data" / "processed" / "04_vectorstore"
    assert settings.vector_collection_name == "travel_expense_policy_chunks"
    assert settings.retrieval_top_k == 12
    assert settings.retrieval_rerank_k == 8
    assert settings.retrieval_context_k == 4
    assert settings.retrieval_context_max_tokens == 3000
    assert settings.retrieval_context_max_block_tokens == 800
    assert settings.rerank_model == "ms-marco-MiniLM-L-12-v2"
    assert settings.chunk_size == 600
    assert settings.chunk_overlap == 120
    assert settings.max_chunk_tokens == 1200
    assert settings.public_demo_mode is False
    assert settings.public_demo_rate_limit_requests == 10
    assert settings.public_demo_rate_limit_window_seconds == 600
    assert settings.author_name == "Vojtech Stefek"
    assert settings.author_linkedin_url == "https://www.linkedin.com/in/vojtech-stefek/"
    assert settings.author_github_url == "https://github.com/stefekvojtech"

    get_settings.cache_clear()


def test_get_settings_reads_question_max_characters(monkeypatch: Any) -> None:
    """The shared question limit should be configurable through the environment."""
    get_settings.cache_clear()
    monkeypatch.setenv("QUESTION_MAX_CHARACTERS", "750")

    assert get_settings().question_max_characters == 750

    get_settings.cache_clear()
