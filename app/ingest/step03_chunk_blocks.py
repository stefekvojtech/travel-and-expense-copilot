"""Convert normalized block artifacts into embedding-ready chunk artifacts.

This stage reads `02_normalized_blocks`, writes `03_chunks`, and writes matching
`03_chunks_preview` Markdown files. It uses LangChain Markdown and recursive
token-aware splitters, while preserving production behavior for XLSX row chunks,
table header context, continuation chunks, and citation-oriented chunk metadata.
"""

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
from app.ingest.artifact_paths import (
    chunk_previews_dir,
    chunks_dir,
    normalized_blocks_dir,
    reset_artifact_dir,
    write_text_if_changed,
)
from app.ingest.artifacts import BlockArtifact, ChunkArtifact, block_artifact_from_dict


HEADERS_TO_SPLIT_ON = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
    ("####", "Header 4"),
    ("#####", "Header 5"),
    ("######", "Header 6"),
]


@dataclass(frozen=True)
class BlockSpan:
    block: BlockArtifact
    start: int
    end: int


@dataclass(frozen=True)
class MarkdownAssembly:
    text: str
    spans: list[BlockSpan]


@dataclass(frozen=True)
class PreparedChunkText:
    text: str
    mapped_text: str
    added_context: bool


@dataclass(frozen=True)
class ChunkedDocument:
    doc_id: str
    chunk_count: int


@dataclass(frozen=True)
class ChunkResult:
    chunked_documents: list[ChunkedDocument]
    chunk_count: int


def chunk_all_blocks(settings: Settings) -> ChunkResult:
    """Build embedding-ready chunk JSONL and preview files from block artifacts."""
    blocks_dir = normalized_blocks_dir(settings)
    output_dir = chunks_dir(settings)
    preview_dir = chunk_previews_dir(settings)
    reset_artifact_dir(output_dir, pattern="*.jsonl")
    reset_artifact_dir(preview_dir, pattern="*.md")

    chunked_documents: list[ChunkedDocument] = []
    for blocks_path in sorted(blocks_dir.glob("*.jsonl")):
        blocks = _read_blocks(blocks_path)
        if not blocks:
            continue

        chunks = chunk_blocks(
            blocks,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            max_chunk_tokens=settings.max_chunk_tokens,
        )
        output_path = output_dir / blocks_path.name
        preview_path = preview_dir / f"{blocks[0].doc_id}.md"
        _write_chunks(output_path, chunks)
        write_text_if_changed(preview_path, _chunks_preview_markdown(chunks))
        chunked_documents.append(
            ChunkedDocument(
                doc_id=blocks[0].doc_id,
                chunk_count=len(chunks),
            )
        )

    return ChunkResult(
        chunked_documents=chunked_documents,
        chunk_count=sum(document.chunk_count for document in chunked_documents),
    )


