# AGENTS.md

## Scope

Applies to `data/`.

This directory contains the demo corpus, generated pipeline artifacts, and golden
eval examples.

## Directory Roles

- `raw/`: source files for the corpus.
- `processed/`: numbered generated artifacts, previews, report, and local Chroma
  vector store.
- `eval/`: golden evaluation examples.

## Rules

- Do not treat preview Markdown files as canonical lineage.
- Do not commit large generated vector databases unless explicitly intended as
  demo fixtures.
- Avoid pointless rewrites of generated files.
- Do not force image re-ingestion without explicit user permission.
- Update docs when artifact formats or data roles change.
