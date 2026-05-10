"""Load raw sources into per-document inspection artifacts.

This first stage writes `01_loaded_documents` JSONL files and matching readable
Markdown previews. PDF, HTML, and TXT sources use LangChain community loaders.
XLSX and image sources use the project's production loaders so source coverage
matches the main pipeline; image loading may call paid OpenAI vision when an API
key is configured.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from langchain_core.documents import Document

from app.core.config import Settings
from app.ingest.artifact_io import write_jsonl
from app.ingest.artifact_paths import (
    loaded_document_previews_dir,
    loaded_documents_dir,
    project_relative_path,
    reset_artifact_dir,
    write_text_if_changed,
)
from app.ingest.artifacts import LoadedDocumentArtifact, PipelineWarning
from app.ingest.loaders import IMAGE_SUFFIXES, normalize_by_file_type
from app.ingest.source_files import (
    build_doc_id,
    discover_raw_files,
    doc_type_from_source_path,
    split_supported_files,
    title_from_source_path,
)


@dataclass(frozen=True)
class LoadedDocument:
    doc_id: str
    source_path: str
    output_loaded_documents_path: str
    output_loaded_documents_preview_path: str
    doc_type: str
    title: str
    loader_name: str
    loaded_document_count: int


@dataclass(frozen=True)
class LoadDocumentsResult:
    documents: list[LoadedDocument]
    warnings: list[PipelineWarning]


def load_all_documents(settings: Settings) -> LoadDocumentsResult:
    """Load all supported raw files and rebuild the stage 01 artifact folders."""
    output_dir = loaded_documents_dir(settings)
    preview_dir = loaded_document_previews_dir(settings)
    reset_artifact_dir(output_dir, pattern="*.jsonl")
    reset_artifact_dir(preview_dir, pattern="*.md")

    source_paths, unsupported_paths = split_supported_files(
        discover_raw_files(settings.raw_data_dir)
    )
    warnings = [_unsupported_warning(path) for path in unsupported_paths]
    loaded_documents: list[LoadedDocument] = []

    for source_path in source_paths:
        try:
            records, file_warnings = load_source_documents(source_path)
        except ImportError as exc:
            records = []
            file_warnings = [
                _warning(
                    source_path,
                    "missing_dependency",
                    f"{exc}. Run `python -m pip install -e .` from the repo root.",
                )
            ]
        except Exception as exc:
            records = []
            file_warnings = [_warning(source_path, "load_failed", str(exc))]

        warnings.extend(file_warnings)
        if not records:
            continue

        doc_id = records[0].doc_id
        loaded_path = output_dir / f"{doc_id}.jsonl"
        preview_path = preview_dir / f"{doc_id}.md"
        write_jsonl(loaded_path, records)
        write_text_if_changed(preview_path, loaded_documents_preview_markdown(records))
        loaded_documents.append(
            LoadedDocument(
                doc_id=doc_id,
                source_path=records[0].source_path,
                output_loaded_documents_path=project_relative_path(loaded_path),
                output_loaded_documents_preview_path=project_relative_path(preview_path),
                doc_type=records[0].doc_type,
                title=records[0].title,
                loader_name=records[0].loader_name,
                loaded_document_count=len(records),
            )
        )

    return LoadDocumentsResult(documents=loaded_documents, warnings=warnings)


def load_source_documents(source_path: Path) -> tuple[list[LoadedDocumentArtifact], list[PipelineWarning]]:
    """Load one raw file into inspection records."""
    suffix = source_path.suffix.lower()
    if suffix in {".pdf", ".html", ".htm", ".txt"}:
        return _load_with_langchain(source_path)
    if suffix == ".xlsx" or suffix in IMAGE_SUFFIXES:
        return _load_with_project_normalizer(source_path)
    return [], [_unsupported_warning(source_path)]


def loaded_documents_preview_markdown(records: list[LoadedDocumentArtifact]) -> str:
    first_record = records[0]
    lines = [
        f"# Loaded Document Preview: {first_record.title}",
        "",
        f"- doc_id: `{first_record.doc_id}`",
        f"- source_path: `{first_record.source_path}`",
        f"- doc_type: `{first_record.doc_type}`",
        f"- loader: `{first_record.loader_name}`",
        f"- loaded_documents: `{len(records)}`",
        "",
    ]
    for record in records:
        lines.extend(
            [
                f"## Document {record.document_index}",
                "",
                f"- metadata: `{json.dumps(record.metadata, ensure_ascii=True)}`",
                "",
                "```text",
                record.text,
                "```",
                "",
            ]
        )
    return "\n".join(lines).strip() + "\n"


def _load_with_langchain(source_path: Path) -> tuple[list[LoadedDocumentArtifact], list[PipelineWarning]]:
    suffix = source_path.suffix.lower()
    doc_id = build_doc_id(source_path)
    source_reference = project_relative_path(source_path)
    doc_type = doc_type_from_source_path(source_path)
    title = title_from_source_path(source_path)

    if suffix == ".pdf":
        from langchain_community.document_loaders import PyPDFLoader

        loader_name = "PyPDFLoader"
        loader = PyPDFLoader(str(source_path), mode="page")
    elif suffix in {".html", ".htm"}:
        from langchain_community.document_loaders import BSHTMLLoader

        loader_name = "BSHTMLLoader"
        loader = BSHTMLLoader(
            str(source_path),
            open_encoding="utf-8",
            bs_kwargs={"features": "html.parser"},
            get_text_separator="\n",
        )
    else:
        from langchain_community.document_loaders import TextLoader

        loader_name = "TextLoader"
        loader = TextLoader(str(source_path), encoding="utf-8", autodetect_encoding=True)

    documents: list[Document] = []
    for index, document in enumerate(loader.lazy_load(), start=1):
        text = _clean_text(document.page_content)
        if not text:
            continue
        documents.append(
            Document(
                page_content=text,
                metadata={
                    **dict(document.metadata),
                    "pipeline_doc_id": doc_id,
                    "pipeline_source_path": source_reference,
                    "pipeline_doc_type": doc_type,
                    "pipeline_title": title,
                    "pipeline_loader_name": loader_name,
                    "pipeline_document_index": index,
                },
            )
        )

    if suffix == ".pdf":
        documents = _merge_pdf_page_documents(documents)

    return [_record_from_document(document) for document in documents], []


def _load_with_project_normalizer(
    source_path: Path,
) -> tuple[list[LoadedDocumentArtifact], list[PipelineWarning]]:
    normalized_source = normalize_by_file_type(source_path)
    doc_id = build_doc_id(source_path)
    source_reference = project_relative_path(source_path)
    doc_type = doc_type_from_source_path(source_path)
    title = title_from_source_path(source_path)
    metadata: dict[str, Any] = {
        "extraction_method": normalized_source.extraction_method,
        "extraction_warning": normalized_source.extraction_warning,
    }
    if normalized_source.blocks:
        metadata["source_block_count"] = len(normalized_source.blocks)
        first_block = normalized_source.blocks[0]
        if doc_type == "image":
            metadata.update(
                {
                    "source_block_type": first_block.block_type,
                    "source_section_path": first_block.section_path,
                    "source_page": first_block.page,
                    "source_sheet": first_block.sheet,
                    "source_block_metadata": first_block.metadata,
                }
            )

    records = [
        LoadedDocumentArtifact(
            doc_id=doc_id,
            source_path=source_reference,
            doc_type=doc_type,
            title=title,
            loader_name=normalized_source.extraction_method,
            document_index=1,
            text=normalized_source.markdown_text,
            metadata=metadata,
        )
    ]
    warnings = []
    if normalized_source.extraction_warning:
        warnings.append(
            _warning(
                source_path,
                normalized_source.extraction_warning,
                f"Loaded with warning: {normalized_source.extraction_warning}",
            )
        )
    return records, warnings


def _record_from_document(document: Document) -> LoadedDocumentArtifact:
    metadata = document.metadata
    return LoadedDocumentArtifact(
        doc_id=str(metadata["pipeline_doc_id"]),
        source_path=str(metadata["pipeline_source_path"]),
        doc_type=str(metadata["pipeline_doc_type"]),
        title=str(metadata["pipeline_title"]),
        loader_name=str(metadata["pipeline_loader_name"]),
        document_index=int(metadata["pipeline_document_index"]),
        text=document.page_content,
        metadata=_source_document_metadata(metadata),
    )


def _merge_pdf_page_documents(documents: list[Document]) -> list[Document]:
    if len(documents) <= 1:
        return documents

    text_parts: list[str] = []
    page_spans: list[dict[str, int]] = []
    source_document_indexes: list[int] = []
    source_metadata: list[dict[str, Any]] = []
    for document in documents:
        metadata = document.metadata
        page_number = _page_number_from_metadata(metadata)
        document_index = int(metadata["pipeline_document_index"])
        part = f"<!-- source_page: {page_number} -->\n\n{document.page_content}"
        start = sum(len(text_part) for text_part in text_parts)
        if text_parts:
            start += 2 * len(text_parts)
        text_parts.append(part)
        page_spans.append(
            {
                "page": page_number,
                "document_index": document_index,
                "start": start,
                "end": start + len(part),
            }
        )
        source_document_indexes.append(document_index)
        source_metadata.append(_source_document_metadata(metadata))

    first_metadata = documents[0].metadata
    merged_metadata = {
        **first_metadata,
        "pipeline_document_index": 1,
        "pipeline_merged_document_count": len(documents),
        "pipeline_pages": [span["page"] for span in page_spans],
        "pipeline_source_document_indexes": source_document_indexes,
        "pipeline_page_spans": page_spans,
        "pipeline_source_document_metadata": source_metadata,
    }
    return [
        Document(
            page_content="\n\n".join(text_parts),
            metadata=merged_metadata,
        )
    ]


def _page_number_from_metadata(metadata: dict[str, Any]) -> int:
    page = metadata.get("page")
    if isinstance(page, int):
        return page + 1
    return int(metadata["pipeline_document_index"])


def _source_document_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    if "pipeline_source_document_metadata" in metadata:
        return {"merged_from": metadata["pipeline_source_document_metadata"]}
    return {
        key: value
        for key, value in metadata.items()
        if not key.startswith("pipeline_") and key != "start_index"
    }


def _unsupported_warning(source_path: Path) -> PipelineWarning:
    suffix = source_path.suffix.lower() or "[no extension]"
    return _warning(
        source_path,
        "unsupported_suffix",
        f"Skipped unsupported file extension: {suffix}",
    )


def _warning(source_path: Path, warning_type: str, message: str) -> PipelineWarning:
    return PipelineWarning(
        source_path=project_relative_path(source_path),
        warning_type=warning_type,
        message=message,
        observed_at=_now_iso(),
    )


def _clean_text(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text.replace("\x00", "")).strip()


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()
