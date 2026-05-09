from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from hashlib import sha1
from pathlib import Path
from typing import Any, Iterable

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

from app.core.config import get_settings

ROOT_DIR = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = ROOT_DIR / "data" / "raw"
EXPERIMENT_OUTPUT_DIR = ROOT_DIR / "data" / "processed_langchain_experiment"
CHUNKS_DIR = EXPERIMENT_OUTPUT_DIR / "chunks"
PREVIEWS_DIR = EXPERIMENT_OUTPUT_DIR / "previews"

HEADERS_TO_SPLIT_ON = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
    ("####", "Header 4"),
    ("#####", "Header 5"),
    ("######", "Header 6"),
]


@dataclass(frozen=True)
class LoadedDocumentRecord:
    doc_id: str
    source_path: str
    doc_type: str
    loader_name: str
    document_index: int
    text: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class ExperimentChunk:
    chunk_id: str
    doc_id: str
    source_path: str
    doc_type: str
    text: str
    document_indexes: list[int]
    pages: list[int]
    section_path: str | None
    chunk_strategy: str
    token_count: int
    order: int
    metadata: dict[str, Any]


@dataclass(frozen=True)
class ExperimentWarning:
    source_path: str
    warning_type: str
    message: str
    observed_at: str


@dataclass(frozen=True)
class ExperimentDocumentResult:
    doc_id: str
    source_path: str
    doc_type: str
    loader_name: str
    loaded_document_count: int
    chunk_count: int
    output_chunks_path: str
    output_preview_path: str


@dataclass(frozen=True)
class ExperimentResult:
    documents: list[ExperimentDocumentResult]
    warnings: list[ExperimentWarning]
    chunk_count: int
    output_dir: str


def run_experiment(
    *,
    raw_data_dir: Path = RAW_DATA_DIR,
    output_dir: Path = EXPERIMENT_OUTPUT_DIR,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
    max_chunk_tokens: int | None = None,
) -> ExperimentResult:
    """Load and chunk raw files with LangChain libraries in an isolated output dir."""
    settings = get_settings()
    resolved_chunk_size = chunk_size if chunk_size is not None else settings.chunk_size
    resolved_chunk_overlap = (
        chunk_overlap if chunk_overlap is not None else settings.chunk_overlap
    )
    resolved_max_chunk_tokens = (
        max_chunk_tokens
        if max_chunk_tokens is not None
        else settings.max_chunk_tokens
    )
    chunks_dir = output_dir / "chunks"
    previews_dir = output_dir / "previews"
    chunks_dir.mkdir(parents=True, exist_ok=True)
    previews_dir.mkdir(parents=True, exist_ok=True)

    document_results: list[ExperimentDocumentResult] = []
    warnings: list[ExperimentWarning] = []
    loaded_records: list[LoadedDocumentRecord] = []

    for source_path in sorted(path for path in raw_data_dir.rglob("*") if path.is_file()):
        try:
            records, file_warnings = load_with_langchain(source_path)
        except ImportError as exc:
            records = []
            file_warnings = [
                _warning(
                    source_path,
                    "missing_dependency",
                    f"{exc}. Run `python -m pip install -e .` from the repo root.",
                )
            ]
        except Exception as exc:  # pragma: no cover - defensive experiment logging
            records = []
            file_warnings = [_warning(source_path, "load_failed", str(exc))]

        warnings.extend(file_warnings)
        if not records:
            continue

        chunks = chunk_loaded_documents(
            records,
            chunk_size=resolved_chunk_size,
            chunk_overlap=resolved_chunk_overlap,
            max_chunk_tokens=resolved_max_chunk_tokens,
        )
        chunks_path = chunks_dir / f"{records[0].doc_id}.jsonl"
        preview_path = previews_dir / f"{records[0].doc_id}.md"
        _write_jsonl(chunks_path, chunks)
        _write_text_if_changed(preview_path, _preview_markdown(records, chunks))
        loaded_records.extend(records)
        document_results.append(
            ExperimentDocumentResult(
                doc_id=records[0].doc_id,
                source_path=_project_relative_path(source_path),
                doc_type=records[0].doc_type,
                loader_name=records[0].loader_name,
                loaded_document_count=len(records),
                chunk_count=len(chunks),
                output_chunks_path=_project_relative_path(chunks_path),
                output_preview_path=_project_relative_path(preview_path),
            )
        )

    _write_jsonl(output_dir / "documents.jsonl", loaded_records)
    _write_jsonl(output_dir / "warnings.jsonl", warnings)
    _write_text_if_changed(output_dir / "report.md", _report_markdown(document_results, warnings))
    _remove_orphaned_files(chunks_dir, [Path(result.output_chunks_path) for result in document_results])
    _remove_orphaned_files(previews_dir, [Path(result.output_preview_path) for result in document_results])

    return ExperimentResult(
        documents=document_results,
        warnings=warnings,
        chunk_count=sum(result.chunk_count for result in document_results),
        output_dir=_project_relative_path(output_dir),
    )


