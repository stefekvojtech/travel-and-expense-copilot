# AGENTS.md

## Scope

Applies to `docs/`.

This directory contains human-facing Markdown documentation.

## Current Files

- `architecture.md`: implemented pipeline and module boundaries.
- `ingestion.md`: ingestion, loaders, previews, blocks, chunks, and embedding.
- `retrieval.md`: Chroma search, reranking, and context assembly.
- `evaluation.md`: golden eval data and planned eval runner.
- `api.md`: current API/UI status and planned API, UI, prompts, tools, and guardrails.

## Rules

- Use Markdown.
- Be explicit about implemented behavior versus planned behavior.
- Prefer concrete paths and commands over vague descriptions.
- Keep docs beginner-friendly but technically accurate.
- Document code-organization conventions in tracked docs, but keep local
  `AGENTS.md` files ignored and untracked.
- Update the relevant doc in the same change as behavior changes.
