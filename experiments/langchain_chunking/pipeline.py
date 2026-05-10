"""Compare LangChain loaders and splitters against the production ingestion path.

This experiment loads raw demo sources with LangChain community loaders, chunks
the resulting documents with LangChain splitters, and writes isolated document,
preview, report, and chunk artifacts under `data/processed_langchain_experiment`.
It intentionally skips XLSX and image vision extraction in this first pass.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from hashlib import sha1
from pathlib import Path
from typing import Any, Callable, Iterable

from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

from app.core.config import get_settings
from app.ingest.artifacts import ChunkArtifact

ROOT_DIR = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = ROOT_DIR / "data" / "raw"
EXPERIMENT_OUTPUT_DIR = ROOT_DIR / "data" / "processed_langchain_experiment"
LOCAL_AGENT_INSTRUCTION_FILENAME = "AGENTS.md"
DOCUMENTS_DIR_NAME = "01_documents"
DOCUMENT_PREVIEWS_DIR_NAME = "02_documents_preview"
CHUNKS_DIR_NAME = "03_chunks"
CHUNK_PREVIEWS_DIR_NAME = "04_chunks_preview"

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
    output_documents_path: str
    output_documents_preview_path: str
    output_chunks_path: str
    output_chunks_preview_path: str


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
    documents_dir = output_dir / DOCUMENTS_DIR_NAME
    document_previews_dir = output_dir / DOCUMENT_PREVIEWS_DIR_NAME
    chunks_dir = output_dir / CHUNKS_DIR_NAME
    chunk_previews_dir = output_dir / CHUNK_PREVIEWS_DIR_NAME
    documents_dir.mkdir(parents=True, exist_ok=True)
    document_previews_dir.mkdir(parents=True, exist_ok=True)
    chunks_dir.mkdir(parents=True, exist_ok=True)
    chunk_previews_dir.mkdir(parents=True, exist_ok=True)

    document_results: list[ExperimentDocumentResult] = []
    warnings: list[ExperimentWarning] = []

    for source_path in sorted(
        path
        for path in raw_data_dir.rglob("*")
        if path.is_file() and path.name != LOCAL_AGENT_INSTRUCTION_FILENAME
    ):
        try:
            documents, file_warnings = load_with_langchain(source_path)
        except ImportError as exc:
            documents = []
            file_warnings = [
                _warning(
                    source_path,
                    "missing_dependency",
                    f"{exc}. Run `python -m pip install -e .` from the repo root.",
                )
            ]
        except Exception as exc:  # pragma: no cover - defensive experiment logging
            documents = []
            file_warnings = [_warning(source_path, "load_failed", str(exc))]

        warnings.extend(file_warnings)
        if not documents:
            continue

        chunks = chunk_loaded_documents(
            documents,
            chunk_size=resolved_chunk_size,
            chunk_overlap=resolved_chunk_overlap,
            max_chunk_tokens=resolved_max_chunk_tokens,
        )
        records = _loaded_records_from_documents(documents)
        doc_id = str(documents[0].metadata["experiment_doc_id"])
        documents_path = documents_dir / f"{doc_id}.jsonl"
        document_preview_path = document_previews_dir / f"{doc_id}.md"
        chunks_path = chunks_dir / f"{doc_id}.jsonl"
        chunk_preview_path = chunk_previews_dir / f"{doc_id}.md"
        _write_jsonl(documents_path, records)
        _write_text_if_changed(
            document_preview_path,
            _documents_preview_markdown(documents),
        )
        _write_jsonl(chunks_path, chunks)
        _write_text_if_changed(
            chunk_preview_path,
            _chunks_preview_markdown(documents, chunks),
        )
        document_results.append(
            ExperimentDocumentResult(
                doc_id=doc_id,
                source_path=_project_relative_path(source_path),
                doc_type=str(documents[0].metadata["experiment_doc_type"]),
                loader_name=str(documents[0].metadata["experiment_loader_name"]),
                loaded_document_count=len(documents),
                chunk_count=len(chunks),
                output_documents_path=_project_relative_path(documents_path),
                output_documents_preview_path=_project_relative_path(document_preview_path),
                output_chunks_path=_project_relative_path(chunks_path),
                output_chunks_preview_path=_project_relative_path(chunk_preview_path),
            )
        )

    _write_text_if_changed(output_dir / "report.md", _report_markdown(document_results, warnings))
    _remove_orphaned_files(documents_dir, [Path(result.output_documents_path) for result in document_results])
    _remove_orphaned_files(
        document_previews_dir,
        [Path(result.output_documents_preview_path) for result in document_results],
    )
    _remove_orphaned_files(chunks_dir, [Path(result.output_chunks_path) for result in document_results])
    _remove_orphaned_files(
        chunk_previews_dir,
        [Path(result.output_chunks_preview_path) for result in document_results],
    )
    _remove_legacy_artifacts(output_dir)

    return ExperimentResult(
        documents=document_results,
        warnings=warnings,
        chunk_count=sum(result.chunk_count for result in document_results),
        output_dir=_project_relative_path(output_dir),
    )


def load_with_langchain(source_path: Path) -> tuple[list[Document], list[ExperimentWarning]]:
    """Load a supported source file with LangChain community loaders."""
    suffix = source_path.suffix.lower()
    doc_id = _build_doc_id(source_path)
    source_reference = _project_relative_path(source_path)
    doc_type = _doc_type(suffix)

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

    documents: list[Document] = []
    for index, document in enumerate(loader.lazy_load(), start=1):
        text = _clean_text(document.page_content)
        if not text:
            continue
        metadata = {
            **dict(document.metadata),
            "experiment_doc_id": doc_id,
            "experiment_source_path": source_reference,
            "experiment_doc_type": doc_type,
            "experiment_loader_name": loader_name,
            "experiment_document_index": index,
        }
        documents.append(
            Document(
                page_content=text,
                metadata=metadata,
            )
        )
    return documents, []


def chunk_loaded_documents(
    documents: list[Document],
    *,
    chunk_size: int,
    chunk_overlap: int,
    max_chunk_tokens: int,
) -> list[ChunkArtifact]:
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
        add_start_index=True,
    )
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=HEADERS_TO_SPLIT_ON,
        strip_headers=False,
    )

    documents_for_recursive_split = _prepare_documents_for_recursive_split(
        documents,
        header_splitter=header_splitter,
        length_function=recursive_splitter._length_function,
        effective_chunk_size=effective_chunk_size,
    )

    chunks: list[ChunkArtifact] = []
    for split_document in recursive_splitter.split_documents(
        documents_for_recursive_split
    ):
        chunk_text = split_document.page_content.strip()
        if not chunk_text:
            continue
        metadata = split_document.metadata
        doc_id = str(metadata["experiment_doc_id"])
        source_path = str(metadata["experiment_source_path"])
        document_index = int(metadata["experiment_document_index"])
        chunks.append(
            ChunkArtifact(
                chunk_id=f"{doc_id}:lc-chunk:{len(chunks) + 1:05d}",
                doc_id=doc_id,
                source_path=source_path,
                doc_type=str(metadata["experiment_doc_type"]),
                title=_title_from_source_path(source_path),
                text=chunk_text,
                source_block_ids=[f"{doc_id}:lc-document:{document_index:05d}"],
                pages=_pages_from_metadata(metadata),
                sheets=[],
                section_path=_section_path_from_metadata(metadata),
                chunk_strategy=str(metadata["experiment_chunk_strategy"]),
                token_count=recursive_splitter._length_function(chunk_text),
                order=len(chunks) + 1,
                metadata={
                    "loader_name": metadata["experiment_loader_name"],
                    "start_index": metadata.get("start_index"),
                    "source_document_metadata": _source_document_metadata(metadata),
                },
            )
        )
    _validate_chunks_within_max_tokens(chunks, max_chunk_tokens=max_chunk_tokens)
    return chunks


def _prepare_documents_for_recursive_split(
    documents: list[Document],
    *,
    header_splitter: MarkdownHeaderTextSplitter,
    length_function: Callable[[str], int],
    effective_chunk_size: int,
) -> list[Document]:
    prepared_documents: list[Document] = []
    for document in documents:
        if not _looks_like_markdown_with_headers(document.page_content):
            prepared_documents.append(
                Document(
                    page_content=document.page_content,
                    metadata={
                        **document.metadata,
                        "experiment_section_path": None,
                        "experiment_chunk_strategy": _chunk_strategy(
                            has_markdown_header=False,
                            token_count=length_function(document.page_content),
                            effective_chunk_size=effective_chunk_size,
                        ),
                    },
                )
            )
            continue

        for section_document in header_splitter.split_text(document.page_content):
            section_text = section_document.page_content.strip()
            if not section_text:
                continue
            section_metadata = {
                **document.metadata,
                **section_document.metadata,
            }
            section_path = _section_path_from_metadata(section_metadata)
            prepared_documents.append(
                Document(
                    page_content=section_text,
                    metadata={
                        **section_metadata,
                        "experiment_section_path": section_path,
                        "experiment_chunk_strategy": _chunk_strategy(
                            has_markdown_header=section_path is not None,
                            token_count=length_function(section_text),
                            effective_chunk_size=effective_chunk_size,
                        ),
                    },
                )
            )
    return prepared_documents


def _chunk_strategy(
    *,
    has_markdown_header: bool,
    token_count: int,
    effective_chunk_size: int,
) -> str:
    prefix = "markdown_header" if has_markdown_header else "plain_text"
    suffix = "recursive_tiktoken" if token_count > effective_chunk_size else "section_as_chunk"
    return f"{prefix}+{suffix}"


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
    chunks: Iterable[ChunkArtifact],
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


def _looks_like_markdown_with_headers(text: str) -> bool:
    return any(line.startswith("#") for line in text.splitlines())


def _section_path_from_metadata(metadata: dict[str, Any]) -> str | None:
    if "experiment_section_path" in metadata:
        section_path = metadata["experiment_section_path"]
        return str(section_path) if section_path else None
    values = [metadata[key] for _, key in HEADERS_TO_SPLIT_ON if metadata.get(key)]
    return str(values[-1]) if values else None


def _pages_from_metadata(metadata: dict[str, Any]) -> list[int]:
    page = metadata.get("page")
    if isinstance(page, int):
        return [page + 1]
    return []


def _documents_preview_markdown(documents: list[Document]) -> str:
    metadata = documents[0].metadata
    lines = [
        f"# LangChain Document Preview: {Path(str(metadata['experiment_source_path'])).name}",
        "",
        f"- doc_id: `{metadata['experiment_doc_id']}`",
        f"- source_path: `{metadata['experiment_source_path']}`",
        f"- loader: `{metadata['experiment_loader_name']}`",
        f"- loaded_documents: `{len(documents)}`",
        "",
    ]
    for document in documents:
        document_metadata = document.metadata
        page_text = _format_pages(_pages_from_metadata(document_metadata))
        lines.extend(
            [
                f"## Document {document_metadata['experiment_document_index']}",
                "",
                f"- source_document_metadata: `{json.dumps(_source_document_metadata(document_metadata), ensure_ascii=True)}`",
                f"- pages: `{page_text}`",
                "",
                "```text",
                document.page_content,
                "```",
                "",
            ]
        )
    return "\n".join(lines).strip() + "\n"


def _chunks_preview_markdown(
    documents: list[Document],
    chunks: list[ChunkArtifact],
) -> str:
    metadata = documents[0].metadata
    lines = [
        f"# LangChain Chunk Preview: {Path(str(metadata['experiment_source_path'])).name}",
        "",
        f"- doc_id: `{metadata['experiment_doc_id']}`",
        f"- source_path: `{metadata['experiment_source_path']}`",
        f"- loader: `{metadata['experiment_loader_name']}`",
        f"- loaded_documents: `{len(documents)}`",
        f"- chunks: `{len(chunks)}`",
        "",
        "## Chunks",
        "",
    ]
    for chunk in chunks:
        page_text = f" pages={chunk.pages}" if chunk.pages else ""
        section_text = f" section={chunk.section_path!r}" if chunk.section_path else ""
        lines.extend(
            [
                f"### {chunk.chunk_id}",
                "",
                f"- strategy: `{chunk.chunk_strategy}`",
                f"- tokens: `{chunk.token_count}`{page_text}{section_text}",
                f"- source_block_ids: `{json.dumps(chunk.source_block_ids, ensure_ascii=True)}`",
                "",
                "```text",
                chunk.text,
                "```",
                "",
            ]
        )
    return "\n".join(lines).strip() + "\n"


def _loaded_records_from_documents(documents: list[Document]) -> list[LoadedDocumentRecord]:
    records: list[LoadedDocumentRecord] = []
    for document in documents:
        metadata = document.metadata
        records.append(
            LoadedDocumentRecord(
                doc_id=str(metadata["experiment_doc_id"]),
                source_path=str(metadata["experiment_source_path"]),
                doc_type=str(metadata["experiment_doc_type"]),
                loader_name=str(metadata["experiment_loader_name"]),
                document_index=int(metadata["experiment_document_index"]),
                text=document.page_content,
                metadata=_source_document_metadata(metadata),
            )
        )
    return records


def _source_document_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    header_names = {header_name for _, header_name in HEADERS_TO_SPLIT_ON}
    return {
        key: value
        for key, value in metadata.items()
        if not key.startswith("experiment_")
        and key not in {"start_index", *header_names}
    }


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
        "| Source | Loader | Loaded docs | Chunks | Documents | Document preview | Chunks | Chunk preview |",
        "| --- | --- | ---: | ---: | --- | --- | --- | --- |",
    ]
    for document in documents:
        lines.append(
            "| "
            f"`{document.source_path}` | "
            f"`{document.loader_name}` | "
            f"{document.loaded_document_count} | "
            f"{document.chunk_count} | "
            f"`{document.output_documents_path}` | "
            f"`{document.output_documents_preview_path}` | "
            f"`{document.output_chunks_path}` | "
            f"`{document.output_chunks_preview_path}` |"
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


def _remove_legacy_artifacts(output_dir: Path) -> None:
    for legacy_file in (output_dir / "documents.jsonl", output_dir / "warnings.jsonl"):
        if legacy_file.exists() and legacy_file.resolve().is_relative_to(output_dir.resolve()):
            legacy_file.unlink()
    for legacy_dir_name in ("chunks", "previews"):
        legacy_dir = output_dir / legacy_dir_name
        if legacy_dir.exists() and legacy_dir.resolve().is_relative_to(output_dir.resolve()):
            for path in sorted(legacy_dir.rglob("*"), reverse=True):
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    path.rmdir()
            legacy_dir.rmdir()


def _format_pages(pages: list[int]) -> str:
    return json.dumps(pages, ensure_ascii=True) if pages else "[]"


def _escape_markdown_table_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


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


def _title_from_source_path(source_path: str) -> str:
    return Path(source_path).stem.replace("_", " ").replace("-", " ").title()


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
