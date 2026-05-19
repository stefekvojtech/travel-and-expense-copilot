# AGENTS.md

## Scope

Applies to `data/processed/`.

This directory contains generated artifacts from loading, normalization,
chunking, embedding, and retrieval setup.

## Current Artifact Roles

- `01_loaded_documents/`: loaded source document JSONL records.
- `01_loaded_documents_preview/`: readable loaded-document previews.
- `02_normalized_blocks/`: canonical normalized block JSONL records.
- `02_normalized_blocks_preview/`: readable block previews.
- `03_chunks/`: embedding-ready chunk JSONL records with inherited metadata.
- `03_chunks_preview/`: readable chunk previews.
- `04_vectorstore/`: local Chroma vector database.
- `report.md`: pipeline summary, artifact counts, and warnings.

## Rules

- Blocks and chunks carry lineage; preview Markdown files do not.
- Avoid hand-editing generated artifacts unless the user explicitly asks for a
  fixture edit.
- Do not commit large vectorstore changes unless explicitly intended.
- Prefer rerunning the appropriate pipeline step when artifacts need regeneration.
- Real embedding uses OpenAI and requires explicit user approval.
- There is no `ingest_manifest.jsonl` or `ingest_warnings.jsonl`; warnings are
  reported in `report.md`.
