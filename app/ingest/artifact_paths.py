"""Central names and path helpers for generated ingestion artifacts."""

from __future__ import annotations

from pathlib import Path

from app.core.config import ROOT_DIR, Settings


LOADED_DOCUMENTS_DIR_NAME = "01_loaded_documents"
LOADED_DOCUMENT_PREVIEWS_DIR_NAME = "01_loaded_documents_preview"
NORMALIZED_BLOCKS_DIR_NAME = "02_normalized_blocks"
NORMALIZED_BLOCK_PREVIEWS_DIR_NAME = "02_normalized_blocks_preview"
CHUNKS_DIR_NAME = "03_chunks"
CHUNK_PREVIEWS_DIR_NAME = "03_chunks_preview"
REPORT_FILENAME = "report.md"


def loaded_documents_dir(settings: Settings) -> Path:
    return settings.processed_data_dir / LOADED_DOCUMENTS_DIR_NAME


def loaded_document_previews_dir(settings: Settings) -> Path:
    return settings.processed_data_dir / LOADED_DOCUMENT_PREVIEWS_DIR_NAME


def normalized_blocks_dir(settings: Settings) -> Path:
    return settings.processed_data_dir / NORMALIZED_BLOCKS_DIR_NAME


def normalized_block_previews_dir(settings: Settings) -> Path:
    return settings.processed_data_dir / NORMALIZED_BLOCK_PREVIEWS_DIR_NAME


def chunks_dir(settings: Settings) -> Path:
    return settings.processed_data_dir / CHUNKS_DIR_NAME


def chunk_previews_dir(settings: Settings) -> Path:
    return settings.processed_data_dir / CHUNK_PREVIEWS_DIR_NAME


def report_path(settings: Settings) -> Path:
    return settings.processed_data_dir / REPORT_FILENAME


def project_relative_path(path: Path) -> str:
    resolved_path = path if path.is_absolute() else ROOT_DIR / path
    try:
        return resolved_path.resolve().relative_to(ROOT_DIR.resolve()).as_posix()
    except ValueError:
        return resolved_path.as_posix()


def reset_artifact_dir(directory: Path, *, pattern: str = "*") -> None:
    """Clear files from one generated artifact directory before rebuilding it."""
    directory.mkdir(parents=True, exist_ok=True)
    directory_root = directory.resolve()
    for path in directory.glob(pattern):
        if not path.is_file():
            continue
        if not path.resolve().is_relative_to(directory_root):
            continue
        path.unlink()


def write_text_if_changed(output_path: Path, text: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists() and output_path.read_text(encoding="utf-8") == text:
        return
    output_path.write_text(text, encoding="utf-8")
