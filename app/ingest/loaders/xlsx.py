from __future__ import annotations

from pathlib import Path

from openpyxl import load_workbook


def normalize_xlsx(source_path: Path) -> tuple[str, str, str | None]:
    workbook = load_workbook(filename=source_path, read_only=True, data_only=True)
    sections: list[str] = []
    for sheet in workbook.worksheets:
        sections.append(f"## Sheet: {sheet.title}")
        for row in sheet.iter_rows(values_only=True):
            values = ["" if value is None else str(value).strip() for value in row]
            if any(values):
                sections.append("| " + " | ".join(values) + " |")
        sections.append("")

    # Future: add richer table metadata when spreadsheet layouts get more complex.
    return ("\n".join(sections).strip(), "openpyxl", None)

