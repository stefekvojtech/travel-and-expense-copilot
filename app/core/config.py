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


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    return int(value) if value is not None else default


def _get_path(name: str) -> Path:
    value = os.getenv(name)
    if value is None:
        raise KeyError(name)
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


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    processed_data_dir = _get_path("PROCESSED_DATA_DIR")
    return Settings(
        embedding_model=os.environ["EMBEDDING_MODEL"],
        vision_model=os.environ["VISION_MODEL"],
        answer_model=os.getenv("ANSWER_MODEL", "gpt-5.5"),
        raw_data_dir=_get_path("RAW_DATA_DIR"),
        processed_data_dir=processed_data_dir,
        vector_store_dir=processed_data_dir / "04_vectorstore",
        vector_collection_name=os.environ["VECTOR_COLLECTION_NAME"],
        retrieval_top_k=_get_int("RETRIEVAL_TOP_K", 12),
        retrieval_rerank_k=_get_int("RETRIEVAL_RERANK_K", 5),
        retrieval_context_k=_get_int("RETRIEVAL_CONTEXT_K", 4),
        retrieval_context_max_tokens=_get_int("RETRIEVAL_CONTEXT_MAX_TOKENS", 3000),
        retrieval_context_max_block_tokens=_get_int(
            "RETRIEVAL_CONTEXT_MAX_BLOCK_TOKENS",
            800,
        ),
        rerank_model=os.environ["RERANK_MODEL"],
        chunk_size=_get_int("CHUNK_SIZE", 800),
        chunk_overlap=_get_int("CHUNK_OVERLAP", 120),
        max_chunk_tokens=_get_int("MAX_CHUNK_TOKENS", 1200),
    )