def load_with_langchain(source_path: Path) -> tuple[list[LoadedDocumentRecord], list[ExperimentWarning]]:
    """Load a supported source file with LangChain community loaders."""
    suffix = source_path.suffix.lower()
    doc_id = _build_doc_id(source_path)

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
        )
    elif suffix == ".txt":
        from langchain_community.document_loaders import TextLoader

        loader_name = "TextLoader"
        loader = TextLoader(str(source_path), encoding="utf-8", autodetect_encoding=True)
    elif suffix == ".xlsx":
        return [], [
            _warning(
                source_path,
                "unsupported_in_experiment",
                "XLSX is intentionally skipped in this first LangChain chunking experiment.",
            )
        ]
    elif suffix in {".png", ".jpg", ".jpeg"}:
        return [], [
            _warning(
                source_path,
                "skipped_paid_vision",
                "Images are skipped because extracting them would require a paid vision call.",
            )
        ]
    else:
        return [], [_warning(source_path, "unsupported_suffix", f"Skipped {suffix or '[no extension]'}.")]

    documents = list(loader.lazy_load())
    records: list[LoadedDocumentRecord] = []
    for index, document in enumerate(documents, start=1):
        text = _clean_text(document.page_content)
        if not text:
            continue
        records.append(
            LoadedDocumentRecord(
                doc_id=doc_id,
                source_path=_project_relative_path(source_path),
                doc_type=_doc_type(suffix),
                loader_name=loader_name,
                document_index=index,
                text=text,
                metadata=dict(document.metadata),
            )
        )
    return records, []


def chunk_loaded_documents(
    records: list[LoadedDocumentRecord],
    *,
    chunk_size: int,
    chunk_overlap: int,
    max_chunk_tokens: int,
) -> list[ExperimentChunk]:
    """Chunk LangChain-loaded documents with LangChain splitter primitives."""
    effective_chunk_size = _effective_chunk_size(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        max_chunk_tokens=max_chunk_tokens,
    )
    recursive_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=effective_chunk_size,
        chunk_overlap=chunk_overlap,
    )
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=HEADERS_TO_SPLIT_ON,
        strip_headers=False,
    )

    chunks: list[ExperimentChunk] = []
    for record in records:
        split_inputs = _split_markdown_sections(record.text, header_splitter)
        for section_text, section_path in split_inputs:
            section_token_count = recursive_splitter._length_function(section_text)
            strategy = (
                "markdown_header+recursive_tiktoken"
                if section_path and section_token_count > effective_chunk_size
                else "markdown_header+section_as_chunk"
                if section_path
                else "recursive_tiktoken"
            )
            for split_document in recursive_splitter.create_documents([section_text]):
                chunk_text = split_document.page_content.strip()
                if not chunk_text:
                    continue
                chunks.append(
                    ExperimentChunk(
                        chunk_id=f"{record.doc_id}:lc-chunk:{len(chunks) + 1:05d}",
                        doc_id=record.doc_id,
                        source_path=record.source_path,
                        doc_type=record.doc_type,
                        text=chunk_text,
                        document_indexes=[record.document_index],
                        pages=_pages_from_metadata(record.metadata),
                        section_path=section_path,
                        chunk_strategy=strategy,
                        token_count=recursive_splitter._length_function(chunk_text),
                        order=len(chunks) + 1,
                        metadata={
                            "loader_name": record.loader_name,
                            "source_document_metadata": record.metadata,
                        },
                    )
                )
    _validate_chunks_within_max_tokens(chunks, max_chunk_tokens=max_chunk_tokens)
    return chunks


def _effective_chunk_size(
    *,
    chunk_size: int,
    chunk_overlap: int,
    max_chunk_tokens: int,
) -> int:
    if max_chunk_tokens < 1:
        raise ValueError("MAX_CHUNK_TOKENS must be greater than zero.")
    if chunk_size < 1:
        raise ValueError("CHUNK_SIZE must be greater than zero.")

    effective_chunk_size = min(chunk_size, max_chunk_tokens)
    if chunk_overlap >= effective_chunk_size:
        raise ValueError(
            "CHUNK_OVERLAP must be smaller than the effective chunk size "
            f"({effective_chunk_size})."
        )
    return effective_chunk_size


def _validate_chunks_within_max_tokens(
    chunks: Iterable[ExperimentChunk],
    *,
    max_chunk_tokens: int,
) -> None:
    oversized_chunks = [
        f"{chunk.chunk_id} ({chunk.token_count} tokens)"
        for chunk in chunks
        if chunk.token_count > max_chunk_tokens
    ]
    if oversized_chunks:
        raise ValueError(
            "Experimental chunking produced chunks above MAX_CHUNK_TOKENS="
            f"{max_chunk_tokens}: {', '.join(oversized_chunks)}"
        )


def _split_markdown_sections(
    text: str,
    header_splitter: MarkdownHeaderTextSplitter,
) -> list[tuple[str, str | None]]:
    if not _looks_like_markdown_with_headers(text):
        return [(text, None)]

    sections: list[tuple[str, str | None]] = []
    for document in header_splitter.split_text(text):
        section_text = document.page_content.strip()
        if not section_text:
            continue
        sections.append((section_text, _section_path_from_metadata(document.metadata)))
    return sections or [(text, None)]


