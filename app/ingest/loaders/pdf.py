from __future__ import annotations

import re
from pathlib import Path

from pypdf import PdfReader

from app.ingest.loaders.common import clean_text


PAGE_LABEL_RE = re.compile(r"^page\s+\d+$", re.IGNORECASE)
NUMBERED_HEADING_RE = re.compile(r"^(\d+(?:\.\d+)*\.?)\s+(.+)$")
BULLET_PREFIXES = ("\u007f", "\u2022", "-", "*")


def normalize_pdf(source_path: Path) -> tuple[str, str, str | None]:
    reader = PdfReader(str(source_path))
    pages = [_extract_page_lines(page.extract_text() or "") for page in reader.pages]
    repeated_lines = _find_repeated_page_lines(pages)

    blocks: list[str] = []
    for index, page in enumerate(reader.pages, start=1):
        page_lines = _extract_page_lines(page.extract_text() or "")
        content_lines = _remove_page_noise(page_lines, repeated_lines)
        if not content_lines:
            blocks.append(f"<!-- source_page: {index} -->")
            blocks.append("[No text extracted from this page]")
            continue

        blocks.append(f"<!-- source_page: {index} -->")
        blocks.extend(_lines_to_markdown_blocks(content_lines))

    # Future: add quality checks and escalate to layout/OCR parsers when needed.
    return ("\n\n".join(block for block in blocks if block).strip(), "pypdf", None)


def _extract_page_lines(page_text: str) -> list[str]:
    lines: list[str] = []
    for line in page_text.splitlines():
        cleaned = clean_text(line.replace("\u007f", "- "))
        if cleaned:
            lines.append(cleaned)
    return lines


def _find_repeated_page_lines(pages: list[list[str]]) -> set[str]:
    line_counts: dict[str, int] = {}
    for page_lines in pages:
        for line in set(page_lines[:3]):
            line_counts[line] = line_counts.get(line, 0) + 1

    min_repetitions = 2 if len(pages) > 1 else 1
    return {
        line
        for line, count in line_counts.items()
        if count >= min_repetitions and not PAGE_LABEL_RE.match(line)
    }


def _remove_page_noise(lines: list[str], repeated_lines: set[str]) -> list[str]:
    cleaned_lines: list[str] = []
    for line in lines:
        if line in repeated_lines:
            continue
        if PAGE_LABEL_RE.match(line):
            continue
        cleaned_lines.append(line)
    return cleaned_lines


def _lines_to_markdown_blocks(lines: list[str]) -> list[str]:
    blocks: list[str] = []
    paragraph_lines: list[str] = []

    for line in lines:
        heading = _format_numbered_heading(line)
        if heading:
            _flush_paragraph(paragraph_lines, blocks)
            blocks.append(heading)
            continue

        bullet = _format_bullet(line)
        if bullet:
            _flush_paragraph(paragraph_lines, blocks)
            blocks.append(bullet)
            continue

        paragraph_lines.append(line)

    _flush_paragraph(paragraph_lines, blocks)
    return blocks


def _format_numbered_heading(line: str) -> str | None:
    match = NUMBERED_HEADING_RE.match(line)
    if not match:
        return None

    number, title = match.groups()
    title = title.strip()
    if not title or len(title) > 90:
        return None

    depth = number.rstrip(".").count(".")
    heading_level = min(2 + depth, 6)
    return f"{'#' * heading_level} {number} {title}"


def _format_bullet(line: str) -> str | None:
    if not line.startswith(BULLET_PREFIXES):
        return None
    return f"- {line.lstrip(''.join(BULLET_PREFIXES)).strip()}"


def _flush_paragraph(paragraph_lines: list[str], blocks: list[str]) -> None:
    if paragraph_lines:
        blocks.append(" ".join(paragraph_lines))
        paragraph_lines.clear()