def chunk_blocks(
    blocks: list[BlockArtifact],
    *,
    chunk_size: int,
    chunk_overlap: int,
    max_chunk_tokens: int,
) -> list[ChunkArtifact]:
    """Split blocks with LangChain Markdown and token-aware recursive splitters."""
    _validate_chunk_settings(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    if blocks and all(block.doc_type == "xlsx" for block in blocks):
        chunks = _chunk_xlsx_rows(
            blocks,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        _validate_chunks_within_max_tokens(chunks, max_chunk_tokens=max_chunk_tokens)
        return chunks

    assembly = _assemble_markdown_with_spans(blocks)
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
    search_start = 0
    for header_document in header_splitter.split_text(assembly.text):
        section_text = header_document.page_content.strip()
        if not section_text:
            continue

        section_path = _section_path_from_metadata(header_document.metadata)
        section_token_count = recursive_splitter._length_function(section_text)
        section_was_recursively_split = section_token_count > chunk_size
        section_start, section_end = _locate_text_span(
            assembly.text,
            section_text,
            start=search_start,
        )
        search_start = section_start

        split_documents = recursive_splitter.create_documents([section_text])
        split_search_start = section_start
        for split_document in split_documents:
            original_chunk_text = split_document.page_content.strip()
            mapped_chunk_text = _strip_added_table_context(
                original_chunk_text,
                section_path,
                section_context,
            )
            original_chunk_start, original_chunk_end = _locate_text_span(
                assembly.text,
                mapped_chunk_text,
                start=split_search_start,
                end=section_end,
            )
            split_search_start = original_chunk_start

            chunk_parts = _chunk_texts_with_sized_table_context(
                original_chunk_text,
                section_path=section_path,
                section_context=section_context,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )

            for prepared_chunk in chunk_parts:
                if not prepared_chunk.text:
                    continue

                chunk_start, chunk_end = _locate_text_span(
                    assembly.text,
                    prepared_chunk.mapped_text,
                    start=original_chunk_start,
                    end=original_chunk_end,
                )
                chunk_blocks_for_metadata = _blocks_for_span(
                    assembly.spans,
                    chunk_start,
                    chunk_end,
                )
                if prepared_chunk.added_context:
                    chunk_blocks_for_metadata = _merge_blocks_preserving_order(
                        _context_blocks(blocks, section_path),
                        chunk_blocks_for_metadata,
                    )
                if not chunk_blocks_for_metadata:
                    chunk_blocks_for_metadata = _blocks_for_span(
                        assembly.spans,
                        section_start,
                        section_end,
                    )
                chunks.append(
                    _build_chunk(
                        chunk_blocks_for_metadata,
                        prepared_chunk.text,
                        _chunk_strategy(
                            section_path=section_path,
                            section_was_recursively_split=section_was_recursively_split,
                            added_context=prepared_chunk.added_context,
                        ),
                        len(chunks) + 1,
                        recursive_splitter,
                    )
                )

    _validate_chunks_within_max_tokens(chunks, max_chunk_tokens=max_chunk_tokens)
    return chunks


def _validate_chunk_settings(
    *,
    chunk_size: int,
    chunk_overlap: int,
) -> None:
    if chunk_size < 1:
        raise ValueError("CHUNK_SIZE must be greater than zero.")

    if chunk_overlap >= chunk_size:
        raise ValueError("CHUNK_OVERLAP must be smaller than CHUNK_SIZE.")


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
            "Chunking produced chunks above MAX_CHUNK_TOKENS="
            f"{max_chunk_tokens}: {', '.join(oversized_chunks)}"
        )


def _chunk_xlsx_rows(
    blocks: list[BlockArtifact],
    *,
    chunk_size: int,
    chunk_overlap: int,
) -> list[ChunkArtifact]:
    """Create retrieval chunks from spreadsheet rows rather than whole sheets."""
    recursive_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    row_blocks = [block for block in blocks if block.block_type == "table_row"]
    chunks: list[ChunkArtifact] = []
    for row_block in row_blocks:
        row_token_count = recursive_splitter._length_function(row_block.text)
        if row_token_count <= chunk_size:
            chunks.append(
                _build_chunk(
                    [row_block],
                    row_block.text,
                    "xlsx_row_as_chunk",
                    len(chunks) + 1,
                    recursive_splitter,
                )
            )
            continue

        for split_document in recursive_splitter.create_documents([row_block.text]):
            split_text = split_document.page_content.strip()
            if not split_text:
                continue
            chunks.append(
                _build_chunk(
                    [row_block],
                    split_text,
                    "xlsx_row+recursive_tiktoken",
                    len(chunks) + 1,
                    recursive_splitter,
                )
            )

    return chunks


def _chunk_strategy(
    *,
    section_path: str | None,
    section_was_recursively_split: bool,
    added_context: bool,
) -> str:
    parts: list[str] = []
    if section_path is not None:
        parts.append("markdown_header")
    else:
        parts.append("plain_text")

    if section_was_recursively_split:
        parts.append("recursive_tiktoken")
    else:
        parts.append("section_as_chunk")

    if added_context:
        parts.append("table_context")

    return "+".join(parts)


def _assemble_markdown_with_spans(blocks: list[BlockArtifact]) -> MarkdownAssembly:
    text_parts: list[str] = []
    spans: list[BlockSpan] = []
    section_context = _build_section_context(blocks)
    previous_section: str | None = None

    for block in blocks:
        text = block.text.strip()
        if not text:
            continue

        if block.section_path and block.section_path != previous_section:
            context = section_context.get(block.section_path)
            if text.startswith("#"):
                _append_text_part(text_parts, spans, text, block)
                if context and context != text:
                    _append_text_part(
                        text_parts,
                        spans,
                        context,
                        _context_block(blocks, block.section_path),
                    )
                previous_section = block.section_path
                continue
            else:
                _append_text_part(text_parts, spans, f"## {block.section_path}", None)
            previous_section = block.section_path

        if text == section_context.get(block.section_path or ""):
            continue

        _append_text_part(text_parts, spans, text, block)

    return MarkdownAssembly(text="\n\n".join(text_parts), spans=spans)


def _append_text_part(
    text_parts: list[str],
    spans: list[BlockSpan],
    text: str,
    block: BlockArtifact | None,
) -> None:
    if not text:
        return

    start = sum(len(part) for part in text_parts)
    if text_parts:
        start += 2 * len(text_parts)
    text_parts.append(text)
    end = start + len(text)
    if block is not None:
        spans.append(BlockSpan(block=block, start=start, end=end))


def _build_chunk(
    blocks: list[BlockArtifact],
    text: str,
    chunk_strategy: str,
    order: int,
    splitter: RecursiveCharacterTextSplitter,
) -> ChunkArtifact:
    first_block = blocks[0]
    pages = sorted({block.page for block in blocks if block.page is not None})
    section_paths = [block.section_path for block in blocks if block.section_path]
    section_path = section_paths[0] if section_paths else None

    return ChunkArtifact(
        chunk_id=f"{first_block.doc_id}:chunk:{order:05d}",
        doc_id=first_block.doc_id,
        source_path=first_block.source_path,
        doc_type=first_block.doc_type,
        title=first_block.title,
        text=text,
        section_path=section_path,
        page=pages[0] if pages else None,
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


def _build_section_context(blocks: list[BlockArtifact]) -> dict[str, str]:
    context: dict[str, str] = {}
    for block in blocks:
        if block.section_path is None:
            continue
        if block.block_type == "table_header" and block.section_path not in context:
            # Spreadsheet continuation chunks need the header row to stay meaningful.
            context[block.section_path] = block.text
    return context


def _chunk_texts_with_sized_table_context(
    chunk_text: str,
    *,
    section_path: str | None,
    section_context: dict[str, str],
    chunk_size: int,
    chunk_overlap: int,
) -> list[PreparedChunkText]:
    if not _needs_table_context(chunk_text, section_path, section_context):
        return [
            PreparedChunkText(
                text=chunk_text,
                mapped_text=_strip_added_table_context(
                    chunk_text,
                    section_path,
                    section_context,
                ),
                added_context=False,
            )
        ]

    prefix = _table_context_prefix(section_path, section_context)
    if prefix is None:
        return [PreparedChunkText(text=chunk_text, mapped_text=chunk_text, added_context=False)]

    prefix_token_count = _token_length(prefix)
    available_chunk_size = chunk_size - prefix_token_count
    if available_chunk_size <= 0:
        raise ValueError("Table context is larger than the configured chunk size.")

    if _token_length(f"{prefix}{chunk_text}") <= chunk_size:
        return [
            PreparedChunkText(
                text=f"{prefix}{chunk_text}",
                mapped_text=chunk_text,
                added_context=True,
            )
        ]

    content_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=available_chunk_size,
        chunk_overlap=min(chunk_overlap, max(0, available_chunk_size // 4)),
    )
    prepared_chunks: list[PreparedChunkText] = []
    for document in content_splitter.create_documents([chunk_text]):
        mapped_text = document.page_content.strip()
        if not mapped_text:
            continue
        prepared_chunks.append(
            PreparedChunkText(
                text=f"{prefix}{mapped_text}",
                mapped_text=mapped_text,
                added_context=True,
            )
        )
    return prepared_chunks


def _needs_table_context(
    chunk_text: str,
    section_path: str | None,
    section_context: dict[str, str],
) -> bool:
    if section_path is None:
        return False
    context = section_context.get(section_path)
    return context is not None and context not in chunk_text


def _table_context_prefix(
    section_path: str | None,
    section_context: dict[str, str],
) -> str | None:
    if section_path is None:
        return None
    context = section_context.get(section_path)
    if context is None:
        return None
    return f"## {section_path}\n\n{context}\n\n"


def _token_length(text: str) -> int:
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base"
    )
    return splitter._length_function(text)


def _strip_added_table_context(
    chunk_text: str,
    section_path: str | None,
    section_context: dict[str, str],
) -> str:
    if section_path is None:
        return chunk_text

    context = section_context.get(section_path)
    if context is None:
        return chunk_text

    stripped = chunk_text.strip()
    section_heading = f"## {section_path}"
    if stripped.startswith(section_heading):
        stripped = stripped[len(section_heading):].strip()
    if stripped.startswith(context):
        stripped = stripped[len(context):].strip()
    if stripped.endswith(context):
        stripped = stripped[: -len(context)].strip()
    return stripped or chunk_text


def _locate_text_span(
    full_text: str,
    target_text: str,
    *,
    start: int,
    end: int | None = None,
) -> tuple[int, int]:
    search_end = len(full_text) if end is None else end
    index = full_text.find(target_text, start, search_end)
    if index == -1:
        normalized = _locate_normalized_span(
            full_text,
            target_text,
            start=start,
            end=search_end,
        )
        if normalized is None:
            raise ValueError("Could not map chunk text back to assembled source text.")
        return normalized
    return index, index + len(target_text)


def _locate_normalized_span(
    full_text: str,
    target_text: str,
    *,
    start: int,
    end: int,
) -> tuple[int, int] | None:
    full_indexes: list[int] = []
    target_chars: list[str] = []
    full_chars: list[str] = []

    for index, char in enumerate(full_text):
        if char.isspace():
            continue
        full_indexes.append(index)
        full_chars.append(char)
    for char in target_text:
        if not char.isspace():
            target_chars.append(char)

    normalized_full = "".join(full_chars)
    normalized_target = "".join(target_chars)
    normalized_start = next(
        (idx for idx, original in enumerate(full_indexes) if original >= start),
        0,
    )
    normalized_end = next(
        (
            idx
            for idx, original in enumerate(full_indexes)
            if original >= end
        ),
        len(full_indexes),
    )

    match_index = normalized_full.find(
        normalized_target,
        normalized_start,
        normalized_end,
    )
    if match_index == -1:
        return None

    original_start = full_indexes[match_index]
    original_end = full_indexes[match_index + len(normalized_target) - 1] + 1
    return original_start, original_end


def _blocks_for_span(
    spans: list[BlockSpan],
    start: int,
    end: int,
) -> list[BlockArtifact]:
    return [
        span.block
        for span in spans
        if span.start < end and span.end > start
    ]


def _context_blocks(
    blocks: list[BlockArtifact],
    section_path: str | None,
) -> list[BlockArtifact]:
    block = _context_block(blocks, section_path)
    return [block] if block is not None else []


def _context_block(
    blocks: list[BlockArtifact],
    section_path: str | None,
) -> BlockArtifact | None:
    if section_path is None:
        return None
    for block in blocks:
        if block.section_path == section_path and block.block_type == "table_header":
            return block
    return None


def _merge_blocks_preserving_order(
    first: list[BlockArtifact],
    second: list[BlockArtifact],
) -> list[BlockArtifact]:
    by_id = {block.block_id: block for block in [*first, *second]}
    return sorted(by_id.values(), key=lambda block: block.order)


def _read_blocks(blocks_path: Path) -> list[BlockArtifact]:
    blocks: list[BlockArtifact] = []
    for line in blocks_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            blocks.append(block_artifact_from_dict(json.loads(line)))
    return sorted(blocks, key=lambda block: block.order)


def _write_chunks(output_path: Path, chunks: Iterable[ChunkArtifact]) -> None:
    rows = [json.dumps(asdict(chunk), ensure_ascii=True) for chunk in chunks]
    write_text_if_changed(output_path, "\n".join(rows) + ("\n" if rows else ""))


def _chunks_preview_markdown(chunks: list[ChunkArtifact]) -> str:
    first_chunk = chunks[0]
    lines = [
        f"# Chunk Preview: {first_chunk.title}",
        "",
        f"- doc_id: `{first_chunk.doc_id}`",
        f"- source_path: `{first_chunk.source_path}`",
        f"- doc_type: `{first_chunk.doc_type}`",
        f"- chunks: `{len(chunks)}`",
        "",
        "## Chunks",
        "",
    ]
    for chunk in chunks:
        page_text = f" page={chunk.page}" if chunk.page is not None else ""
        section_text = f" section={chunk.section_path!r}" if chunk.section_path else ""
        lines.extend(
            [
                f"### {chunk.chunk_id}",
                "",
                f"- order: `{chunk.order}`",
                f"- strategy: `{chunk.chunk_strategy}`",
                f"- tokens: `{chunk.token_count}`{page_text}{section_text}",
                f"- metadata: `{json.dumps(chunk.metadata, ensure_ascii=True)}`",
                "",
                "```text",
                chunk.text,
                "```",
                "",
            ]
        )
    return "\n".join(lines).strip() + "\n"


def _merge_metadata(blocks: list[BlockArtifact]) -> dict:
    metadata: dict = {}
    table_indexes = [
        block.metadata.get("table_index_on_page")
        for block in blocks
        if block.metadata.get("table_index_on_page") is not None
    ]
    if table_indexes:
        metadata["table_indexes_on_page"] = table_indexes
    for key in ("row_number",):
        values = [
            block.metadata.get(key)
            for block in blocks
            if block.metadata.get(key) is not None
        ]
        unique_values = list(dict.fromkeys(values))
        if len(unique_values) == 1:
            metadata[key] = unique_values[0]
        elif unique_values:
            metadata[f"{key}s"] = unique_values
    return metadata
