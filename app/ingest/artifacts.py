from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BlockArtifact:
    """Canonical block JSONL row produced by raw ingestion."""

    doc_id: str
    block_id: str
    source_path: str
    doc_type: str
    title: str
    block_type: str
    text: str
    section_path: str | None
    page: int | None
    sheet: str | None
    order: int
    metadata: dict[str, Any]


@dataclass(frozen=True)
class ChunkArtifact:
    """Canonical chunk JSONL row consumed by embedding and retrieval."""

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
