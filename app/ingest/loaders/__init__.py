from __future__ import annotations

from pathlib import Path

from app.ingest.loaders.html import normalize_html
from app.ingest.loaders.image import normalize_image
from app.ingest.loaders.pdf import normalize_pdf
from app.ingest.loaders.xlsx import normalize_xlsx


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg"}
SUPPORTED_SUFFIXES = {".pdf", ".html", ".htm", ".xlsx", *IMAGE_SUFFIXES}


def infer_doc_type(suffix: str) -> str:
    if suffix == ".pdf":
        return "pdf"
    if suffix in {".html", ".htm"}:
        return "html"
    if suffix == ".xlsx":
        return "xlsx"
    if suffix in IMAGE_SUFFIXES:
        return "image"
    return "unknown"


def normalize_by_file_type(source_path: Path) -> tuple[str, str, str | None]:
    suffix = source_path.suffix.lower()
    if suffix in {".html", ".htm"}:
        return normalize_html(source_path)
    if suffix == ".xlsx":
        return normalize_xlsx(source_path)
    if suffix == ".pdf":
        return normalize_pdf(source_path)
    if suffix in IMAGE_SUFFIXES:
        return normalize_image(source_path)
    return ("Unsupported file type.", "unsupported", "unsupported_suffix")

