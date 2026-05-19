# AGENTS.md

## Scope

Applies to `app/retrieval/`.

This package owns retrieval from the local vector store, local reranking, and
citation-ready context assembly.

## Current Flow

1. `vector_store.py` embeds the query and searches Chroma.
2. `rerank.py` reranks retrieved candidates with local FlashRank.
3. `context.py` selects diverse evidence blocks and formats citation-ready context.
4. `chroma_config.py` stores shared Chroma collection metadata.

## Rules

- Retrieval module docstrings should call out whether code performs paid query
  embedding, local reranking, or citation-context assembly.
- Preserve citation lineage fields: source path, chunk ID, section path, pages,
  sheets, row number, retrieval score, and rerank score.
- Do not generate final policy answers directly from the user question. Retrieval
  must happen first once answer generation exists.
- Query embedding uses OpenAI and is a paid call. Prefer `search_chunks.py --dry-run`
  for collection inspection.
- Keep Chroma swappable where practical.
- Keep local reranking local unless the user explicitly asks for a paid reranker.
- Update `docs/retrieval.md` when retrieval behavior, filters, ranking, scoring,
  or context formatting changes.
