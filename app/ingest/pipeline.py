from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from hashlib import sha1, sha256
from pathlib import Path
from typing import Iterable

from app.core.config import Settings
from app.ingest.loaders import (
    SUPPORTED_SUFFIXES,
    infer_doc_type,
    normalize_by_file_type,
)


@dataclass(frozen=True)
class IngestedDocument:
    doc_id: str
    source_path: str
    output_markdown_path: str
    doc_type: str
    title: str
    content_hash: str
    source_size_bytes: int
    source_modified_at: str
    ingested_at: str
    markdown_text: str
    extraction_method: str
    extraction_warning: str | None


@dataclass(frozen=True)
class IngestResult:
    ingested_documents: list[IngestedDocument]
    skipped_documents: list[IngestedDocument]
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

    manifest_path = settings.processed_data_dir / "ingest_manifest.jsonl"
    warnings_path = settings.processed_data_dir / "ingest_warnings.jsonl"
    previous_documents = _read_manifest(manifest_path)
    previous_by_source = {
        document.source_path: document for document in previous_documents
    }
    source_paths, unsupported_paths = split_supported_files(
        discover_raw_files(settings.raw_data_dir)
    )
    warnings = [_build_unsupported_warning(path) for path in unsupported_paths]

    ingested_documents: list[IngestedDocument] = []
    skipped_documents: list[IngestedDocument] = []
    latest_documents: list[IngestedDocument] = []
    for source_path in source_paths:
        source_key = source_path.as_posix()
        content_hash = _hash_file(source_path)
        previous_document = previous_by_source.get(source_key)
        # Incremental ingestion reuses existing Markdown when the source file is unchanged.
        if (
            not force
            and previous_document is not None
            and previous_document.content_hash == content_hash
            and Path(previous_document.output_markdown_path).exists()
        ):
            skipped_documents.append(previous_document)
            latest_documents.append(previous_document)
            continue

        document = normalize_source(source_path, settings, content_hash=content_hash)
        write_markdown(document)
        ingested_documents.append(document)
        latest_documents.append(document)

    write_manifest(manifest_path, latest_documents)
    write_warnings(warnings_path, warnings)
    return IngestResult(
        ingested_documents=ingested_documents,
        skipped_documents=skipped_documents,
        warnings=warnings,
    )


def normalize_source(
    source_path: Path,
    settings: Settings,
    *,
    content_hash: str | None = None,
) -> IngestedDocument:
    suffix = source_path.suffix.lower()
    markdown_text, extraction_method, extraction_warning = normalize_by_file_type(
        source_path
    )
    doc_id = _build_doc_id(source_path)
    doc_type = infer_doc_type(suffix)
    title = source_path.stem.replace("_", " ").replace("-", " ").title()
    output_path = settings.markdown_dir / f"{doc_id}.md"
    source_stat = source_path.stat()
    source_hash = content_hash or _hash_file(source_path)
    source_modified_at = _format_timestamp(source_stat.st_mtime)
    ingested_at = _now_iso()

    header = [
        f"# {title}",
        "",
        f"- doc_id: `{doc_id}`",
        f"- source_path: `{source_path.as_posix()}`",
        f"- doc_type: `{doc_type}`",
        f"- content_hash: `{source_hash}`",
        f"- extraction_method: `{extraction_method}`",
    ]
    if extraction_warning:
        header.append(f"- extraction_warning: `{extraction_warning}`")

    markdown = "\n".join(header + ["", "## Content", "", markdown_text.strip(), ""]).strip()

    return IngestedDocument(
        doc_id=doc_id,
        source_path=source_path.as_posix(),
        output_markdown_path=output_path.as_posix(),
        doc_type=doc_type,
        title=title,
        content_hash=source_hash,
        source_size_bytes=source_stat.st_size,
        source_modified_at=source_modified_at,
        ingested_at=ingested_at,
        markdown_text=markdown,
        extraction_method=extraction_method,
        extraction_warning=extraction_warning,
    )


def write_markdown(document: IngestedDocument) -> None:
    output_path = Path(document.output_markdown_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(document.markdown_text + "\n", encoding="utf-8")


def write_manifest(output_path: Path, documents: Iterable[IngestedDocument]) -> None:
    rows = [json.dumps(asdict(document), ensure_ascii=True) for document in documents]
    output_path.write_text("\n".join(rows) + ("\n" if rows else ""), encoding="utf-8")


def write_warnings(output_path: Path, warnings: Iterable[IngestWarning]) -> None:
    rows = [json.dumps(asdict(warning), ensure_ascii=True) for warning in warnings]
    output_path.write_text("\n".join(rows) + ("\n" if rows else ""), encoding="utf-8")


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
        documents.append(IngestedDocument(**row))
    return documents


def _build_unsupported_warning(source_path: Path) -> IngestWarning:
    suffix = source_path.suffix.lower() or "[no extension]"
    return IngestWarning(
        source_path=source_path.as_posix(),
        warning_type="unsupported_suffix",
        message=f"Skipped unsupported file extension: {suffix}",
        observed_at=_now_iso(),
    )


def _build_doc_id(source_path: Path) -> str:
    digest = sha1(source_path.as_posix().encode("utf-8")).hexdigest()[:10]
    slug = re.sub(r"[^a-z0-9]+", "-", source_path.stem.lower()).strip("-")
    return f"{slug}-{digest}"


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
