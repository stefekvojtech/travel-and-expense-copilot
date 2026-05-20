"""Loader-level data models returned before common ingestion metadata is added."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SourceBlock:
    # A loader-level content unit before the pipeline adds common document fields.
    # UiPath parallel: one extracted transaction row before Orchestrator stamps IDs.
    text: str
    block_type: str
    section_path: str | None = None
    page: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class NormalizedSource:
    # Each loader returns both outputs at once:
    # Markdown for humans/chunk structure, blocks for source lineage metadata.
    markdown_text: str
    blocks: list[SourceBlock]
    extraction_method: str
    extraction_warning: str | None = None
