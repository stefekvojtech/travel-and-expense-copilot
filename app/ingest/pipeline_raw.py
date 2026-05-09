from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from hashlib import sha1, sha256
from pathlib import Path
from typing import Iterable

from app.core.config import ROOT_DIR, Settings
from app.ingest.loaders import (
    SUPPORTED_SUFFIXES,
    infer_doc_type,
    normalize_by_file_type,
)
from app.ingest.artifacts import BlockArtifact
from app.ingest.loaders.models import SourceBlock


@dataclass(frozen=True)
class IngestedDocument:
    # Document-level manifest row: one source file and its generated artifacts.
    doc_id: str
    source_path: str
    output_markdown_path: str
    output_blocks_path: str
    doc_type: str
    title: str
    content_hash: str
    source_size_bytes: int
    source_modified_at: str
    ingested_at: str
    markdown_text: str
    block_count: int
    extraction_method: str
    extraction_warning: str | None


@dataclass(frozen=True)
class IngestResult:
    ingested_documents: list[IngestedDocument]
    skipped_documents: list[IngestedDocument]
    removed_documents: list[IngestedDocument]
    warnings: list[IngestWarning]


@dataclass(frozen=True)
class IngestWarning:
    source_path: str
    warning_type: str
    message: str
    observed_at: str


def discover_raw_files(raw_data_dir: Path) -> list[Path]:
    # Discover every file under raw_data_dir so unsupported types are reported.
    return sorted(path for path in raw_data_dir.rglob("*") if path.is_file())


def split_supported_files(source_paths: Iterable[Path]) -> tuple[list[Path], list[Path]]:
    supported_paths: list[Path] = []
    unsupported_paths: list[Path] = []
    for source_path in source_paths:
        if source_path.suffix.lower() in SUPPORTED_SUFFIXES:
            supported_paths.append(source_path)
        else:
            unsupported_paths.append(source_path)
    return supported_paths, unsupported_paths


def ingest_sources(settings: Settings, *, force: bool = False) -> IngestResult:
    settings.markdown_dir.mkdir(parents=True, exist_ok=True)
    settings.processed_data_dir.mkdir(parents=True, exist_ok=True)
    blocks_dir = settings.processed_data_dir / "blocks"
    blocks_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = settings.processed_data_dir / "ingest_manifest.jsonl"
    warnings_path = settings.processed_data_dir / "ingest_warnings.jsonl"
    previous_documents = _read_manifest(manifest_path)
    previous_by_source = {
        _project_relative_path(Path(document.source_path)): document
        for document in previous_documents
    }
    source_paths, unsupported_paths = split_supported_files(
        discover_raw_files(settings.raw_data_dir)
    )
    current_source_keys = {_project_relative_path(source_path) for source_path in source_paths}
    warnings = [_build_unsupported_warning(path) for path in unsupported_paths]
    removed_documents = _remove_orphaned_markdown(
        previous_documents,
        current_source_keys,
        settings.markdown_dir,
        blocks_dir,
    )

    ingested_documents: list[IngestedDocument] = []
    skipped_documents: list[IngestedDocument] = []
    latest_documents: list[IngestedDocument] = []
    for source_path in source_paths:
        source_key = _project_relative_path(source_path)
        content_hash = _hash_file(source_path)
        previous_document = previous_by_source.get(source_key)
        # Incremental ingestion reuses existing artifacts when the raw file hash matches.
        if (
            not force
            and previous_document is not None
            and previous_document.content_hash == content_hash
            and _resolve_project_path(previous_document.output_markdown_path).exists()
            and _resolve_project_path(previous_document.output_blocks_path).exists()
        ):
            skipped_documents.append(previous_document)
            latest_documents.append(previous_document)
            continue

        document, blocks = normalize_source(
            source_path,
            settings,
            blocks_dir,
            content_hash=content_hash,
        )
        write_markdown(document)
        write_blocks(_resolve_project_path(document.output_blocks_path), blocks)
        ingested_documents.append(document)
        latest_documents.append(document)

    if ingested_documents or removed_documents or len(latest_documents) != len(previous_documents):
        write_manifest(manifest_path, latest_documents)
    write_warnings(warnings_path, warnings)
    return IngestResult(
        ingested_documents=ingested_documents,
        skipped_documents=skipped_documents,
        removed_documents=removed_documents,
        warnings=warnings,
    )


def normalize_source(
    source_path: Path,
    settings: Settings,
    blocks_dir: Path,
    *,
    content_hash: str | None = None,
) -> tuple[IngestedDocument, list[BlockArtifact]]:
    suffix = source_path.suffix.lower()
    normalized_source = normalize_by_file_type(source_path)
    source_reference = _project_relative_path(source_path)
    doc_id = _build_doc_id(source_path)
    doc_type = infer_doc_type(suffix)
    title = source_path.stem.replace("_", " ").replace("-", " ").title()
    output_path = settings.markdown_dir / f"{doc_id}.md"
    blocks_path = blocks_dir / f"{doc_id}.jsonl"
    output_reference = _project_relative_path(output_path)
    blocks_reference = _project_relative_path(blocks_path)
    source_stat = source_path.stat()
    source_hash = content_hash or _hash_file(source_path)
    source_modified_at = _format_timestamp(source_stat.st_mtime)
    ingested_at = _now_iso()

    header = [
        f"# {title}",
        "",
        f"- doc_id: `{doc_id}`",
        f"- source_path: `{source_reference}`",
        f"- doc_type: `{doc_type}`",
        f"- content_hash: `{source_hash}`",
        f"- extraction_method: `{normalized_source.extraction_method}`",
        f"- blocks_path: `{blocks_reference}`",
    ]
    if normalized_source.extraction_warning:
        header.append(f"- extraction_warning: `{normalized_source.extraction_warning}`")

    # Markdown stays readable; the block JSONL carries the detailed lineage.
    markdown = "\n".join(
        header + ["", "## Content", "", normalized_source.markdown_text.strip(), ""]
    ).strip()
    blocks = _build_block_artifacts(
        normalized_source.blocks,
        doc_id=doc_id,
        source_path=source_path,
        doc_type=doc_type,
        title=title,
    )

    return (
        IngestedDocument(
            doc_id=doc_id,
            source_path=source_reference,
            output_markdown_path=output_reference,
            output_blocks_path=blocks_reference,
            doc_type=doc_type,
            title=title,
            content_hash=source_hash,
            source_size_bytes=source_stat.st_size,
            source_modified_at=source_modified_at,
            ingested_at=ingested_at,
            markdown_text=markdown,
            block_count=len(blocks),
            extraction_method=normalized_source.extraction_method,
            extraction_warning=normalized_source.extraction_warning,
        ),
        blocks,
    )


