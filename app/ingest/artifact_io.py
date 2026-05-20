"""Read and write JSONL artifact files used by ingestion stages."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, TypeVar

from app.ingest.artifact_paths import write_text_if_changed

T = TypeVar("T")


def write_jsonl(output_path: Path, rows: Iterable[object]) -> None:
    text_rows = [
        json.dumps(asdict(row) if is_dataclass(row) else row, ensure_ascii=True)
        for row in rows
    ]
    write_text_if_changed(output_path, "\n".join(text_rows) + ("\n" if text_rows else ""))


def read_jsonl(
    output_path: Path,
    row_type: type[T] | Callable[[dict[str, Any]], T],
) -> list[T]:
    rows: list[T] = []
    if not output_path.exists():
        return rows
    for line in output_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            if isinstance(row_type, type):
                rows.append(row_type(**row))
            else:
                rows.append(row_type(row))
    return rows
