"""Embed stage 03 chunk artifacts into the local Chroma vector store.

This module reads `03_chunks` JSONL files, builds OpenAI embeddings for the
chunk text, stores flattened metadata in Chroma, and promotes replacement
collections only after count verification. Normal execution makes paid
embedding calls through the configured provider.
"""

from __future__ import annotations

import json
import re
import shutil
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.core.config import Settings
from app.ingest.artifact_paths import chunks_dir
from app.ingest.artifacts import ChunkArtifact
from app.retrieval.chroma_config import CHROMA_COLLECTION_METADATA


@dataclass(frozen=True)
class EmbedResult:
    chunk_count: int
    collection_name: str
    vector_store_path: str


def embed_all_chunks(settings: Settings) -> EmbedResult:
    """Embed chunk JSONL artifacts into the configured local Chroma collection."""
    chunks = _read_all_chunks(chunks_dir(settings))

    settings.vector_store_dir.mkdir(parents=True, exist_ok=True)
    temp_collection_name = _temporary_collection_name(settings.vector_collection_name)
    try:
        vector_store = _build_chroma_vector_store(
            settings,
            collection_name=temp_collection_name,
        )

        if chunks:
            # Build replacement vectors in a temporary collection first. The
            # existing production collection remains usable if embedding fails.
            vector_store.add_texts(
                texts=[chunk.text for chunk in chunks],
                metadatas=[_chunk_metadata(chunk) for chunk in chunks],
                ids=[chunk.chunk_id for chunk in chunks],
            )
        _verify_collection_count(settings, temp_collection_name, expected_count=len(chunks))
        _promote_temporary_collection(
            settings,
            temp_collection_name=temp_collection_name,
        )
    except Exception:
        _delete_collection_if_exists(settings, temp_collection_name)
        raise

    _remove_orphaned_chroma_vector_dirs(settings)

    return EmbedResult(
        chunk_count=len(chunks),
        collection_name=settings.vector_collection_name,
        vector_store_path=settings.vector_store_dir.as_posix(),
    )


def _build_chroma_vector_store(settings: Settings, *, collection_name: str):
    try:
        from langchain_chroma import Chroma
        from langchain_openai import OpenAIEmbeddings
    except ImportError as exc:
        raise RuntimeError(
            "Embedding requires langchain-chroma and langchain-openai. "
            "Run `python -m pip install -e .` from the project root."
        ) from exc

    embeddings = OpenAIEmbeddings(model=settings.embedding_model)
    return Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=settings.vector_store_dir.as_posix(),
        collection_metadata=CHROMA_COLLECTION_METADATA,
    )


def _temporary_collection_name(collection_name: str) -> str:
    return f"{collection_name}__tmp__{uuid4().hex}"


def _promote_temporary_collection(
    settings: Settings,
    *,
    temp_collection_name: str,
) -> None:
    client = _chroma_client(settings)
    backup_collection_name = _temporary_collection_name(
        f"{settings.vector_collection_name}__backup"
    )
    backup_created = False
    if _collection_exists(settings, settings.vector_collection_name):
        current_collection = client.get_collection(settings.vector_collection_name)
        current_collection.modify(name=backup_collection_name)
        backup_created = True

    temp_collection = client.get_collection(temp_collection_name)
    try:
        temp_collection.modify(name=settings.vector_collection_name)
    except Exception:
        if backup_created:
            backup_collection = client.get_collection(backup_collection_name)
            backup_collection.modify(name=settings.vector_collection_name)
        raise

    if backup_created:
        _delete_collection_if_exists(settings, backup_collection_name)


def _verify_collection_count(
    settings: Settings,
    collection_name: str,
    *,
    expected_count: int,
) -> None:
    collection = _chroma_client(settings).get_collection(collection_name)
    actual_count = collection.count()
    if actual_count != expected_count:
        raise RuntimeError(
            "Temporary Chroma collection count mismatch: "
            f"expected {expected_count}, got {actual_count}."
        )


def _delete_collection_if_exists(settings: Settings, collection_name: str) -> None:
    client = _chroma_client(settings)
    try:
        client.delete_collection(collection_name)
    except Exception as exc:
        message = str(exc).lower()
        if "does not exist" not in message and "not found" not in message:
            raise


def _collection_exists(settings: Settings, collection_name: str) -> bool:
    try:
        _chroma_client(settings).get_collection(collection_name)
    except Exception as exc:
        message = str(exc).lower()
        if "does not exist" in message or "not found" in message:
            return False
        raise
    return True


def _chroma_client(settings: Settings):
    try:
        import chromadb
    except ImportError as exc:
        raise RuntimeError(
            "Embedding requires chromadb. Run `python -m pip install -e .` "
            "from the project root."
        ) from exc

    return chromadb.PersistentClient(path=settings.vector_store_dir.as_posix())


def _remove_orphaned_chroma_vector_dirs(settings: Settings) -> None:
    sqlite_path = settings.vector_store_dir / "chroma.sqlite3"
    if not sqlite_path.exists():
        return

    active_vector_segment_ids = _read_active_vector_segment_ids(sqlite_path)
    uuid_dir_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    )
    vector_store_root = settings.vector_store_dir.resolve()
    for path in settings.vector_store_dir.iterdir():
        if not path.is_dir() or not uuid_dir_pattern.match(path.name):
            continue
        if path.name in active_vector_segment_ids:
            continue
        if not path.resolve().is_relative_to(vector_store_root):
            continue
        shutil.rmtree(path)


def _read_active_vector_segment_ids(sqlite_path: Path) -> set[str]:
    connection = sqlite3.connect(sqlite_path)
    try:
        rows = connection.execute(
            "SELECT id FROM segments WHERE scope = 'VECTOR'"
        ).fetchall()
    finally:
        connection.close()
    return {str(row[0]) for row in rows}


def _read_all_chunks(chunks_dir: Path) -> list[ChunkArtifact]:
    chunks: list[ChunkArtifact] = []
    for chunks_path in sorted(chunks_dir.glob("*.jsonl")):
        chunks.extend(_read_chunks(chunks_path))
    return chunks


def _read_chunks(chunks_path: Path) -> list[ChunkArtifact]:
    chunks: list[ChunkArtifact] = []
    for line in chunks_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            chunks.append(ChunkArtifact(**json.loads(line)))
    return chunks


def _chunk_metadata(chunk: ChunkArtifact) -> dict[str, str | int | float | bool | None]:
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