def write_markdown(document: IngestedDocument) -> None:
    output_path = _resolve_project_path(document.output_markdown_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    _write_text_if_changed(output_path, document.markdown_text + "\n")


def write_manifest(output_path: Path, documents: Iterable[IngestedDocument]) -> None:
    rows = [json.dumps(asdict(document), ensure_ascii=True) for document in documents]
    _write_text_if_changed(output_path, "\n".join(rows) + ("\n" if rows else ""))


def write_blocks(output_path: Path, blocks: Iterable[BlockArtifact]) -> None:
    # JSONL keeps each block append/read-friendly for later chunking workflows.
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = [json.dumps(asdict(block), ensure_ascii=True) for block in blocks]
    _write_text_if_changed(output_path, "\n".join(rows) + ("\n" if rows else ""))


def write_warnings(output_path: Path, warnings: Iterable[IngestWarning]) -> None:
    rows = [json.dumps(asdict(warning), ensure_ascii=True) for warning in warnings]
    _write_text_if_changed(output_path, "\n".join(rows) + ("\n" if rows else ""))


def _write_text_if_changed(output_path: Path, text: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists() and output_path.read_text(encoding="utf-8") == text:
        return
    output_path.write_text(text, encoding="utf-8")


def _remove_orphaned_markdown(
    previous_documents: Iterable[IngestedDocument],
    current_source_keys: set[str],
    markdown_dir: Path,
    blocks_dir: Path,
) -> list[IngestedDocument]:
    removed_documents: list[IngestedDocument] = []
    for document in previous_documents:
        if document.source_path in current_source_keys:
            continue

        output_path = _resolve_project_path(document.output_markdown_path)
        # Only remove files inside the configured markdown output directory.
        if output_path.exists() and output_path.resolve().is_relative_to(
            markdown_dir.resolve()
        ):
            output_path.unlink()
        blocks_path = _resolve_project_path(document.output_blocks_path)
        if blocks_path.exists() and blocks_path.resolve().is_relative_to(
            blocks_dir.resolve()
        ):
            blocks_path.unlink()
        removed_documents.append(document)

    return removed_documents


def _read_manifest(manifest_path: Path) -> list[IngestedDocument]:
    if not manifest_path.exists():
        return []

    documents: list[IngestedDocument] = []
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if "content_hash" not in row:
            continue
        documents.append(_document_from_manifest_row(row, manifest_path.parent))
    return documents


def _document_from_manifest_row(row: dict, processed_data_dir: Path) -> IngestedDocument:
    doc_id = row.get("doc_id", "")
    # Backward compatibility for manifests created before block artifacts existed.
    row.setdefault(
        "output_blocks_path",
        (processed_data_dir / "blocks" / f"{doc_id}.jsonl").as_posix(),
    )
    row.setdefault("block_count", 0)
    return IngestedDocument(**row)


def _build_block_artifacts(
    source_blocks: Iterable[SourceBlock],
    *,
    doc_id: str,
    source_path: Path,
    doc_type: str,
    title: str,
) -> list[BlockArtifact]:
    artifacts: list[BlockArtifact] = []
    for index, source_block in enumerate(source_blocks, start=1):
        # Stable local order makes it easy to connect chunks back to source blocks.
        artifacts.append(
            BlockArtifact(
                doc_id=doc_id,
                block_id=f"{doc_id}:{index:05d}",
                source_path=_project_relative_path(source_path),
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


def _build_unsupported_warning(source_path: Path) -> IngestWarning:
    suffix = source_path.suffix.lower() or "[no extension]"
    return IngestWarning(
        source_path=_project_relative_path(source_path),
        warning_type="unsupported_suffix",
        message=f"Skipped unsupported file extension: {suffix}",
        observed_at=_now_iso(),
    )


def _build_doc_id(source_path: Path) -> str:
    digest = sha1(_project_relative_path(source_path).encode("utf-8")).hexdigest()[:10]
    slug = re.sub(r"[^a-z0-9]+", "-", source_path.stem.lower()).strip("-")
    return f"{slug}-{digest}"


def _project_relative_path(path: Path) -> str:
    resolved_path = path if path.is_absolute() else ROOT_DIR / path
    try:
        return resolved_path.resolve().relative_to(ROOT_DIR.resolve()).as_posix()
    except ValueError:
        return resolved_path.as_posix()


def _resolve_project_path(path: str | Path) -> Path:
    resolved_path = Path(path)
    if resolved_path.is_absolute():
        return resolved_path
    return ROOT_DIR / resolved_path


def _hash_file(source_path: Path) -> str:
    digest = sha256()
    with source_path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _format_timestamp(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp, UTC).isoformat()
