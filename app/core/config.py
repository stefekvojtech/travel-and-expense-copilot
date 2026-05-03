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


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    return int(value) if value is not None else default


def _get_float(name: str, default: float) -> float:
    value = os.getenv(name)
    return float(value) if value is not None else default


@dataclass(frozen=True)
class Settings:
    app_name: str
    environment: str
    debug: bool
    model_provider: str
    chat_model: str
    embedding_model: str
    vision_model: str
    temperature: float
    raw_data_dir: Path
    processed_data_dir: Path
    markdown_dir: Path
    chunks_dir: Path
    vector_store_dir: Path
    retrieval_top_k: int
    retrieval_rerank_k: int
    retrieval_context_k: int
    chunk_size: int
    chunk_overlap: int
    max_chunk_tokens: int
    enable_pii_redaction: bool
    enable_html_sanitization: bool


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        app_name=os.environ["APP_NAME"],
        environment=os.environ["APP_ENV"],
        debug=_get_bool("DEBUG", False),
        model_provider=os.environ["MODEL_PROVIDER"],
        chat_model=os.environ["CHAT_MODEL"],
        embedding_model=os.environ["EMBEDDING_MODEL"],
        vision_model=os.environ["VISION_MODEL"],
        temperature=_get_float("MODEL_TEMPERATURE", 0.0),
        raw_data_dir=Path(os.environ["RAW_DATA_DIR"]),
        processed_data_dir=Path(os.environ["PROCESSED_DATA_DIR"]),
        markdown_dir=Path(os.environ["MARKDOWN_DIR"]),
        chunks_dir=Path(os.environ["CHUNKS_DIR"]),
        vector_store_dir=Path(os.environ["VECTOR_STORE_DIR"]),
        retrieval_top_k=_get_int("RETRIEVAL_TOP_K", 12),
        retrieval_rerank_k=_get_int("RETRIEVAL_RERANK_K", 5),
        retrieval_context_k=_get_int("RETRIEVAL_CONTEXT_K", 4),
        chunk_size=_get_int("CHUNK_SIZE", 800),
        chunk_overlap=_get_int("CHUNK_OVERLAP", 120),
        max_chunk_tokens=_get_int("MAX_CHUNK_TOKENS", 1200),
        enable_pii_redaction=_get_bool("ENABLE_PII_REDACTION", True),
        enable_html_sanitization=_get_bool("ENABLE_HTML_SANITIZATION", True),
    )
