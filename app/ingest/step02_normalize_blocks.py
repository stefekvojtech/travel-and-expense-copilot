"""Normalize loaded/raw sources into block artifacts and block previews.

This stage writes `02_normalized_blocks` JSONL files and
`02_normalized_blocks_preview` Markdown files. It reuses the production loaders
for PDF, HTML, XLSX, TXT, and images. Image normalization reuses the stage 01
loaded image text when available so a normal pipeline run does not call paid
vision twice.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from app.core.config import Settings
from app.ingest.artifact_io import read_jsonl, write_jsonl
from app.ingest.artifact_paths import (
    loaded_documents_dir,
    normalized_block_previews_dir,
    normalized_blocks_dir,
    project_relative_path,
    reset_artifact_dir,
    write_text_if_changed,
)
from app.ingest.artifacts import BlockArtifact, LoadedDocumentArtifact, PipelineWarning
from app.ingest.loaders import IMAGE_SUFFIXES, normalize_by_file_type
from app.ingest.loaders.models import SourceBlock
from app.ingest.source_files import (
    build_doc_id,
    discover_raw_files,
    doc_type_from_source_path,
    split_supported_files,
    title_from_source_path,
)


@dataclass(frozen=True)
class NormalizedBlockDocument:
    doc_id: str
    source_path: str
    output_blocks_path: str
    output_blocks_preview_path: str
    doc_type: str
    title: str
    block_count: int


@dataclass(frozen=True)
class NormalizeBlocksResult:
    documents: list[NormalizedBlockDocument]
    warnings: list[PipelineWarning]
    block_count: int


def normalize_all_blocks(settings: Settings) -> NormalizeBlocksResult:
    """Normalize all supported raw files and rebuild the stage 02 folders."""
    blocks_dir = normalized_blocks_dir(settings)
    preview_dir = normalized_block_previews_dir(settings)
    reset_artifact_dir(blocks_dir, pattern="*.jsonl")
    reset_artifact_dir(preview_dir, pattern="*.md")

    source_paths, _ = split_supported_files(discover_raw_files(settings.raw_data_dir))
    documents: list[NormalizedBlockDocument] = []
    warnings: list[PipelineWarning] = []

    for source_path in source_paths:
        try:
            blocks = normalize_source_to_blocks(source_path, settings=settings)
        except Exception as exc:
            warnings.append(
                PipelineWarning(
                    source_path=project_relative_path(source_path),
                    warning_type="normalize_failed",
                    message=str(exc),
                    observed_at=_now_iso(),
                )
            )
            continue

        if not blocks:
            continue

        doc_id = blocks[0].doc_id
        output_path = blocks_dir / f"{doc_id}.jsonl"
        preview_path = preview_dir / f"{doc_id}.md"
        write_jsonl(output_path, blocks)
        write_text_if_changed(preview_path, normalized_blocks_preview_markdown(blocks))
        documents.append(
            NormalizedBlockDocument(
                doc_id=doc_id,
                source_path=blocks[0].source_path,
                output_blocks_path=project_relative_path(output_path),
                output_blocks_preview_path=project_relative_path(preview_path),
                doc_type=blocks[0].doc_type,
                title=blocks[0].title,
                block_count=len(blocks),
            )
        )

    return NormalizeBlocksResult(
        documents=documents,
        warnings=warnings,
        block_count=sum(document.block_count for document in documents),
    )


def normalize_source_to_blocks(source_path: Path, *, settings: Settings) -> list[BlockArtifact]:
    """Normalize one supported source file into canonical block artifacts."""
    if source_path.suffix.lower() in IMAGE_SUFFIXES:
        loaded_image = _read_loaded_document_for_source(source_path, settings=settings)
        if loaded_image is not None:
            return _blocks_from_loaded_image(loaded_image)

    normalized_source = normalize_by_file_type(source_path)
    return build_block_artifacts(
        normalized_source.blocks,
        doc_id=build_doc_id(source_path),
        source_path=source_path,
        doc_type=doc_type_from_source_path(source_path),
        title=title_from_source_path(source_path),
    )


def build_block_artifacts(
    source_blocks: Iterable[SourceBlock],
    *,
    doc_id: str,
    source_path: Path,
    doc_type: str,
    title: str,
) -> list[BlockArtifact]:
    artifacts: list[BlockArtifact] = []
    for index, source_block in enumerate(source_blocks, start=1):
        artifacts.append(
            BlockArtifact(
                doc_id=doc_id,
                block_id=f"{doc_id}:{index:05d}",
                source_path=project_relative_path(source_path),
                doc_type=doc_type,
                title=title,
                block_type=source_block.block_type,
                text=source_block.text,
                section_path=source_block.section_path,
                page=source_block.page,
                sheet=source_block.sheet,
                order=index,
                metadata=source_block.metadata,
            )
        )
    return artifacts


def normalized_blocks_preview_markdown(blocks: list[BlockArtifact]) -> str:
    first_block = blocks[0]
    lines = [
        f"# Normalized Block Preview: {first_block.title}",
        "",
        f"- doc_id: `{first_block.doc_id}`",
        f"- source_path: `{first_block.source_path}`",
        f"- doc_type: `{first_block.doc_type}`",
        f"- blocks: `{len(blocks)}`",
        "",
        "## Blocks",
        "",
    ]
    for block in blocks:
        page_text = f" page={block.page}" if block.page is not None else ""
        sheet_text = f" sheet={block.sheet!r}" if block.sheet is not None else ""
        section_text = (
            f" section={block.section_path!r}" if block.section_path is not None else ""
        )
        lines.extend(
            [
                f"### {block.block_id}",
                "",
                f"- order: `{block.order}`",
                f"- type: `{block.block_type}`{page_text}{sheet_text}{section_text}",
                f"- metadata: `{json.dumps(block.metadata, ensure_ascii=True)}`",
                "",
                "```text",
                block.text,
                "```",
                "",
            ]
        )
    return "\n".join(lines).strip() + "\n"


def _read_loaded_document_for_source(
    source_path: Path,
    *,
    settings: Settings,
) -> LoadedDocumentArtifact | None:
    doc_id = build_doc_id(source_path)
    loaded_path = loaded_documents_dir(settings) / f"{doc_id}.jsonl"
    records = read_jsonl(loaded_path, LoadedDocumentArtifact)
    return records[0] if records else None


def _blocks_from_loaded_image(record: LoadedDocumentArtifact) -> list[BlockArtifact]:
    metadata = record.metadata
    source_block_metadata = metadata.get("source_block_metadata")
    if not isinstance(source_block_metadata, dict):
        source_block_metadata = {}
    block_type = metadata.get("source_block_type")
    section_path = metadata.get("source_section_path")
    page = metadata.get("source_page")
    sheet = metadata.get("source_sheet")
    return [
        BlockArtifact(
            doc_id=record.doc_id,
            block_id=f"{record.doc_id}:00001",
            source_path=record.source_path,
            doc_type=record.doc_type,
            title=record.title,
            block_type=block_type if isinstance(block_type, str) else "image_vision_text",
            text=record.text,
            section_path=section_path if isinstance(section_path, str) else "Image Extraction",
            page=page if isinstance(page, int) else None,
            sheet=sheet if isinstance(sheet, str) else None,
            order=1,
            metadata=source_block_metadata,
        )
    ]


def _now_iso() -> str:
    from datetime import UTC, datetime

    return datetime.now(UTC).isoformat()
