"""Generate the Markdown report for the numbered ingestion pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable

from app.core.config import Settings
from app.ingest.artifact_io import read_jsonl
from app.ingest.artifact_paths import (
    chunk_previews_dir,
    chunks_dir,
    loaded_document_previews_dir,
    loaded_documents_dir,
    normalized_block_previews_dir,
    normalized_blocks_dir,
    project_relative_path,
    report_path,
    write_text_if_changed,
)
from app.ingest.artifacts import BlockArtifact, ChunkArtifact, LoadedDocumentArtifact, PipelineWarning
from app.ingest.source_files import discover_raw_files, split_supported_files


@dataclass(frozen=True)
class ReportDocument:
    source_path: str
    doc_id: str
    doc_type: str
    loader_name: str
    loaded_document_count: int
    normalized_block_count: int
    chunk_count: int
    output_loaded_documents_path: str | None
    output_loaded_documents_preview_path: str | None
    output_normalized_blocks_path: str | None
    output_normalized_blocks_preview_path: str | None
    output_chunks_path: str | None
    output_chunks_preview_path: str | None


def write_pipeline_report(
    settings: Settings,
    *,
    runtime_warnings: Iterable[PipelineWarning] = (),
) -> None:
    """Write `report.md` from current artifacts and current run warnings."""
    documents = _collect_report_documents(settings)
    warnings = _collect_warnings(settings, runtime_warnings)
    write_text_if_changed(report_path(settings), _report_markdown(settings, documents, warnings))


def _collect_report_documents(settings: Settings) -> list[ReportDocument]:
    loaded_by_doc_id = _read_loaded_records(settings)
    blocks_by_doc_id = _read_block_records(settings)
    chunks_by_doc_id = _read_chunk_records(settings)
    doc_ids = sorted(
        {
            *loaded_by_doc_id.keys(),
            *blocks_by_doc_id.keys(),
            *chunks_by_doc_id.keys(),
        },
        key=lambda doc_id: _document_sort_key(doc_id, loaded_by_doc_id, blocks_by_doc_id, chunks_by_doc_id),
    )

    documents: list[ReportDocument] = []
    for doc_id in doc_ids:
        loaded_records = loaded_by_doc_id.get(doc_id, [])
        blocks = blocks_by_doc_id.get(doc_id, [])
        chunks = chunks_by_doc_id.get(doc_id, [])
        source_path = _first_source_path(loaded_records, blocks, chunks)
        doc_type = _first_doc_type(loaded_records, blocks, chunks)
        loader_name = loaded_records[0].loader_name if loaded_records else ""
        documents.append(
            ReportDocument(
                source_path=source_path,
                doc_id=doc_id,
                doc_type=doc_type,
                loader_name=loader_name,
                loaded_document_count=len(loaded_records),
                normalized_block_count=len(blocks),
                chunk_count=len(chunks),
                output_loaded_documents_path=_path_if_exists(loaded_documents_dir(settings) / f"{doc_id}.jsonl"),
                output_loaded_documents_preview_path=_path_if_exists(
                    loaded_document_previews_dir(settings) / f"{doc_id}.md"
                ),
                output_normalized_blocks_path=_path_if_exists(normalized_blocks_dir(settings) / f"{doc_id}.jsonl"),
                output_normalized_blocks_preview_path=_path_if_exists(
                    normalized_block_previews_dir(settings) / f"{doc_id}.md"
                ),
                output_chunks_path=_path_if_exists(chunks_dir(settings) / f"{doc_id}.jsonl"),
                output_chunks_preview_path=_path_if_exists(chunk_previews_dir(settings) / f"{doc_id}.md"),
            )
        )
    return documents


def _read_loaded_records(settings: Settings) -> dict[str, list[LoadedDocumentArtifact]]:
    records_by_doc_id: dict[str, list[LoadedDocumentArtifact]] = {}
    for path in sorted(loaded_documents_dir(settings).glob("*.jsonl")):
        records = read_jsonl(path, LoadedDocumentArtifact)
        if records:
            records_by_doc_id[records[0].doc_id] = records
    return records_by_doc_id


def _read_block_records(settings: Settings) -> dict[str, list[BlockArtifact]]:
    blocks_by_doc_id: dict[str, list[BlockArtifact]] = {}
    for path in sorted(normalized_blocks_dir(settings).glob("*.jsonl")):
        blocks = read_jsonl(path, BlockArtifact)
        if blocks:
            blocks_by_doc_id[blocks[0].doc_id] = blocks
    return blocks_by_doc_id


def _read_chunk_records(settings: Settings) -> dict[str, list[ChunkArtifact]]:
    chunks_by_doc_id: dict[str, list[ChunkArtifact]] = {}
    for path in sorted(chunks_dir(settings).glob("*.jsonl")):
        chunks = read_jsonl(path, ChunkArtifact)
        if chunks:
            chunks_by_doc_id[chunks[0].doc_id] = chunks
    return chunks_by_doc_id


def _collect_warnings(
    settings: Settings,
    runtime_warnings: Iterable[PipelineWarning],
) -> list[PipelineWarning]:
    _, unsupported_paths = split_supported_files(discover_raw_files(settings.raw_data_dir))
    warnings = [
        PipelineWarning(
            source_path=project_relative_path(path),
            warning_type="unsupported_suffix",
            message=f"Skipped unsupported file extension: {path.suffix.lower() or '[no extension]'}",
            observed_at=_now_iso(),
        )
        for path in unsupported_paths
    ]
    for records in _read_loaded_records(settings).values():
        for record in records:
            warning_type = record.metadata.get("extraction_warning")
            if isinstance(warning_type, str) and warning_type:
                warnings.append(
                    PipelineWarning(
                        source_path=record.source_path,
                        warning_type=warning_type,
                        message=f"Loaded with warning: {warning_type}",
                        observed_at=_now_iso(),
                    )
                )
    warnings.extend(runtime_warnings)
    return _dedupe_warnings(warnings)


def _report_markdown(
    settings: Settings,
    documents: list[ReportDocument],
    warnings: list[PipelineWarning],
) -> str:
    lines = [
        "# Ingestion Pipeline Report",
        "",
        f"- generated_at: `{_now_iso()}`",
        f"- output_dir: `{project_relative_path(settings.processed_data_dir)}`",
        f"- documents_loaded: `{sum(1 for document in documents if document.loaded_document_count)}`",
        f"- blocks_normalized: `{sum(document.normalized_block_count for document in documents)}`",
        f"- chunks_generated: `{sum(document.chunk_count for document in documents)}`",
        f"- warnings: `{len(warnings)}`",
        "",
        "## Documents",
        "",
        "| Source | Loader | Loaded docs | Blocks | Chunks | Loaded docs | Loaded preview | Blocks | Blocks preview | Chunks | Chunk preview |",
        "| --- | --- | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- |",
    ]
    for document in documents:
        lines.append(
            "| "
            f"`{document.source_path}` | "
            f"`{document.loader_name}` | "
            f"{document.loaded_document_count} | "
            f"{document.normalized_block_count} | "
            f"{document.chunk_count} | "
            f"{_format_optional_path(document.output_loaded_documents_path)} | "
            f"{_format_optional_path(document.output_loaded_documents_preview_path)} | "
            f"{_format_optional_path(document.output_normalized_blocks_path)} | "
            f"{_format_optional_path(document.output_normalized_blocks_preview_path)} | "
            f"{_format_optional_path(document.output_chunks_path)} | "
            f"{_format_optional_path(document.output_chunks_preview_path)} |"
        )

    lines.extend(
        [
            "",
            "## Warnings",
            "",
            "| Source | Type | Message | Observed at |",
            "| --- | --- | --- | --- |",
        ]
    )
    if warnings:
        for warning in warnings:
            lines.append(
                "| "
                f"`{_escape_markdown_table_cell(warning.source_path)}` | "
                f"`{_escape_markdown_table_cell(warning.warning_type)}` | "
                f"{_escape_markdown_table_cell(warning.message)} | "
                f"`{_escape_markdown_table_cell(warning.observed_at)}` |"
            )
    else:
        lines.append("|  |  | No warnings. |  |")
    return "\n".join(lines).strip() + "\n"


def _document_sort_key(
    doc_id: str,
    loaded_by_doc_id: dict[str, list[LoadedDocumentArtifact]],
    blocks_by_doc_id: dict[str, list[BlockArtifact]],
    chunks_by_doc_id: dict[str, list[ChunkArtifact]],
) -> str:
    return _first_source_path(
        loaded_by_doc_id.get(doc_id, []),
        blocks_by_doc_id.get(doc_id, []),
        chunks_by_doc_id.get(doc_id, []),
    )


def _first_source_path(
    loaded_records: list[LoadedDocumentArtifact],
    blocks: list[BlockArtifact],
    chunks: list[ChunkArtifact],
) -> str:
    if loaded_records:
        return loaded_records[0].source_path
    if blocks:
        return blocks[0].source_path
    if chunks:
        return chunks[0].source_path
    return ""


def _first_doc_type(
    loaded_records: list[LoadedDocumentArtifact],
    blocks: list[BlockArtifact],
    chunks: list[ChunkArtifact],
) -> str:
    if loaded_records:
        return loaded_records[0].doc_type
    if blocks:
        return blocks[0].doc_type
    if chunks:
        return chunks[0].doc_type
    return ""


def _path_if_exists(path: Path) -> str | None:
    return project_relative_path(path) if path.exists() else None


def _format_optional_path(path: str | None) -> str:
    return f"`{path}`" if path else ""


def _dedupe_warnings(warnings: list[PipelineWarning]) -> list[PipelineWarning]:
    by_key: dict[tuple[str, str, str], PipelineWarning] = {}
    for warning in warnings:
        by_key[(warning.source_path, warning.warning_type, warning.message)] = warning
    return sorted(by_key.values(), key=lambda warning: (warning.source_path, warning.warning_type))


def _escape_markdown_table_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()
