# AGENTS.md

## Scope

Applies to everything under `app/`.

This directory contains Python application code. Keep business logic in reusable
modules and keep future route/script layers thin.

## Current Package Map

- `core/`: settings and project-root path resolution.
- `ingest/`: ingestion pipelines, source loaders, chunking, and embedding.
- `retrieval/`: Chroma retrieval, FlashRank reranking, and context assembly.
- `api/`: FastAPI chat, download, and UI configuration routes.
- `agents/`: grounded answer generation and validation.
- `prompts/`: prompt Markdown files for answer generation.
- `tools/`: deterministic claim, currency, and evidence tools.
- `streaming/`: server-sent event helpers and chat streaming orchestration.
- `ui/`: implemented plain HTML/CSS/JS browser UI.

## Rules

- Every Python module in `app/` should start with a concise module docstring that
  explains the module's role and boundaries.
- Use type hints where reasonable.
- Prefer small functions that can be tested directly.
- Do not place route-specific business logic in API modules once API work begins.
- Do not make OpenAI calls from imports or module-level initialization.
- Keep OpenAI usage explicit and easy to dry-run or avoid.
- Preserve source metadata and citation lineage when touching ingestion or retrieval.
- Update `docs/architecture.md` when adding or moving application boundaries.
