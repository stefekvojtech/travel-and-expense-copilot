from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Iterable

from app.retrieval.rerank import RerankedChunk
from app.retrieval.vector_store import RetrievedChunk

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
    sheet_label: str | None
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
    max_blocks_per_section: int = 1,
) -> AssembledContext:
    """Convert retrieved chunks into citation-ready evidence for answer generation."""
    selected_chunks = _select_diverse_chunks(
        retrieved_chunks,
        max_blocks=max_blocks,
        max_blocks_per_section=max_blocks_per_section,
    )
    evidence_blocks: list[EvidenceBlock] = []
    for chunk in selected_chunks:
        evidence_blocks.append(_build_evidence_block(chunk, len(evidence_blocks) + 1))

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
) -> EvidenceBlock:
    return EvidenceBlock(
        citation_id=f"[{citation_number}]",
        chunk_id=chunk.chunk_id,
        source_path=chunk.source_path,
        doc_type=_optional_str(chunk.metadata.get("doc_type")),
        title=_optional_str(chunk.metadata.get("title")),
        section_path=chunk.section_path,
        page_label=_join_json_list(chunk.metadata.get("pages")),
        sheet_label=_join_json_list(chunk.metadata.get("sheets")),
        row_number=_optional_int(chunk.metadata.get("metadata_row_number")),
        cosine_distance=chunk.cosine_distance,
        approximate_cosine_similarity=chunk.approximate_cosine_similarity,
        rerank_score=chunk.rerank_score if isinstance(chunk, RerankedChunk) else None,
        text=chunk.text.strip(),
    )


def _format_context_text(evidence_blocks: list[EvidenceBlock]) -> str:
    parts: list[str] = []
    for block in evidence_blocks:
        parts.append(
            "\n".join(
                line
                for line in [
                    f"{block.citation_id} {block.title or 'Untitled source'}",
                    f"source_path: {block.source_path}",
                    f"chunk_id: {block.chunk_id}",
                    f"doc_type: {block.doc_type}",
                    f"section_path: {block.section_path}",
                    f"pages: {block.page_label}" if block.page_label else None,
                    f"sheets: {block.sheet_label}" if block.sheet_label else None,
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
        )
    return "\n\n---\n\n".join(parts)


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


def _optional_str(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _optional_int(value: Any) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None
