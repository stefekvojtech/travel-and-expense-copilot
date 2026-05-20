"""Tests for spreadsheet normalization behavior."""

from pathlib import Path

from app.ingest.loaders.xlsx import normalize_xlsx


def test_xlsx_row_text_omits_location_prefixes() -> None:
    normalized = normalize_xlsx(Path("data/raw/per_diem_caps.xlsx"))

    row_block = next(block for block in normalized.blocks if block.block_type == "table_row")
    assert not row_block.text.startswith("Sheet:")
    assert "\nRow:" not in row_block.text
    assert row_block.section_path
    assert not row_block.section_path.startswith("Sheet:")
    assert row_block.metadata["row_number"] > 0
