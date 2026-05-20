"""Assemble retrieved chunks into citation-ready evidence context.

This module selects diverse retrieved or reranked chunks, trims evidence to a
token budget, formats source metadata, and produces the context text that a
future grounded answer generator can cite.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from typing import Any, Iterable

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.retrieval.step01_search_chunks import RetrievedChunk
from app.retrieval.step02_rerank_chunks import RerankedChunk

ContextCandidate = RetrievedChunk | RerankedChunk


@dataclass(frozen=True)
class EvidenceBlock:
    citation_id: str
    chunk_id: str | None
    source_path: str | None
    doc_type: str | None
    title: str | None
    section_path: str | None
    page_label: str | None
    row_number: int | None
    cosine_distance: float
    approximate_cosine_similarity: float
    rerank_score: float | None
    text: str


@dataclass(frozen=True)
class AssembledContext:
    evidence_blocks: list[EvidenceBlock]
    context_text: str


def assemble_context(
    retrieved_chunks: Iterable[ContextCandidate],
    *,
    max_blocks: int,
    max_total_tokens: int,
    max_block_tokens: int,
    max_blocks_per_section: int = 1,
) -> AssembledContext:
    """Convert retrieved chunks into citation-ready evidence for answer generation."""
    selected_chunks = _select_diverse_chunks(
        retrieved_chunks,
        max_blocks=max_blocks,
        max_blocks_per_section=max_blocks_per_section,
    )
    evidence_blocks: list[EvidenceBlock] = []
    total_tokens = 0
    for chunk in selected_chunks:
        remaining_tokens = max_total_tokens - total_tokens
        if remaining_tokens <= 0:
            break

        evidence_block = _build_budgeted_evidence_block(
            chunk,
            len(evidence_blocks) + 1,
            max_block_tokens=min(max_block_tokens, remaining_tokens),
        )
        block_tokens = _token_length(_format_context_block(evidence_block))
        if block_tokens > remaining_tokens:
            continue

        evidence_blocks.append(evidence_block)
        total_tokens += block_tokens

    return AssembledContext(
        evidence_blocks=evidence_blocks,
        context_text=_format_context_text(evidence_blocks),
    )


def _select_diverse_chunks(
    retrieved_chunks: Iterable[ContextCandidate],
    *,
    max_blocks: int,
    max_blocks_per_section: int,
) -> list[ContextCandidate]:
    selected: list[ContextCandidate] = []
    overflow: list[ContextCandidate] = []
    seen_chunk_ids: set[str] = set()
    section_counts: dict[tuple[str | None, str | None], int] = {}

    for chunk in retrieved_chunks:
        chunk_id = chunk.chunk_id
        if chunk_id is not None and chunk_id in seen_chunk_ids:
            continue
        if chunk_id is not None:
            seen_chunk_ids.add(chunk_id)

        section_key = (chunk.source_path, chunk.section_path)
        section_count = section_counts.get(section_key, 0)
        if section_count >= max_blocks_per_section:
            overflow.append(chunk)
            continue

        selected.append(chunk)
        section_counts[section_key] = section_count + 1
        if len(selected) >= max_blocks:
            break

    for chunk in overflow:
        if len(selected) >= max_blocks:
            break
        selected.append(chunk)

    return selected[:max_blocks]


def _build_evidence_block(
    chunk: ContextCandidate,
    citation_number: int,
    *,
    text: str,
) -> EvidenceBlock:
    return EvidenceBlock(
        citation_id=f"[{citation_number}]",
        chunk_id=chunk.chunk_id,
        source_path=chunk.source_path,
        doc_type=_optional_str(chunk.metadata.get("doc_type")),
        title=_optional_str(chunk.metadata.get("title")),
        section_path=chunk.section_path,
        page_label=_metadata_label(chunk.metadata, "page", "pages"),
        row_number=_optional_int(
            chunk.metadata.get("row_number")
            or chunk.metadata.get("metadata_row_number")
        ),
        cosine_distance=chunk.cosine_distance,
        approximate_cosine_similarity=chunk.approximate_cosine_similarity,
        rerank_score=chunk.rerank_score if isinstance(chunk, RerankedChunk) else None,
        text=text,
    )


def _build_budgeted_evidence_block(
    chunk: ContextCandidate,
    citation_number: int,
    *,
    max_block_tokens: int,
) -> EvidenceBlock:
    """Build an evidence block whose formatted output fits the block token budget."""
    empty_block = _build_evidence_block(chunk, citation_number, text="")
    metadata_tokens = _token_length(_format_context_block(empty_block))
    max_text_tokens = max(max_block_tokens - metadata_tokens, 0)

    block = replace(
        empty_block,
        text=_trim_text_to_token_budget(
            chunk.text.strip(),
            max_text_tokens=max_text_tokens,
        ),
    )

    # The trim marker itself costs tokens, so tighten once more if needed.
    while _token_length(_format_context_block(block)) > max_block_tokens and block.text:
        overflow = _token_length(_format_context_block(block)) - max_block_tokens
        max_text_tokens = max(max_text_tokens - overflow - 1, 0)
        block = replace(
            empty_block,
            text=_trim_text_to_token_budget(
                chunk.text.strip(),
                max_text_tokens=max_text_tokens,
            ),
        )

    return block


def _format_context_text(evidence_blocks: list[EvidenceBlock]) -> str:
    return "\n\n---\n\n".join(
        _format_context_block(block)
        for block in evidence_blocks
    )


def _format_context_block(block: EvidenceBlock) -> str:
    return "\n".join(
        line
        for line in [
            f"{block.citation_id} {block.title or 'Untitled source'}",
            f"source_path: {block.source_path}",
            f"chunk_id: {block.chunk_id}",
            f"doc_type: {block.doc_type}",
            f"section_path: {block.section_path}",
            f"page: {block.page_label}" if block.page_label else None,
            f"row_number: {block.row_number}"
            if block.row_number is not None
            else None,
            (
                "retrieval_score: "
                f"cosine_distance={block.cosine_distance:.4f}, "
                f"approx_similarity={block.approximate_cosine_similarity:.4f}"
            ),
            f"rerank_score: {block.rerank_score:.4f}"
            if block.rerank_score is not None
            else None,
            "content:",
            block.text,
        ]
        if line is not None
    )


def _trim_text_to_token_budget(text: str, *, max_text_tokens: int) -> str:
    if max_text_tokens <= 0:
        return ""
    if _token_length(text) <= max_text_tokens:
        return text

    trim_marker = "\n\n[Trimmed to fit context budget.]"
    trim_marker_tokens = _token_length(trim_marker)
    if trim_marker_tokens >= max_text_tokens:
        return ""

    text_budget = max_text_tokens - trim_marker_tokens
    split_documents = _token_splitter(
        chunk_size=text_budget,
        chunk_overlap=0,
    ).create_documents([text])
    if not split_documents:
        return ""

    trimmed_text = split_documents[0].page_content.strip()
    return f"{trimmed_text}{trim_marker}"


def _token_length(text: str) -> int:
    return _token_splitter()._length_function(text)


def _token_splitter(
    *,
    chunk_size: int = 1000,
    chunk_overlap: int = 0,
) -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )


def _join_json_list(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, list):
        values = value
    elif isinstance(value, str):
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError:
            return value or None
        values = decoded if isinstance(decoded, list) else [decoded]
    else:
        values = [value]

    labels = [str(item) for item in values if item not in (None, "")]
    return ", ".join(labels) if labels else None


def _metadata_label(metadata: dict[str, Any], key: str, legacy_key: str) -> str | None:
    value = metadata.get(key)
    if value not in (None, ""):
        return str(value)
    return _join_json_list(metadata.get(legacy_key))


def _optional_str(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _optional_int(value: Any) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None
