# Architecture

This project is a local-first RAG demo for a Travel & Expense policy assistant.
The current code stops at retrieval context assembly. It does not yet generate a
final natural-language answer for users.

## Implemented Flow

```text
data/raw/*
  -> app/ingest/step01_load_documents.py
  -> data/processed/01_loaded_documents/*.jsonl
  -> data/processed/01_loaded_documents_preview/*.md

data/raw/* + data/processed/01_loaded_documents/*.jsonl
  -> app/ingest/step02_normalize_blocks.py
  -> data/processed/02_normalized_blocks/*.jsonl
  -> data/processed/02_normalized_blocks_preview/*.md

data/processed/02_normalized_blocks/*.jsonl
  -> app/ingest/step03_chunk_blocks.py
  -> data/processed/03_chunks/*.jsonl
  -> data/processed/03_chunks_preview/*.md

data/processed/03_chunks/*.jsonl
  -> app/ingest/step04_embed_chunks.py
  -> data/processed/04_vectorstore/

numbered stage outputs
  -> app/ingest/pipeline_report.py
  -> data/processed/report.md

query
  -> app/retrieval/vector_store.py
  -> app/retrieval/rerank.py
  -> app/retrieval/context.py
  -> citation-ready evidence context
```

## Runtime Boundaries

`app/core/config.py` owns configuration loading. It loads `.env` from the project
root and resolves relative configured paths from the project root.

`app/ingest/` owns ingestion, source normalization, block artifacts, chunking, and
embedding.

`app/retrieval/` owns local vector search, reranking, and context assembly.

`app/api/`, `app/agents/`, `app/prompts/`, `app/tools/`, `app/ui/`, and
`app/streaming/` currently exist only as empty scaffolds.

`scripts/` contains the command-line entrypoints that call application modules.
`scripts/01_load_documents.py` through `scripts/04_embed_chunks.py` run the
build stages individually. `scripts/00_run_ingestion.py` runs the numbered
ingestion flow from raw files through vector-store embedding. Search remains a
separate retrieval script.
The scripts should stay thin.

## Current Modules

`app/core/config.py` defines the `Settings` dataclass and `get_settings()` cache.
Required settings come from environment variables, usually via `.env`.

`app/ingest/step01_load_documents.py` discovers raw files and writes
loaded-document inspection JSONL plus readable previews. PDF, HTML, and TXT use
LangChain community loaders. XLSX and images use the project loaders so source
coverage stays aligned with production behavior.

`app/ingest/step02_normalize_blocks.py` normalizes supported sources into block
JSONL and readable block previews. Image normalization reuses the stage 01 image
text when available to avoid a second vision call in a normal pipeline run.

`app/ingest/artifacts.py` defines the shared block and chunk artifact schemas used
by raw ingestion, chunking, and embedding.

`app/ingest/loaders/` contains reusable file-type strategies:

- PDF uses `pypdf` for text and `pdfplumber` for tables.
- HTML uses BeautifulSoup and strips `script` and `style`.
- XLSX uses OpenPyXL in read-only, data-only mode.
- TXT uses simple paragraph cleanup.
- Images use OpenAI vision through LangChain/OpenAI when `OPENAI_API_KEY` exists.

`app/ingest/step03_chunk_blocks.py` reads block JSONL artifacts and creates chunks with
LangChain text splitters. Spreadsheet rows are chunked row-by-row. Other sources
are assembled into Markdown with spans so chunks can be mapped back to source
blocks.

`app/ingest/step04_embed_chunks.py` reads chunk JSONL files and embeds chunk text into
local Chroma. It builds a temporary collection first and promotes it only after
count verification.

`app/ingest/pipeline_report.py` writes `data/processed/report.md` from the
current numbered artifacts and warnings. The pipeline no longer writes
`ingest_manifest.jsonl` or `ingest_warnings.jsonl`.

`app/retrieval/vector_store.py` opens Chroma, embeds the query, retrieves chunks,
and supports exact-match filters for `doc_type`, `source_path`, and
`section_path`.

`app/retrieval/rerank.py` reranks retrieved candidates with local FlashRank.

`app/retrieval/context.py` selects diverse chunks, applies token budgets, and
formats evidence blocks with citation IDs and retrieval metadata.

## Code Documentation Conventions

Every Python module should start with a short top-level module docstring. In this
project, a module means a single `.py` file, such as
`app/ingest/step01_load_documents.py` or `scripts/search_chunks.py`.

Module docstrings should make the file understandable at a glance. They should
describe the module's role in the pipeline, the artifacts it reads or writes, and
important boundaries such as paid OpenAI calls, dry-run behavior, or planned-only
scaffolds.

Examples of the current convention:

- pipeline modules state which pipeline stage they own and what they do not do
- loader modules state the source type, extraction strategy, and metadata they
  preserve
- retrieval modules state whether they perform query embedding, local reranking,
  or citation-ready context assembly
- scripts state the command purpose and whether normal execution may call a paid
  model

Inline comments should explain non-obvious decisions, edge cases, lineage
assumptions, or temporary demo shortcuts. Avoid comments that simply repeat what
the code already says.

## Artifact Roles

`data/raw/` contains source documents.

`data/processed/01_loaded_documents/` contains loaded source document records.
This stage is useful for inspecting loader output before project normalization.

`data/processed/01_loaded_documents_preview/` contains readable previews of the
loaded source document records.

`data/processed/02_normalized_blocks/` contains canonical normalized block
JSONL. Blocks carry source metadata and are the input to chunking.

`data/processed/02_normalized_blocks_preview/` contains readable block previews.

`data/processed/03_chunks/` contains embedding-ready chunk JSONL. Chunks inherit
metadata and source block lineage.

`data/processed/03_chunks_preview/` contains readable chunk previews.

`data/processed/04_vectorstore/` contains the local Chroma database.

`data/processed/report.md` summarizes stage outputs and warnings.

`data/eval/` contains golden evaluation examples. The runner is not yet developed.

## Planned Boundaries

These boundaries are planned by project rules but not yet implemented:

- API routes should live in `app/api/`.
- Prompts should live in `app/prompts/`.
- Agent logic should live in `app/agents/`.
- Deterministic application tools can live in `app/tools/`.
- UI code can live in `app/ui/`.
- Streaming helpers can live in `app/streaming/`.
- MCP server code should live in `mcp_server/`.
- Business logic should not be placed directly in API route files.

## Current Limitations

There is no final answer generator. `scripts/search_chunks.py` prints assembled
context, not a user-facing policy answer.

There is no judge step, no confidence explanation, and no abstention flow beyond
the retrieval context that a future answer generator can use.

There is no API server, web UI, upload workflow, or streaming response panel yet.
The corresponding directories are currently empty scaffolds.

There is no automated eval runner yet.
