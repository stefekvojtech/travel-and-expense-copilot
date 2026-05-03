from __future__ import annotations

from pathlib import Path

from openpyxl import load_workbook

from app.ingest.loaders.models import NormalizedSource, SourceBlock


def normalize_xlsx(source_path: Path) -> NormalizedSource:
    # Read formulas as cached values because RAG needs visible business data.
    workbook = load_workbook(filename=source_path, read_only=True, data_only=True)
    sections: list[str] = []
    blocks: list[SourceBlock] = []
    for sheet in workbook.worksheets:
        # Treat each worksheet like a section; later chunks can cite sheet metadata.
        section = f"Sheet: {sheet.title}"
        sections.append(f"## {section}")
        blocks.append(
            SourceBlock(
                text=f"## {section}",
                block_type="heading",
                section_path=section,
                sheet=sheet.title,
            )
        )
        for row in sheet.iter_rows(values_only=True):
            values = ["" if value is None else str(value).strip() for value in row]
            if any(values):
                # Current generic strategy keeps each non-empty row as one lineage block.
                row_markdown = "| " + " | ".join(values) + " |"
                sections.append(row_markdown)
                blocks.append(
                    SourceBlock(
                        text=row_markdown,
                        block_type="table_row",
                        section_path=section,
                        sheet=sheet.title,
                    )
                )
        sections.append("")

    # Future: add richer table metadata when spreadsheet layouts get more complex.
    return NormalizedSource(
        markdown_text="\n".join(sections).strip(),
        blocks=blocks,
        extraction_method="openpyxl",
    )
