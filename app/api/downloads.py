"""Download routes for local demo source artifacts."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from fastapi import APIRouter
from fastapi.responses import Response

from app.core.config import ROOT_DIR


router = APIRouter()

RAW_DATA_DIR = ROOT_DIR / "data" / "raw"
RAW_DATA_ZIP_NAME = "atlas-raw-policy-corpus.zip"


@router.get("/api/downloads/raw-data.zip")
def download_raw_data_zip() -> Response:
    """Return a ZIP archive of demo raw files, excluding local agent instructions."""
    zip_bytes = build_raw_data_zip(RAW_DATA_DIR)
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{RAW_DATA_ZIP_NAME}"',
            "Cache-Control": "no-store",
        },
    )


def build_raw_data_zip(raw_data_dir: Path) -> bytes:
    """Build a ZIP archive from raw source files while omitting AGENTS.md files."""
    buffer = BytesIO()
    with ZipFile(buffer, mode="w", compression=ZIP_DEFLATED) as archive:
        for path in sorted(raw_data_dir.rglob("*")):
            if not path.is_file() or path.name.lower() == "agents.md":
                continue
            archive.write(path, path.relative_to(raw_data_dir).as_posix())
    return buffer.getvalue()
