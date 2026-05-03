from __future__ import annotations

import re
from pathlib import Path

import pdfplumber
from pypdf import PdfReader

from app.ingest.loaders.common import clean_text


PAGE_LABEL_RE = re.compile(r"^page\s+\d+$", re.IGNORECASE)
NUMBERED_HEADING_RE = re.compile(r"^(\d+(?:\.\d+)*\.?)\s+(.+)$")
BULLET_PREFIXES = ("\u007f", "\u2022", "-", "*")


def normalize_pdf(source_path: Path) -> tuple[str, str, str | None]:
    reader = PdfReader(str(source_path))
    pages = [_extract_page_lines(page.extract_text() or "") for page in reader.pages]
    repeated_lines = _find_repeated_page_lines(pages)
    tables_by_page, table_lines_by_page = _extract_tables_by_page(source_path)

    blocks: list[str] = []
    for index, page in enumerate(reader.pages, start=1):
        page_lines = _extract_page_lines(page.extract_text() or "")
        page_tables = tables_by_page.get(index, [])
        table_lines = table_lines_by_page.get(index, set())
        content_lines = _remove_page_noise(page_lines, repeated_lines)
        if not content_lines:
            blocks.append(f"<!-- source_page: {index} -->")
            blocks.append("[No text extracted from this page]")
        else:
            blocks.append(f"<!-- source_page: {index} -->")
            blocks.extend(
                _lines_to_markdown_blocks(
                    content_lines,
                    page_tables=page_tables,
                    table_lines=table_lines,
                    page_number=index,
                )
            )

    # Future: add quality checks and escalate to layout/OCR parsers when needed.
    return ("\n\n".join(block for block in blocks if block).strip(), "pypdf+pdfplumber", None)


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


def _remove_page_noise(
    lines: list[str],
    repeated_lines: set[str],
) -> list[str]:
    cleaned_lines: list[str] = []
    for line in lines:
        if line in repeated_lines:
            continue
        if PAGE_LABEL_RE.match(line):
            continue
        cleaned_lines.append(line)
    return cleaned_lines


def _is_table_line(line: str, table_lines: set[str]) -> bool:
    for table_line in table_lines:
        if line == table_line:
            return True
        if len(line) > 3 and line in table_line:
            return True
    return False


def _extract_tables_by_page(
    source_path: Path,
) -> tuple[dict[int, list[list[list[str]]]], dict[int, set[str]]]:
    tables_by_page: dict[int, list[list[list[str]]]] = {}
    table_lines_by_page: dict[int, set[str]] = {}
    with pdfplumber.open(source_path) as pdf:
        for page_index, page in enumerate(pdf.pages, start=1):
            raw_tables = [table for table in page.extract_tables() if table and len(table) > 1]
            tables = [_clean_table(table) for table in raw_tables]
            if tables:
                tables_by_page[page_index] = tables
                table_lines_by_page[page_index] = _table_text_lines(raw_tables)
    return tables_by_page, table_lines_by_page


def _clean_table(table: list[list[str | None]]) -> list[list[str]]:
    width = max(len(row) for row in table)
    cleaned_table: list[list[str]] = []
    for row in table:
        cleaned_row = [clean_text(cell or "") for cell in row]
        cleaned_row.extend([""] * (width - len(cleaned_row)))
        if any(cleaned_row):
            cleaned_table.append(cleaned_row)
    return cleaned_table


def _table_text_lines(tables: list[list[list[str | None]]]) -> set[str]:
    lines: set[str] = set()
    for table in tables:
        for row in table:
            for cell in row:
                for line in (cell or "").splitlines():
                    cleaned = clean_text(line)
                    if cleaned:
                        lines.add(cleaned)
    return lines


def _table_to_markdown(table: list[list[str]]) -> str:
    if not table:
        return ""

    header = [_escape_table_cell(cell) for cell in table[0]]
    separator = ["---"] * len(header)
    body = [
        [_escape_table_cell(cell) for cell in row]
        for row in table[1:]
    ]
    rows = [
        f"| {' | '.join(header)} |",
        f"| {' | '.join(separator)} |",
    ]
    rows.extend(f"| {' | '.join(row)} |" for row in body)
    return "\n".join(rows)


def _escape_table_cell(cell: str) -> str:
    return clean_text(cell).replace("|", "\\|")


def _lines_to_markdown_blocks(
    lines: list[str],
    *,
    page_tables: list[list[list[str]]],
    table_lines: set[str],
    page_number: int,
) -> list[str]:
    blocks: list[str] = []
    paragraph_lines: list[str] = []
    next_table_index = 0

    for line in lines:
        if _is_table_line(line, table_lines):
            if next_table_index < len(page_tables):
                _flush_paragraph(paragraph_lines, blocks)
                table_index = next_table_index + 1
                table_markdown = _table_to_markdown(page_tables[next_table_index])
                if table_markdown:
                    blocks.append(f"#### Extracted Table {table_index} (Page {page_number})")
                    blocks.append(table_markdown)
                next_table_index += 1
            continue

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
    for table in page_tables[next_table_index:]:
        table_index = next_table_index + 1
        table_markdown = _table_to_markdown(table)
        if table_markdown:
            blocks.append(f"#### Extracted Table {table_index} (Page {page_number})")
            blocks.append(table_markdown)
        next_table_index += 1
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
