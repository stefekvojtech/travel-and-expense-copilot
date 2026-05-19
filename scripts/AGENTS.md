# AGENTS.md

## Scope

Applies to `scripts/`.

Scripts are thin command-line entrypoints over application modules.

## Current Scripts

- `01_load_documents.py`: load raw sources into numbered loaded-document artifacts and previews.
- `02_normalize_blocks.py`: normalize supported sources into canonical block artifacts and previews.
- `03_chunk_blocks.py`: chunk normalized block JSONL artifacts and write chunk previews.
- `04_embed_chunks.py`: embed chunk JSONL artifacts into local Chroma.
- `00_run_ingestion.py`: run the complete numbered ingestion flow.
- `search_chunks.py`: vector search, rerank, and context assembly.
- `print_open_ai_models.py`: utility for listing OpenAI models.

## Rules

- Every script should have a module docstring that states the command's purpose
  and flags paid model calls or dry-run behavior where relevant.
- Keep scripts small; put reusable behavior in `app/`.
- Preserve `python -m pip install -e .` as the expected setup model.
- Do not reintroduce `scripts/_bootstrap.py`.
- Do not assume a dry-run mode exists for embedding. `04_embed_chunks.py` calls
  paid OpenAI embeddings; stage 01 may call paid vision for image sources.
- Search keeps `--dry-run` for inspecting Chroma without embedding a query.
- Update `README.md` and relevant docs when adding, removing, or changing scripts.