def _looks_like_markdown_with_headers(text: str) -> bool:
    return any(line.startswith("#") for line in text.splitlines())


def _section_path_from_metadata(metadata: dict[str, Any]) -> str | None:
    values = [metadata[key] for _, key in HEADERS_TO_SPLIT_ON if metadata.get(key)]
    return str(values[-1]) if values else None


def _pages_from_metadata(metadata: dict[str, Any]) -> list[int]:
    page = metadata.get("page")
    if isinstance(page, int):
        return [page + 1]
    return []


def _preview_markdown(
    records: list[LoadedDocumentRecord],
    chunks: list[ExperimentChunk],
    *,
    sample_size: int = 8,
) -> str:
    lines = [
        f"# LangChain Chunk Preview: {Path(records[0].source_path).name}",
        "",
        f"- doc_id: `{records[0].doc_id}`",
        f"- source_path: `{records[0].source_path}`",
        f"- loader: `{records[0].loader_name}`",
        f"- loaded_documents: `{len(records)}`",
        f"- chunks: `{len(chunks)}`",
        "",
        "## Sample Chunks",
        "",
    ]
    for chunk in chunks[:sample_size]:
        page_text = f" pages={chunk.pages}" if chunk.pages else ""
        section_text = f" section={chunk.section_path!r}" if chunk.section_path else ""
        lines.extend(
            [
                f"### {chunk.chunk_id}",
                "",
                f"- strategy: `{chunk.chunk_strategy}`",
                f"- tokens: `{chunk.token_count}`{page_text}{section_text}",
                "",
                "```text",
                chunk.text[:1200],
                "```",
                "",
            ]
        )
    return "\n".join(lines).strip() + "\n"


def _report_markdown(
    documents: list[ExperimentDocumentResult],
    warnings: list[ExperimentWarning],
) -> str:
    lines = [
        "# LangChain Chunking Experiment Report",
        "",
        f"- generated_at: `{_now_iso()}`",
        f"- output_dir: `{_project_relative_path(EXPERIMENT_OUTPUT_DIR)}`",
        f"- documents_chunked: `{len(documents)}`",
        f"- chunks_generated: `{sum(document.chunk_count for document in documents)}`",
        f"- warnings: `{len(warnings)}`",
        "",
        "## Documents",
        "",
        "| Source | Loader | Loaded docs | Chunks | Preview |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for document in documents:
        lines.append(
            "| "
            f"`{document.source_path}` | "
            f"`{document.loader_name}` | "
            f"{document.loaded_document_count} | "
            f"{document.chunk_count} | "
            f"`{document.output_preview_path}` |"
        )

    if warnings:
        lines.extend(["", "## Warnings", ""])
        for warning in warnings:
            lines.append(
                f"- `{warning.source_path}` `{warning.warning_type}`: {warning.message}"
            )
    return "\n".join(lines).strip() + "\n"


def _write_jsonl(output_path: Path, rows: Iterable[object]) -> None:
    text_rows = [json.dumps(asdict(row), ensure_ascii=True) for row in rows]
    _write_text_if_changed(output_path, "\n".join(text_rows) + ("\n" if text_rows else ""))


def _write_text_if_changed(output_path: Path, text: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists() and output_path.read_text(encoding="utf-8") == text:
        return
    output_path.write_text(text, encoding="utf-8")


def _remove_orphaned_files(directory: Path, expected_relative_paths: Iterable[Path]) -> None:
    expected_paths = {
        (ROOT_DIR / path).resolve() if not path.is_absolute() else path.resolve()
        for path in expected_relative_paths
    }
    for path in directory.glob("*"):
        if path.is_file() and path.resolve() not in expected_paths:
            path.unlink()


def _warning(source_path: Path, warning_type: str, message: str) -> ExperimentWarning:
    return ExperimentWarning(
        source_path=_project_relative_path(source_path),
        warning_type=warning_type,
        message=message,
        observed_at=_now_iso(),
    )


def _build_doc_id(source_path: Path) -> str:
    digest = sha1(_project_relative_path(source_path).encode("utf-8")).hexdigest()[:10]
    slug = re.sub(r"[^a-z0-9]+", "-", source_path.stem.lower()).strip("-")
    return f"{slug}-{digest}"


def _doc_type(suffix: str) -> str:
    if suffix == ".pdf":
        return "pdf"
    if suffix in {".html", ".htm"}:
        return "html"
    if suffix == ".txt":
        return "text"
    return "unknown"


def _clean_text(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text.replace("\x00", "")).strip()


def _project_relative_path(path: Path) -> str:
    resolved_path = path if path.is_absolute() else ROOT_DIR / path
    try:
        return resolved_path.resolve().relative_to(ROOT_DIR.resolve()).as_posix()
    except ValueError:
        return resolved_path.as_posix()


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()
