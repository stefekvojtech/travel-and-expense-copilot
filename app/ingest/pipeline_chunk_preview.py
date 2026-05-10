"""Render production chunk JSONL artifacts as readable Markdown previews."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from app.core.config import ROOT_DIR, Settings
from app.ingest.artifacts import ChunkArtifact


@dataclass(frozen=True)
class ChunkPreviewDocument:
    doc_id: str
    output_preview_path: str
    chunk_count: int


@dataclass(frozen=True)
class ChunkPreviewResult:
    previewed_documents: list[ChunkPreviewDocument]
    chunk_count: int
    output_dir: str


def preview_all_chunks(
    settings: Settings,
    *,
    output_dir: Path | None = None,
) -> ChunkPreviewResult:
    """Write human-readable Markdown previews for every chunk JSONL file."""
    preview_dir = output_dir or settings.processed_data_dir / "chunks_preview"
    preview_dir.mkdir(parents=True, exist_ok=True)

    previewed_documents: list[ChunkPreviewDocument] = []
    for chunks_path in sorted(settings.chunks_dir.glob("*.jsonl")):
        chunks = _read_chunks(chunks_path)
        if not chunks:
            continue

        output_path = preview_dir / f"{chunks[0].doc_id}.md"
        _write_text_if_changed(output_path, _chunks_preview_markdown(chunks))
        previewed_documents.append(
            ChunkPreviewDocument(
                doc_id=chunks[0].doc_id,
                output_preview_path=_project_relative_path(output_path),
                chunk_count=len(chunks),
            )
        )

    _remove_orphaned_preview_files(preview_dir, previewed_documents)
    return ChunkPreviewResult(
        previewed_documents=previewed_documents,
        chunk_count=sum(document.chunk_count for document in previewed_documents),
        output_dir=_project_relative_path(preview_dir),
    )


def _read_chunks(chunks_path: Path) -> list[ChunkArtifact]:
    chunks: list[ChunkArtifact] = []
    for line in chunks_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            chunks.append(ChunkArtifact(**json.loads(line)))
    return sorted(chunks, key=lambda chunk: chunk.order)


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
        page_text = f" pages={_format_int_list(chunk.pages)}" if chunk.pages else ""
        sheet_text = f" sheets={_format_str_list(chunk.sheets)}" if chunk.sheets else ""
        section_text = f" section={chunk.section_path!r}" if chunk.section_path else ""
        lines.extend(
            [
                f"### {chunk.chunk_id}",
                "",
                f"- order: `{chunk.order}`",
                f"- strategy: `{chunk.chunk_strategy}`",
                f"- tokens: `{chunk.token_count}`{page_text}{sheet_text}{section_text}",
                f"- source_block_ids: `{json.dumps(chunk.source_block_ids, ensure_ascii=True)}`",
                f"- metadata: `{json.dumps(chunk.metadata, ensure_ascii=True)}`",
                "",
                "```text",
                chunk.text,
                "```",
                "",
            ]
        )
    return "\n".join(lines).strip() + "\n"


def _format_int_list(values: list[int]) -> str:
    return "[" + ", ".join(str(value) for value in values) + "]"


def _format_str_list(values: list[str]) -> str:
    return "[" + ", ".join(repr(value) for value in values) + "]"


def _write_text_if_changed(output_path: Path, text: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists() and output_path.read_text(encoding="utf-8") == text:
        return
    output_path.write_text(text, encoding="utf-8")


def _remove_orphaned_preview_files(
    preview_dir: Path,
    previewed_documents: Iterable[ChunkPreviewDocument],
) -> None:
    expected_paths = {
        _resolve_project_path(document.output_preview_path).resolve()
        for document in previewed_documents
    }
    for preview_path in preview_dir.glob("*.md"):
        if preview_path.resolve() not in expected_paths:
            preview_path.unlink()


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
