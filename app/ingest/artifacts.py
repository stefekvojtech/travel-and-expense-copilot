"""Shared artifact schemas passed between ingestion, chunking, and retrieval.

Loaded-document artifacts preserve source loader output for inspection. Block
artifacts preserve source-level lineage from normalization. Chunk artifacts are
embedding-ready records derived from those blocks with a small
citation-oriented metadata set.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PipelineWarning:
    """Warning row shown in the generated Markdown report."""

    source_path: str
    warning_type: str
    message: str
    observed_at: str


@dataclass(frozen=True)
class LoadedDocumentArtifact:
    """JSONL row for the first loaded-document inspection stage."""

    doc_id: str
    source_path: str
    doc_type: str
    title: str
    loader_name: str
    document_index: int
    text: str
    metadata: dict[str, Any]


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
    section_path: str | None
    page: int | None
    sheet: str | None
    chunk_strategy: str
    token_count: int
    order: int
    metadata: dict[str, Any]


def chunk_artifact_from_dict(row: dict[str, Any]) -> ChunkArtifact:
    """Build a chunk artifact from current rows or older generated rows."""
    normalized = dict(row)
    if "page" not in normalized:
        normalized["page"] = _first_value(normalized.pop("pages", []))
    if "sheet" not in normalized:
        normalized["sheet"] = _first_value(normalized.pop("sheets", []))
    normalized.pop("source_block_ids", None)
    return ChunkArtifact(**normalized)


def _first_value(value: Any) -> Any:
    if isinstance(value, list):
        return value[0] if value else None
    if isinstance(value, str):
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError:
            return value or None
        if isinstance(decoded, list):
            return decoded[0] if decoded else None
        return decoded
    return value
