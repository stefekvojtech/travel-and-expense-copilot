# Travel & Expense Policy Copilot

Local-first, grounded Travel & Expense Policy Copilot built in Python.

This project is a learning/demo RAG system for practicing document ingestion,
chunking, embeddings, retrieval, citations, deterministic tools, and evaluation.
It is not a finished assistant yet. The current implementation builds and searches
a local policy corpus; answer generation, API routes, UI, agent tools, judge flow,
and the full evaluation runner are not yet developed.

## Current Status

Implemented:

- Raw document ingestion from `data/raw/`
- Normalization into human-readable Markdown previews and canonical block JSONL
- Chunk generation from block JSONL artifacts
- OpenAI embedding into a local Chroma vector store
- Chroma vector retrieval
- Local FlashRank reranking
- Citation-ready context assembly
- A golden eval dataset in `data/eval/golden_eval_set.jsonl`

Not yet developed:

- FastAPI app and API routes
- Browser UI
- Final grounded answer generation
- Prompt files under `app/prompts/`
- Agent/tool layer under `app/agents/`
- MCP server tools under `mcp_server/`
- Automated eval runner
- Judge/faithfulness flow

## Documentation

Start here, then go deeper as needed:

- [Architecture](docs/architecture.md)
- [Ingestion](docs/ingestion.md)
- [Retrieval](docs/retrieval.md)
- [Evaluation](docs/evaluation.md)
- [API and UI Status](docs/api.md)

`AGENTS.md` contains project rules and development constraints for coding agents.
The docs in `docs/` explain the project for humans working in the repo.

## Project Layout

```text
app/
  agents/               Empty scaffold for future agent logic
  api/                  Empty scaffold for future API routes
  core/                 Settings and project-root path resolution
  ingest/               Raw ingestion, loaders, chunking, embedding
  prompts/              Empty scaffold for future prompt files
  retrieval/            Chroma search, FlashRank rerank, context assembly
  streaming/            Empty scaffold for future streaming behavior
  tools/                Empty scaffold for future deterministic tools
  ui/                   Empty scaffold for future plain HTML/CSS/JS UI
data/
  raw/                  Demo source documents
  processed/            Generated markdown, blocks, chunks, and Chroma store
  eval/                 Golden evaluation examples
scripts/                Command-line entrypoints and unified pipeline CLI
docs/                   Human documentation
AGENTS.md               Agent-facing project instructions
pyproject.toml          Package metadata and dependencies
```

Some future-facing directories already exist as empty scaffolds. `mcp_server/` is
not present yet.

## Setup

Use Python 3.11 or newer. From the repository root:

```powershell
python -m pip install -e .
```

Create a local `.env` from `.env.example` and set `OPENAI_API_KEY` if you intend
to run image extraction, embedding, or vector search that embeds a query.

Relative paths in `.env` are resolved from the project root, not from the current
terminal working directory.

## Current Pipeline

The current local pipeline is:

1. Put raw files in `data/raw/`.
2. Run ingestion to create Markdown previews, block JSONL, manifest, and warnings.
3. Run chunking to create embedding-ready chunk JSONL.
4. Run embedding to write vectors into local Chroma.
5. Run search to retrieve chunks, rerank them, and print assembled evidence context.

Commands:

```powershell
python scripts/pipeline.py ingest
python scripts/pipeline.py chunk
python scripts/pipeline.py embed --dry-run
python scripts/pipeline.py embed
python scripts/pipeline.py search "Can I take a taxi from Prague airport after 21:00?"
```

The older focused script entrypoints are still available:

```powershell
python scripts/ingest_incremental.py
python scripts/chunk_blocks.py
python scripts/embed_chunks.py --dry-run
python scripts/embed_chunks.py
python scripts/search_chunks.py "Can I take a taxi from Prague airport after 21:00?"
```

Use `python scripts/pipeline.py ingest --force` or `python scripts/ingest_force.py`
only when you intentionally want to rebuild all ingestion artifacts. Image ingestion
can call OpenAI vision and consume paid credits when an API key is configured.

Use `python scripts/embed_chunks.py --dry-run` before a real embedding run. A real
embedding run calls OpenAI embeddings and consumes paid credits.

## Supported Source Types

Current source loaders:

- PDF: `app/ingest/loaders/pdf.py`
- HTML/HTM: `app/ingest/loaders/html.py`
- XLSX: `app/ingest/loaders/xlsx.py`
- TXT: `app/ingest/loaders/text.py`
- PNG/JPG/JPEG: `app/ingest/loaders/image.py`

Unsupported files are written to `data/processed/ingest_warnings.jsonl`.

## Important Concepts

Markdown previews are for human inspection. They are not the canonical source for
chunk lineage.

Block JSONL files in `data/processed/blocks/` are the canonical normalized
artifacts. Chunking reads these files.

Chunk JSONL files in `data/processed/chunks/` are the embedding-ready artifacts.
Each chunk carries source lineage metadata such as `doc_id`, `chunk_id`,
`source_path`, `source_block_ids`, `section_path`, `pages`, `sheets`, and
`token_count`.

The local Chroma vector store lives under `data/processed/vectorstore/`. It uses
cosine distance through collection metadata `{"hnsw:space": "cosine"}`.

## Development Notes

This project intentionally favors local/open-source components. OpenAI is used for
embeddings and image vision extraction where configured.

Do not add a paid SaaS dependency unless the project explicitly needs it. Keep the
future frontend plain HTML/CSS/JS and the backend Python.

The current project does not use `uv`; use `python -m pip install -e .` unless
`uv` is later added deliberately.
