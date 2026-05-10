"""Source discovery and stable document identity helpers for ingestion stages."""

from __future__ import annotations

import re
from hashlib import sha1
from pathlib import Path
from typing import Iterable

from app.ingest.artifact_paths import project_relative_path
from app.ingest.loaders import SUPPORTED_SUFFIXES, infer_doc_type


LOCAL_AGENT_INSTRUCTION_FILENAME = "AGENTS.md"


def discover_raw_files(raw_data_dir: Path) -> list[Path]:
    """Return all raw source files, including unsupported files for reporting."""
    return sorted(
        path
        for path in raw_data_dir.rglob("*")
        if path.is_file() and path.name != LOCAL_AGENT_INSTRUCTION_FILENAME
    )


def split_supported_files(source_paths: Iterable[Path]) -> tuple[list[Path], list[Path]]:
    supported_paths: list[Path] = []
    unsupported_paths: list[Path] = []
    for source_path in source_paths:
        if source_path.suffix.lower() in SUPPORTED_SUFFIXES:
            supported_paths.append(source_path)
        else:
            unsupported_paths.append(source_path)
    return supported_paths, unsupported_paths


def build_doc_id(source_path: Path) -> str:
    digest = sha1(project_relative_path(source_path).encode("utf-8")).hexdigest()[:10]
    slug = re.sub(r"[^a-z0-9]+", "-", source_path.stem.lower()).strip("-")
    return f"{slug}-{digest}"


def title_from_source_path(source_path: Path | str) -> str:
    return Path(source_path).stem.replace("_", " ").replace("-", " ").title()


def doc_type_from_source_path(source_path: Path) -> str:
    return infer_doc_type(source_path.suffix.lower())
