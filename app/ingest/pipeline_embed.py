from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from app.core.config import Settings


@dataclass(frozen=True)
class ChunkRecord:
    chunk_id: str
    doc_id: str
    source_path: str
    doc_type: str
    title: str
    text: str
    source_block_ids: list[str]
    section_path: str | None
    pages: list[int]
    sheets: list[str]
    chunk_strategy: str
    token_count: int
    order: int
    metadata: dict[str, Any]


@dataclass(frozen=True)
class EmbedResult:
    chunk_count: int
    collection_name: str
    vector_store_path: str
    embedded: bool


def embed_all_chunks(settings: Settings, *, dry_run: bool = False) -> EmbedResult:
    """Embed chunk JSONL artifacts into the configured local Chroma collection."""
    chunks = _read_all_chunks(settings.chunks_dir)
    if dry_run:
        return EmbedResult(
            chunk_count=len(chunks),
            collection_name=settings.vector_collection_name,
            vector_store_path=settings.vector_store_dir.as_posix(),
            embedded=False,
        )

    settings.vector_store_dir.mkdir(parents=True, exist_ok=True)
    vector_store = _build_chroma_vector_store(settings)

    if chunks:
        # Chroma stores one embedding document per chunk. UiPath parallel: each
        # queue item keeps its transaction data plus references back to the source.
        vector_store.add_texts(
            texts=[chunk.text for chunk in chunks],
            metadatas=[_chunk_metadata(chunk) for chunk in chunks],
            ids=[chunk.chunk_id for chunk in chunks],
        )

    return EmbedResult(
        chunk_count=len(chunks),
        collection_name=settings.vector_collection_name,
        vector_store_path=settings.vector_store_dir.as_posix(),
        embedded=True,
    )


def _build_chroma_vector_store(settings: Settings):
    try:
        from langchain_chroma import Chroma
        from langchain_openai import OpenAIEmbeddings
    except ImportError as exc:
        raise RuntimeError(
            "Embedding requires langchain-chroma and langchain-openai. "
            "Run `uv sync` after updating pyproject.toml."
        ) from exc

    embeddings = OpenAIEmbeddings(model=settings.embedding_model)
    return Chroma(
        collection_name=settings.vector_collection_name,
        embedding_function=embeddings,
        persist_directory=settings.vector_store_dir.as_posix(),
    )


def _read_all_chunks(chunks_dir: Path) -> list[ChunkRecord]:
    chunks: list[ChunkRecord] = []
    for chunks_path in sorted(chunks_dir.glob("*.jsonl")):
        chunks.extend(_read_chunks(chunks_path))
    return chunks


def _read_chunks(chunks_path: Path) -> list[ChunkRecord]:
    chunks: list[ChunkRecord] = []
    for line in chunks_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            chunks.append(ChunkRecord(**json.loads(line)))
    return chunks


def _chunk_metadata(chunk: ChunkRecord) -> dict[str, str | int | float | bool | None]:
    metadata: dict[str, str | int | float | bool | None] = {
        "chunk_id": chunk.chunk_id,
        "doc_id": chunk.doc_id,
        "source_path": chunk.source_path,
        "doc_type": chunk.doc_type,
        "title": chunk.title,
        "section_path": chunk.section_path,
        "chunk_strategy": chunk.chunk_strategy,
        "token_count": chunk.token_count,
        "order": chunk.order,
        "source_block_ids": json.dumps(chunk.source_block_ids, ensure_ascii=True),
        "pages": json.dumps(chunk.pages, ensure_ascii=True),
        "sheets": json.dumps(chunk.sheets, ensure_ascii=True),
    }
    metadata.update(_flatten_metadata(chunk.metadata))
    return metadata


def _flatten_metadata(
    metadata: dict[str, Any],
    *,
    prefix: str = "metadata",
) -> dict[str, str | int | float | bool | None]:
    flattened: dict[str, str | int | float | bool | None] = {}
    for key, value in metadata.items():
        flattened_key = f"{prefix}_{key}"
        if _is_chroma_scalar(value):
            flattened[flattened_key] = value
        else:
            flattened[flattened_key] = json.dumps(value, ensure_ascii=True)
    return flattened


def _is_chroma_scalar(value: Any) -> bool:
    return value is None or isinstance(value, str | int | float | bool)
