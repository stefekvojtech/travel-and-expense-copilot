# AGENTS.md

## Scope

Applies to `app/ingest/`.

This package owns raw source ingestion, file-type normalization, block artifacts,
chunking, and embedding into the local vector store.

## Current Flow

1. `step01_load_documents.py` discovers supported raw files and writes
   `01_loaded_documents` JSONL plus readable previews.
2. `step02_normalize_blocks.py` uses loaders in `loaders/` to normalize sources
   into canonical `02_normalized_blocks` JSONL plus readable previews.
3. `step03_chunk_blocks.py` reads normalized block JSONL and writes
   `03_chunks` JSONL plus readable previews.
4. `step04_embed_chunks.py` reads chunk JSONL, calls OpenAI embeddings, and
   writes to local Chroma under `04_vectorstore`.
5. `pipeline_report.py` writes `data/processed/report.md`; there is no manifest
   or separate warnings JSONL file.

## Rules

- Keep ingestion module docstrings specific about the artifact stage they own:
  raw normalization, chunking, or embedding.
- Load sources first, then normalize every source type to preview Markdown plus
  block JSONL.
- Treat `02_normalized_blocks` JSONL as canonical for chunk lineage.
- Preview Markdown files are for transparency and inspection only.
- Preserve metadata lineage on every chunk.
- Do not add document-specific extraction hacks unless they are explicitly marked
  as temporary demo-only shortcuts.
- Do not run paid image or embedding calls without explicit user permission.
- Prefer local validation commands. Do not assume embedding has a dry-run mode.
- Update `docs/ingestion.md` when ingestion, chunking, embedding, artifacts, or
  supported source types change.
