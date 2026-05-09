"""Normalize HTML files into Markdown blocks with section lineage.

The HTML loader removes non-content tags, preserves common semantic structures
such as headings, lists, paragraphs, and tables, and emits source blocks for
later chunking and citation metadata.
"""

from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup

from app.ingest.loaders.common import clean_text
from app.ingest.loaders.models import NormalizedSource, SourceBlock


def normalize_html(source_path: Path) -> NormalizedSource:
    html_text = source_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html_text, "html.parser")
    # Scripts/styles are not policy evidence and would pollute embeddings.
    for tag_name in ("script", "style"):
        for tag in soup.find_all(tag_name):
            tag.decompose()

    # Generic HTML strategy: preserve headings, lists, and tables as Markdown.
    markdown_text = _html_soup_to_markdown(soup)
    return NormalizedSource(
        markdown_text=markdown_text,
        blocks=_markdown_to_blocks(markdown_text),
        extraction_method="beautifulsoup4",
    )


def _html_soup_to_markdown(soup: BeautifulSoup) -> str:
    body = soup.body or soup
    blocks = _render_block_nodes(body)
    cleaned_blocks = [block.strip() for block in blocks if block and block.strip()]
    return "\n\n".join(cleaned_blocks)


def _render_block_nodes(node) -> list[str]:
    # Walk common semantic HTML tags and flatten layout-only containers.
    blocks: list[str] = []
    for child in getattr(node, "children", []):
        name = getattr(child, "name", None)
        if name is None:
            text = clean_text(str(child))
            if text:
                blocks.append(text)
            continue

        if name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            level = int(name[1])
            text = _collect_inline_text(child)
            if text:
                blocks.append(f"{'#' * level} {text}")
            continue

        if name == "p":
            text = _collect_inline_text(child)
            if text:
                blocks.append(text)
            continue

        if name in {"ul", "ol"}:
            blocks.extend(_render_list(child, ordered=name == "ol"))
            continue

        if name == "table":
            table_markdown = _render_table(child)
            if table_markdown:
                blocks.append(table_markdown)
            continue

        if name in {"section", "article", "main", "header", "footer", "nav", "div"}:
            blocks.extend(_render_block_nodes(child))
            continue

        text = _collect_inline_text(child)
        if text:
            blocks.append(text)

    return blocks


def _render_list(list_node, ordered: bool) -> list[str]:
    items: list[str] = []
    index = 1
    for item in list_node.find_all("li", recursive=False):
        text = _collect_inline_text(item)
        if not text:
            continue
        prefix = f"{index}. " if ordered else "- "
        items.append(f"{prefix}{text}")
        index += 1
    return items


def _render_table(table_node) -> str:
    rows: list[list[str]] = []
    for row in table_node.find_all("tr"):
        cells = row.find_all(["th", "td"])
        values = [_collect_inline_text(cell) for cell in cells]
        if any(values):
            rows.append(values)

    if not rows:
        return ""

    width = max(len(row) for row in rows)
    padded_rows = [row + [""] * (width - len(row)) for row in rows]
    header = padded_rows[0]
    separator = ["---"] * width
    body = padded_rows[1:]

    markdown_rows = [
        f"| {' | '.join(header)} |",
        f"| {' | '.join(separator)} |",
    ]
    markdown_rows.extend(f"| {' | '.join(row)} |" for row in body)
    return "\n".join(markdown_rows)


def _collect_inline_text(node) -> str:
    text_parts: list[str] = []
    for part in node.stripped_strings:
        text_parts.append(clean_text(str(part)))
    return " ".join(part for part in text_parts if part)


def _markdown_to_blocks(markdown_text: str) -> list[SourceBlock]:
    # HTML has no page numbers, so the useful lineage here is mainly section_path.
    blocks: list[SourceBlock] = []
    current_section: str | None = None
    for block in markdown_text.split("\n\n"):
        text = block.strip()
        if not text:
            continue
        if text.startswith("#"):
            current_section = text.lstrip("#").strip()
            block_type = "heading"
        elif text.startswith("|"):
            block_type = "table"
        elif text.startswith(("- ", "1. ")):
            block_type = "list"
        else:
            block_type = "paragraph"
        blocks.append(
            SourceBlock(
                text=text,
                block_type=block_type,
                section_path=current_section,
            )
        )
    return blocks
