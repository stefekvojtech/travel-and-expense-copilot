"""Load environment-backed settings and resolve project-local paths.

This module centralizes configuration for ingestion, chunking, embedding,
retrieval, answer generation, and local artifact directories. Relative paths
from `.env` are resolved from the repository root so scripts behave
consistently from any working directory.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional during early scaffold stage
    load_dotenv = None


ROOT_DIR = Path(__file__).resolve().parents[2]

if load_dotenv is not None:
    load_dotenv(ROOT_DIR / ".env")

DEFAULT_EMBEDDING_MODEL = "text-embedding-3-large"
DEFAULT_VISION_MODEL = "gpt-5.4"
DEFAULT_ANSWER_MODEL = "gpt-4.1-mini"
DEFAULT_RAW_DATA_DIR = "data/raw"
DEFAULT_PROCESSED_DATA_DIR = "data/processed"
DEFAULT_VECTOR_COLLECTION_NAME = "travel_expense_policy_chunks"
DEFAULT_RETRIEVAL_TOP_K = 12
DEFAULT_RETRIEVAL_RERANK_K = 8
DEFAULT_RETRIEVAL_CONTEXT_K = 4
DEFAULT_RETRIEVAL_CONTEXT_MAX_TOKENS = 3000
DEFAULT_RETRIEVAL_CONTEXT_MAX_BLOCK_TOKENS = 800
DEFAULT_RERANK_MODEL = "ms-marco-MiniLM-L-12-v2"
DEFAULT_CHUNK_SIZE = 600
DEFAULT_CHUNK_OVERLAP = 120
DEFAULT_MAX_CHUNK_TOKENS = 1200
DEFAULT_ANSWER_MAX_TOKENS = 500
DEFAULT_QUESTION_MAX_CHARACTERS = 1000
DEFAULT_PUBLIC_DEMO_MODE = False
DEFAULT_PUBLIC_DEMO_RATE_LIMIT_REQUESTS = 10
DEFAULT_PUBLIC_DEMO_RATE_LIMIT_WINDOW_SECONDS = 600
DEFAULT_AUTHOR_NAME = "Vojtech Stefek"
DEFAULT_AUTHOR_LINKEDIN_URL = "https://www.linkedin.com/in/vojtech-stefek/"
DEFAULT_AUTHOR_GITHUB_URL = "https://github.com/stefekvojtech"


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    return int(value) if value is not None else default


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_str(name: str, default: str = "") -> str:
    return os.getenv(name, default)


def _get_path(name: str, default: str) -> Path:
    value = os.getenv(name, default)
    path = Path(value)
    if path.is_absolute():
        return path
    return ROOT_DIR / path


@dataclass(frozen=True)
class Settings:
    embedding_model: str
    vision_model: str
    answer_model: str
    raw_data_dir: Path
    processed_data_dir: Path
    vector_store_dir: Path
    vector_collection_name: str
    retrieval_top_k: int
    retrieval_rerank_k: int
    retrieval_context_k: int
    retrieval_context_max_tokens: int
    retrieval_context_max_block_tokens: int
    rerank_model: str
    chunk_size: int
    chunk_overlap: int
    max_chunk_tokens: int
    answer_max_tokens: int = DEFAULT_ANSWER_MAX_TOKENS
    question_max_characters: int = DEFAULT_QUESTION_MAX_CHARACTERS
    public_demo_mode: bool = DEFAULT_PUBLIC_DEMO_MODE
    public_demo_rate_limit_requests: int = DEFAULT_PUBLIC_DEMO_RATE_LIMIT_REQUESTS
    public_demo_rate_limit_window_seconds: int = (
        DEFAULT_PUBLIC_DEMO_RATE_LIMIT_WINDOW_SECONDS
    )
    author_name: str = ""
    author_linkedin_url: str = ""
    author_github_url: str = ""


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    processed_data_dir = _get_path("PROCESSED_DATA_DIR", DEFAULT_PROCESSED_DATA_DIR)
    return Settings(
        embedding_model=_get_str("EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL),
        vision_model=_get_str("VISION_MODEL", DEFAULT_VISION_MODEL),
        answer_model=_get_str("ANSWER_MODEL", DEFAULT_ANSWER_MODEL),
        raw_data_dir=_get_path("RAW_DATA_DIR", DEFAULT_RAW_DATA_DIR),
        processed_data_dir=processed_data_dir,
        vector_store_dir=processed_data_dir / "04_vectorstore",
        vector_collection_name=_get_str(
            "VECTOR_COLLECTION_NAME",
            DEFAULT_VECTOR_COLLECTION_NAME,
        ),
        retrieval_top_k=_get_int("RETRIEVAL_TOP_K", DEFAULT_RETRIEVAL_TOP_K),
        retrieval_rerank_k=_get_int("RETRIEVAL_RERANK_K", DEFAULT_RETRIEVAL_RERANK_K),
        retrieval_context_k=_get_int("RETRIEVAL_CONTEXT_K", DEFAULT_RETRIEVAL_CONTEXT_K),
        retrieval_context_max_tokens=_get_int(
            "RETRIEVAL_CONTEXT_MAX_TOKENS",
            DEFAULT_RETRIEVAL_CONTEXT_MAX_TOKENS,
        ),
        retrieval_context_max_block_tokens=_get_int(
            "RETRIEVAL_CONTEXT_MAX_BLOCK_TOKENS",
            DEFAULT_RETRIEVAL_CONTEXT_MAX_BLOCK_TOKENS,
        ),
        rerank_model=_get_str("RERANK_MODEL", DEFAULT_RERANK_MODEL),
        chunk_size=_get_int("CHUNK_SIZE", DEFAULT_CHUNK_SIZE),
        chunk_overlap=_get_int("CHUNK_OVERLAP", DEFAULT_CHUNK_OVERLAP),
        max_chunk_tokens=_get_int("MAX_CHUNK_TOKENS", DEFAULT_MAX_CHUNK_TOKENS),
        answer_max_tokens=_get_int("ANSWER_MAX_TOKENS", DEFAULT_ANSWER_MAX_TOKENS),
        question_max_characters=_get_int(
            "QUESTION_MAX_CHARACTERS",
            DEFAULT_QUESTION_MAX_CHARACTERS,
        ),
        public_demo_mode=_get_bool("PUBLIC_DEMO_MODE", DEFAULT_PUBLIC_DEMO_MODE),
        public_demo_rate_limit_requests=_get_int(
            "PUBLIC_DEMO_RATE_LIMIT_REQUESTS",
            DEFAULT_PUBLIC_DEMO_RATE_LIMIT_REQUESTS,
        ),
        public_demo_rate_limit_window_seconds=_get_int(
            "PUBLIC_DEMO_RATE_LIMIT_WINDOW_SECONDS",
            DEFAULT_PUBLIC_DEMO_RATE_LIMIT_WINDOW_SECONDS,
        ),
        author_name=_get_str("AUTHOR_NAME", DEFAULT_AUTHOR_NAME),
        author_linkedin_url=_get_str(
            "AUTHOR_LINKEDIN_URL",
            DEFAULT_AUTHOR_LINKEDIN_URL,
        ),
        author_github_url=_get_str("AUTHOR_GITHUB_URL", DEFAULT_AUTHOR_GITHUB_URL),
    )
