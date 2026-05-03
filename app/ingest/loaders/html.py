from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup

from app.ingest.loaders.common import clean_text


def normalize_html(source_path: Path) -> tuple[str, str, str | None]:
    html_text = source_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html_text, "html.parser")
    for tag_name in ("script", "style"):
        for tag in soup.find_all(tag_name):
            tag.decompose()

    # Generic HTML strategy: preserve headings, lists, and tables as Markdown.
    return (_html_soup_to_markdown(soup), "beautifulsoup4", None)


def _html_soup_to_markdown(soup: BeautifulSoup) -> str:
    body = soup.body or soup
    blocks = _render_block_nodes(body)
    cleaned_blocks = [block.strip() for block in blocks if block and block.strip()]
    return "\n\n".join(cleaned_blocks)


def _render_block_nodes(node) -> list[str]:
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

