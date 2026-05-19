# AGENTS.md

## Scope

Applies to `data/raw/`.

This directory contains raw source documents for the demo policy corpus.

## Rules

- Raw files are the source of truth for ingestion.
- Ingestion discovers supported files recursively.
- Local `AGENTS.md` instruction files are excluded from ingestion discovery and
  are not source corpus documents.
- Supported types are PDF, HTML/HTM, XLSX, TXT, PNG, JPG, and JPEG.
- Unsupported files should produce ingest warnings instead of silent skips.
- Do not add document-specific parser logic for a new raw file unless it is clearly
  marked as a temporary demo-only shortcut.
