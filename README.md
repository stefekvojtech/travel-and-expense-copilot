---
title: "Travel & Expense Policy Copilot"
sdk: docker
app_port: 7860
---

# Travel & Expense Policy Copilot

Local-first, grounded Travel & Expense Policy Copilot built in Python.

This project is a learning/demo RAG system for practicing document ingestion,
chunking, embeddings, retrieval, citations, deterministic tools, and evaluation.
It is not a finished assistant yet. The current implementation builds and searches
a local policy corpus and can generate first-pass grounded answers from retrieved
evidence through CLI, FastAPI routes, and a minimal browser UI; agent
tool-calling, judge flow, and answer-level evaluation are not yet developed.

## Current Status

Implemented:

- Raw document ingestion from `data/raw/`
- Loaded-document inspection artifacts
- Normalization into canonical block JSONL and readable block previews
- Chunk generation from block JSONL artifacts
- OpenAI embedding into a local Chroma vector store
- Chroma vector retrieval
- Local FlashRank reranking
- Citation-ready context assembly
- First-pass grounded answer generation from retrieved evidence
- FastAPI health, chat, and streaming chat routes
- Minimal plain HTML/CSS/JS browser UI with streaming answers, expandable
  processing traces, a retrieval debug panel, and clickable example questions
- Structured answer-output validation and fail-closed citation checks
- Prompt files for the grounded-answering contract and answer examples
- Deterministic currency conversion tool with local Finance workbook rates first
  and Frankfurter API fallback
- Deterministic claim eligibility and evidence completeness tools
- A golden eval dataset in `data/eval/golden_eval_set.jsonl`
- Retrieval eval runner with Markdown and JSONL outputs

Not yet developed:

- Agent tool-calling loop for claim evaluation
- MCP server tools under `mcp_server/`
- Answer-level eval runner
- Judge/faithfulness flow

## Documentation

Start here, then go deeper as needed:

- [Architecture](docs/architecture.md)
- [Ingestion](docs/ingestion.md)
- [Retrieval](docs/retrieval.md)
- [Evaluation](docs/evaluation.md)
- [API and UI Status](docs/api.md)
- [Deployment](docs/deployment.md)
- [Deterministic Tools](docs/tools.md)
- [Future Improvements](docs/future_improvements.md)

`AGENTS.md` contains project rules and development constraints for coding agents.
The docs in `docs/` explain the project for humans working in the repo.

## Project Layout

