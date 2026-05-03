from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

from app.core.config import Settings


HEADERS_TO_SPLIT_ON = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
    ("####", "Header 4"),
    ("#####", "Header 5"),
    ("######", "Header 6"),
]


@dataclass(frozen=True)
class SourceBlockRecord:
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
    metadata: dict


@dataclass(frozen=True)
class ChunkArtifact:
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
    metadata: dict


@dataclass(frozen=True)
class ChunkedDocument:
    doc_id: str
    output_chunks_path: str
    chunk_count: int


@dataclass(frozen=True)
class ChunkResult:
    chunked_documents: list[ChunkedDocument]
    chunk_count: int


def chunk_all_blocks(settings: Settings) -> ChunkResult:
    """Build embedding-ready chunk JSONL files from block sidecar artifacts."""
    blocks_dir = settings.processed_data_dir / "blocks"
    settings.chunks_dir.mkdir(parents=True, exist_ok=True)

    chunked_documents: list[ChunkedDocument] = []
    for blocks_path in sorted(blocks_dir.glob("*.jsonl")):
        blocks = _read_blocks(blocks_path)
        if not blocks:
            continue

        chunks = chunk_blocks(
            blocks,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )
        output_path = settings.chunks_dir / blocks_path.name
        _write_chunks(output_path, chunks)
        chunked_documents.append(
            ChunkedDocument(
                doc_id=blocks[0].doc_id,
                output_chunks_path=output_path.as_posix(),
                chunk_count=len(chunks),
            )
        )

    _remove_orphaned_chunk_files(settings.chunks_dir, chunked_documents)
    return ChunkResult(
        chunked_documents=chunked_documents,
        chunk_count=sum(document.chunk_count for document in chunked_documents),
    )


def chunk_blocks(
    blocks: list[SourceBlockRecord],
    *,
    chunk_size: int,
    chunk_overlap: int,
) -> list[ChunkArtifact]:
    """Split blocks with LangChain Markdown and token-aware recursive splitters."""
    markdown_text = _blocks_to_markdown(blocks)
    section_context = _build_section_context(blocks)
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=HEADERS_TO_SPLIT_ON,
        strip_headers=False,
    )
    recursive_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    chunks: list[ChunkArtifact] = []
    for header_document in header_splitter.split_text(markdown_text):
        section_text = header_document.page_content.strip()
        if not section_text:
            continue

        section_path = _section_path_from_metadata(header_document.metadata)
        section_blocks = _matching_blocks(blocks, section_path)
        if not section_blocks:
            section_blocks = blocks

        split_documents = recursive_splitter.create_documents([section_text])
        for split_document in split_documents:
            chunk_text = _add_table_context_to_chunk(
                split_document.page_content.strip(),
                section_path,
                section_context,
            )
            if not chunk_text:
                continue
            chunk_blocks_for_metadata = _blocks_present_in_text(chunk_text, blocks)
            if not chunk_blocks_for_metadata:
                chunk_blocks_for_metadata = section_blocks
            chunks.append(
                _build_chunk(
                    chunk_blocks_for_metadata,
                    chunk_text,
                    "markdown_header_recursive_tiktoken",
                    len(chunks) + 1,
                    recursive_splitter,
                )
            )

    return chunks


def _blocks_to_markdown(blocks: list[SourceBlockRecord]) -> str:
    sections: list[str] = []
    section_context = _build_section_context(blocks)
    previous_section: str | None = None

    for block in blocks:
        text = block.text.strip()
        if not text:
            continue

        if block.section_path and block.section_path != previous_section:
            context = section_context.get(block.section_path)
            if text.startswith("#"):
                sections.append(text)
                if context and context != text:
                    sections.append(context)
                previous_section = block.section_path
                continue
            else:
                sections.append(f"## {block.section_path}")
            previous_section = block.section_path

        if text == section_context.get(block.section_path or ""):
            continue

        sections.append(text)

    return "\n\n".join(sections)


