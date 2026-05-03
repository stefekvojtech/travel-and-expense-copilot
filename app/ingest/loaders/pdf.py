from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from app.ingest.loaders.common import clean_text


def normalize_pdf(source_path: Path) -> tuple[str, str, str | None]:
    reader = PdfReader(str(source_path))
    sections: list[str] = []
    for index, page in enumerate(reader.pages, start=1):
        page_text = clean_text(page.extract_text() or "")
        sections.append(f"## Page {index}")
        sections.append(page_text or "[No text extracted from this page]")
        sections.append("")

    # Future: add quality checks and escalate to layout/OCR parsers when needed.
    return ("\n".join(sections).strip(), "pypdf", None)

