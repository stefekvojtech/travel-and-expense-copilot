# AGENTS.md

## Scope

Applies to `app/ingest/loaders/`.

This directory contains reusable file-type strategies that normalize raw files
into `NormalizedSource` objects.

## Current Loaders

- `pdf.py`: PDF text through `pypdf`, tables through `pdfplumber`.
- `html.py`: BeautifulSoup-based HTML-to-Markdown conversion.
- `xlsx.py`: OpenPyXL row-level spreadsheet extraction.
- `text.py`: UTF-8 plain text cleanup.
- `image.py`: OpenAI vision extraction when an API key is configured.
- `models.py`: shared loader dataclasses.
- `common.py`: shared text cleanup helpers.

## Rules

- Each loader module should have a module docstring describing the source type,
  extraction strategy, and lineage metadata it preserves.
- Each loader should be reusable across many files of that type.
- Return both human-readable Markdown and structured `SourceBlock` records.
- Preserve useful source metadata such as page, sheet, row, section, and table
  information.
- Report limitations through extraction warnings when practical.
- Avoid one-off parsing for a single demo document.
- Be especially careful with `image.py`: vision extraction is a paid model call.
- If a new suffix is supported, update `loaders/__init__.py`, `.env.example` only
  if needed, `README.md`, and `docs/ingestion.md`.