def _build_chunk(
    blocks: list[SourceBlockRecord],
    text: str,
    chunk_strategy: str,
    order: int,
    splitter: RecursiveCharacterTextSplitter,
) -> ChunkArtifact:
    first_block = blocks[0]
    pages = sorted({block.page for block in blocks if block.page is not None})
    sheets = sorted({block.sheet for block in blocks if block.sheet is not None})
    section_paths = [block.section_path for block in blocks if block.section_path]
    section_path = section_paths[0] if section_paths else None

    return ChunkArtifact(
        chunk_id=f"{first_block.doc_id}:chunk:{order:05d}",
        doc_id=first_block.doc_id,
        source_path=first_block.source_path,
        doc_type=first_block.doc_type,
        title=first_block.title,
        text=text,
        source_block_ids=[block.block_id for block in blocks],
        section_path=section_path,
        pages=pages,
        sheets=sheets,
        chunk_strategy=chunk_strategy,
        token_count=splitter._length_function(text),
        order=order,
        metadata=_merge_metadata(blocks),
    )


def _section_path_from_metadata(metadata: dict) -> str | None:
    header_values = [
        metadata[key]
        for _, key in HEADERS_TO_SPLIT_ON
        if key in metadata and metadata[key]
    ]
    if not header_values:
        return None
    return str(header_values[-1])


def _matching_blocks(
    blocks: list[SourceBlockRecord],
    section_path: str | None,
) -> list[SourceBlockRecord]:
    if section_path is None:
        return [block for block in blocks if block.section_path is None]
    return [block for block in blocks if block.section_path == section_path]


def _blocks_present_in_text(
    chunk_text: str,
    blocks: list[SourceBlockRecord],
) -> list[SourceBlockRecord]:
    normalized_chunk = _normalize_for_matching(chunk_text)
    matched_blocks: list[SourceBlockRecord] = []
    for block in blocks:
        normalized_block = _normalize_for_matching(block.text)
        if normalized_block and normalized_block in normalized_chunk:
            matched_blocks.append(block)
    return matched_blocks


def _normalize_for_matching(text: str) -> str:
    return " ".join(text.split())


def _build_section_context(blocks: list[SourceBlockRecord]) -> dict[str, str]:
    context: dict[str, str] = {}
    for block in blocks:
        if block.section_path is None:
            continue
        if block.block_type == "table_row" and block.section_path not in context:
            # Spreadsheet continuation chunks need the header row to stay meaningful.
            context[block.section_path] = block.text
    return context


def _add_table_context_to_chunk(
    chunk_text: str,
    section_path: str | None,
    section_context: dict[str, str],
) -> str:
    if section_path is None:
        return chunk_text

    context = section_context.get(section_path)
    if context is None or context in chunk_text:
        return chunk_text

    if not chunk_text.startswith("#"):
        return f"## {section_path}\n\n{context}\n\n{chunk_text}".strip()
    return f"{chunk_text}\n\n{context}".strip()


def _read_blocks(blocks_path: Path) -> list[SourceBlockRecord]:
    blocks: list[SourceBlockRecord] = []
    for line in blocks_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            blocks.append(SourceBlockRecord(**json.loads(line)))
    return sorted(blocks, key=lambda block: block.order)


def _write_chunks(output_path: Path, chunks: Iterable[ChunkArtifact]) -> None:
    rows = [json.dumps(asdict(chunk), ensure_ascii=True) for chunk in chunks]
    output_path.write_text("\n".join(rows) + ("\n" if rows else ""), encoding="utf-8")


def _remove_orphaned_chunk_files(
    chunks_dir: Path,
    chunked_documents: Iterable[ChunkedDocument],
) -> None:
    expected_paths = {
        Path(document.output_chunks_path).resolve() for document in chunked_documents
    }
    for chunk_path in chunks_dir.glob("*.jsonl"):
        if chunk_path.resolve() not in expected_paths:
            chunk_path.unlink()


def _merge_metadata(blocks: list[SourceBlockRecord]) -> dict:
    metadata: dict = {}
    table_indexes = [
        block.metadata.get("table_index_on_page")
        for block in blocks
        if block.metadata.get("table_index_on_page") is not None
    ]
    if table_indexes:
        metadata["table_indexes_on_page"] = table_indexes
    return metadata