```text
app/
  agents/               Answer orchestration and future agent logic
  api/                  FastAPI routes and Pydantic schemas
  core/                 Settings and project-root path resolution
  ingest/               Raw ingestion, loaders, chunking, embedding
  eval/                 Retrieval evaluation over golden examples
  prompts/              Prompt Markdown files
  retrieval/            Chroma search, FlashRank rerank, context assembly
  streaming/            Server-sent event helpers and chat streaming orchestration
  tools/                Deterministic helper tools
  ui/                   Plain HTML/CSS/JS browser UI
data/
  raw/                  Demo source documents
  processed/            Numbered generated artifacts and Chroma store
  eval/                 Golden evaluation examples
scripts/                Numbered stage scripts, full pipeline, and search CLI
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

The app has built-in defaults for non-secret settings shown in `.env.example`.
Create a local `.env` only when you need to override those defaults or set
`OPENAI_API_KEY` for OpenAI-backed image extraction, chunk embedding, vector
search, or answer generation.

Relative paths in `.env` are resolved from the project root, not from the current
terminal working directory.

## Current Pipeline

The current local pipeline is:

1. Put raw files in `data/raw/`.
2. Load source documents into `01_loaded_documents` and readable previews.
3. Normalize loaded/raw sources into `02_normalized_blocks` and readable previews.
4. Chunk blocks into `03_chunks` and readable chunk previews.
5. Embed chunks into local Chroma under `04_vectorstore`.
6. Run search separately to retrieve chunks, rerank them, and print evidence context.

Commands:

```powershell
python scripts/01_load_documents.py
python scripts/02_normalize_blocks.py
python scripts/03_chunk_blocks.py
python scripts/04_embed_chunks.py
python scripts/00_run_ingestion.py
```

Retrieval and answer generation stay outside the corpus-build pipeline:

```powershell
python scripts/10_retrieve_context.py "Can I take a taxi from Prague airport after 21:00?"
python scripts/30_ask.py "Can I take a taxi from Prague airport after 21:00?"
```

`scripts/30_ask.py` performs paid OpenAI calls for query embedding and final
answer generation.

The same answer path is exposed through FastAPI:

```powershell
python -m uvicorn app.main:app --reload
```

Open the local UI at:

```text
http://127.0.0.1:8000/ui/
```

Routes:

- `GET /health`
- `POST /api/chat`
- `POST /api/chat/stream`

`/api/chat` returns one validated JSON answer. `/api/chat/stream` returns
server-sent events for simple runtime status, detailed answer trace steps,
answer deltas, and the final validated answer payload. The browser UI uses the
streaming route and displays retrieved evidence, rerank scores, citations,
confidence, and the assembled context in its debug panel.
Both chat routes and the UI perform paid OpenAI calls for query embedding and
final answer generation.

For public demos, set `PUBLIC_DEMO_MODE=true` in the hosted environment. Demo
mode keeps the OpenAI key backend-only, ignores caller-provided `search_k`, caps
questions at 1000 characters, limits answer generation to `ANSWER_MAX_TOKENS`,
uses public-demo rate limits, and returns generic server errors to browser
clients. Keep local development at `PUBLIC_DEMO_MODE=false`.

## Docker and Hugging Face Spaces

The repository includes a Dockerfile for deployment to Hugging Face Spaces or
another container host. It serves FastAPI and the static UI from one process and
uses the existing Chroma artifacts under `data/processed/04_vectorstore/`.
Ingestion does not run at container startup.

For Hugging Face Spaces:

1. Create a Docker Space.
2. Set `OPENAI_API_KEY` as a private Space Secret.
3. Set `PUBLIC_DEMO_MODE=true` in the Space environment.
4. Keep the app port at `7860`.
5. Deploy the committed snapshot with `python scripts/deploy_hf_space.py`.

Container startup command:

```text
python -m uvicorn app.main:app --host 0.0.0.0 --port 7860
```

If configuring the Space through README metadata, use:

```yaml
---
sdk: docker
app_port: 7860
---
```

The deploy script uses the Hugging Face login or Git credential already stored
on the machine. Do not put Hugging Face tokens in `.env` or tracked files.

## Script Numbering

Script numbers indicate the order and role of local workflow entrypoints:

- `00_*`: orchestration scripts that run multiple numbered stages
- `01_*` through `09_*`: corpus-build stages, from raw source files to indexes
- `10_*` through `19_*`: retrieval and retrieval-debug entrypoints
- `20_*` through `29_*`: evaluation entrypoints
- `30_*` and above: future runtime, API, UI, or agent workflows if they need
  ordered command-line entrypoints

The first automated eval runner is `scripts/20_run_eval.py`. It evaluates
retrieval quality against `data/eval/golden_eval_set.jsonl`.

Retrieval evaluation writes:

- `data/eval/20_retrieval_eval_report.md`
- `data/eval/20_retrieval_eval_results.jsonl`

Command:

```powershell
python scripts/20_run_eval.py
```

This command embeds each eval question and therefore uses the configured paid
embedding provider.

The numbered stages always rebuild their own output folders. The full pipeline
does the same, then embeds into Chroma. There is no incremental/force split.
Ask before running stage 04 chunk embedding, either directly with
`scripts/04_embed_chunks.py` or indirectly through `scripts/00_run_ingestion.py`.

## Supported Source Types

Current source loaders:

- PDF: `app/ingest/loaders/pdf.py`
- HTML/HTM: `app/ingest/loaders/html.py`
- XLSX: `app/ingest/loaders/xlsx.py`
- TXT: `app/ingest/loaders/text.py`
- PNG/JPG/JPEG: `app/ingest/loaders/image.py`

Unsupported files and loader warnings are shown in `data/processed/report.md`.

## Important Concepts

Preview Markdown files are for human inspection. They are generated beside the
machine-readable files for the same stage and are not canonical lineage inputs.

Block JSONL files in `data/processed/02_normalized_blocks/` are the canonical normalized
artifacts. Chunking reads these files.

Chunk JSONL files in `data/processed/03_chunks/` are the embedding-ready artifacts.
Each chunk carries citation-oriented metadata such as `doc_id`, `chunk_id`,
`source_path`, `section_path`, `page`, and `token_count`. Richer
block-level lineage remains in `data/processed/02_normalized_blocks/`.

The local Chroma vector store lives under `data/processed/04_vectorstore/`. It uses
cosine distance through collection metadata `{"hnsw:space": "cosine"}`.

Grounded answer generation reads prompts from `app/prompts/`, calls the existing
retrieval pipeline, and asks the configured `ANSWER_MODEL` to answer only from
the assembled evidence context. The answer layer uses structured model output,
validates citations against assembled evidence IDs, and abstains before answer
generation when reranked evidence is below the current weak-evidence threshold.
OpenAI HTTP clients are built with environment proxy inheritance disabled so
local shell proxy settings do not break query embedding or answer generation.

## Development Notes

This project intentionally favors local/open-source components. OpenAI is used for
embeddings, image vision extraction, and first-pass answer generation where
configured.

Do not add a paid SaaS dependency unless the project explicitly needs it. Keep the
future frontend plain HTML/CSS/JS and the backend Python.

The current project does not use `uv`; use `python -m pip install -e .` unless
`uv` is later added deliberately.
