# Architecture

This project is a local-first RAG demo for a Travel & Expense policy assistant.
The current code builds a searchable policy corpus, assembles citation-ready
retrieval context, and can generate a first-pass grounded natural-language
answer from that evidence.

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
  -> app/retrieval/step01_search_chunks.py
  -> app/retrieval/step02_rerank_chunks.py
  -> app/retrieval/step03_assemble_context.py
  -> citation-ready evidence context

query
  -> app/agents/answer.py
  -> retrieval pipeline
  -> app/prompts/system.md + app/prompts/answer_fewshot.md
  -> structured answer model output
  -> citation and weak-evidence validation
  -> grounded answer with citations, confidence, and abstention state

HTTP request
  -> app/main.py
  -> app/api/chat.py
  -> app/agents/answer.py or app/streaming/chat.py
  -> JSON response or server-sent events

Browser
  -> app/main.py
  -> app/ui/index.html + app/ui/app.js + app/ui/styles.css
  -> POST /api/chat/stream
  -> streaming answer and retrieval debug panel

data/eval/golden_eval_set.jsonl
  -> app/eval/step01_run_retrieval_eval.py
  -> data/eval/20_retrieval_eval_results.jsonl
  -> data/eval/20_retrieval_eval_report.md
```

## Runtime Boundaries

`app/core/config.py` owns configuration loading. It loads `.env` from the project
root and resolves relative configured paths from the project root.

`app/core/openai_clients.py` builds OpenAI HTTP clients for LangChain/OpenAI
calls with environment proxy inheritance disabled. This keeps local shell proxy
variables from breaking query embedding, answer generation, image extraction,
or embedding rebuilds.

`app/ingest/` owns ingestion, source normalization, block artifacts, chunking, and
embedding.

`app/retrieval/` owns local vector search, reranking, and context assembly.

`app/agents/` owns the first answer-generation orchestration path.

`app/prompts/` stores Markdown prompts for grounded answer generation.

`app/eval/` owns evaluation runners and report generation.

`app/api/` owns the FastAPI route layer and request/response schemas.

`app/streaming/` owns transport-agnostic server-sent event helpers for streaming
grounded answers.

`app/tools/` owns deterministic helper tools. It includes currency conversion,
claim eligibility evaluation, and evidence completeness checking. These tools
consume structured claim facts and retrieved policy facts; they do not retrieve
policy or decide conversation flow.

`app/ui/` owns the static browser UI. FastAPI serves it under `/ui/`, and the
root URL redirects there. The UI uses plain HTML/CSS/JS and consumes
`POST /api/chat/stream` with the Fetch streaming API so it can send JSON request
filters in the future while rendering server-sent events.

`scripts/` contains the command-line entrypoints that call application modules.
`scripts/01_load_documents.py` through `scripts/04_embed_chunks.py` run the
build stages individually. `scripts/00_run_ingestion.py` runs the numbered
ingestion flow from raw files through vector-store embedding. Search remains a
separate retrieval script.
The scripts should stay thin.

Script numbering is grouped by workflow band:

- `00_*`: orchestration scripts that run multiple numbered stages
- `01_*` through `09_*`: corpus-build stages, from raw source files to indexes
- `10_*` through `19_*`: retrieval and retrieval-debug entrypoints
- `20_*` through `29_*`: evaluation entrypoints
- `30_*` and above: future runtime, API, UI, or agent workflows if they need
  ordered command-line entrypoints

Following that convention, the automated retrieval eval runner is
`scripts/20_run_eval.py`.

`scripts/30_ask.py` runs retrieval and OpenAI-backed answer generation. It uses
the `30_*` band because it is a runtime/copilot workflow rather than corpus
build, retrieval debug, or evaluation.

## Current Modules

`app/core/config.py` defines the `Settings` dataclass and `get_settings()` cache.
Required settings come from environment variables, usually via `.env`.

`app/core/openai_clients.py` centralizes OpenAI HTTP client construction. The
retrieval, answer, streaming, embedding, and image extraction modules use it
when constructing LangChain OpenAI models or embeddings.

`app/ingest/step01_load_documents.py` discovers raw files and writes
loaded-document inspection JSONL plus readable previews. PDF, HTML, and TXT use
LangChain community loaders. XLSX and images use the project loaders so source
coverage stays aligned with production behavior.

`app/ingest/step02_normalize_blocks.py` normalizes supported sources into block
JSONL and readable block previews. Image normalization reuses the stage 01 image
text when available to avoid duplicate image extraction in a normal pipeline run.

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
are assembled into Markdown so headings and source citation metadata carry into
chunks.

`app/ingest/step04_embed_chunks.py` reads chunk JSONL files and embeds chunk text into
local Chroma. It builds a temporary collection first and promotes it only after
count verification.

`app/ingest/pipeline_report.py` writes `data/processed/report.md` from the
current numbered artifacts and warnings. The pipeline no longer writes
`ingest_manifest.jsonl` or `ingest_warnings.jsonl`.

`app/retrieval/step01_search_chunks.py` opens Chroma, embeds the query,
retrieves chunks, and supports exact-match filters for `doc_type`,
`source_path`, and `section_path`.

`app/retrieval/step02_rerank_chunks.py` reranks retrieved candidates with local
FlashRank.

`app/retrieval/step03_assemble_context.py` selects diverse chunks, applies token
budgets, and formats evidence blocks with citation IDs and retrieval metadata.

`app/agents/answer.py` orchestrates retrieve, rerank, assemble context, and
generate answer. It calls OpenAI through `langchain-openai`, so normal execution
performs a paid answer-generation model call in addition to the retrieval query
embedding. `ANSWER_MODEL` must be set in the environment; the runtime no longer
falls back to a built-in answer-model default. Model output is constrained with
LangChain structured output and Pydantic, then validated against the assembled
evidence citation IDs. If evidence is below the weak-evidence threshold, or if
the model output fails validation, the answer layer abstains instead of
returning an unsupported answer.

`app/api/chat.py` exposes the implemented HTTP runtime routes. `GET /health`
returns liveness only. `POST /api/chat` returns one validated grounded answer.
`POST /api/chat/stream` returns server-sent events for retrieval progress,
answer deltas, and the final validated answer payload.

`app/api/schemas.py` defines the Pydantic request and response models used by
the API routes.

`app/streaming/chat.py` runs the same retrieval and answer-generation flow for
streaming callers. It streams answer text from the model's JSON `answer` field,
then parses and validates the final model JSON before emitting the final answer
payload.

`app/streaming/sse.py` formats event names and JSON payloads as server-sent
events.

`app/ui/index.html`, `app/ui/styles.css`, and `app/ui/app.js` implement the
minimal browser UI. The UI renders streamed answer deltas, citation and
confidence metadata, retrieved evidence blocks, rerank scores, validation
warnings, assembled retrieval context, and clickable example questions. The
file upload control is present but disabled until an upload route exists.

`app/tools/currency.py` converts amounts between currencies for future claim
evaluation. It first uses the `ExchangeRates` sheet in
`data/raw/per_diem_caps.xlsx`; if no usable company rate exists, it can fall
back to Frankfurter's free exchange-rate API. It does not make reimbursement
eligibility decisions and is not yet wired into the answer agent.

`app/tools/models.py` defines shared typed claim and policy-fact models.
`app/tools/evidence.py` checks whether required claim evidence is present and
returns missing fields, manual-review reasons, and clarification questions.
`app/tools/eligibility.py` applies deterministic claim arithmetic and policy
facts to structured claim lines. It can include an evidence completeness result
when evidence policy facts are supplied. These tools are not yet wired into the
answer agent, API, or UI.

`app/prompts/system.md` defines the grounded-answering contract.
`app/prompts/answer_fewshot.md` defines the first answer JSON schema and
citation/abstention examples.

`app/eval/step01_run_retrieval_eval.py` reads the golden eval set, runs the
current retrieval flow, checks whether required sources appear in retrieved,
reranked, and assembled-context results, and writes Markdown plus JSONL reports.
It embeds each eval question through the retrieval stack, so normal execution
uses the configured paid embedding provider.

## Code Documentation Conventions

Every Python module should start with a short top-level module docstring. In this
project, a module means a single `.py` file, such as
`app/ingest/step01_load_documents.py` or `scripts/10_retrieve_context.py`.

Module docstrings should make the file understandable at a glance. They should
describe the module's role in the pipeline, the artifacts it reads or writes, and
important boundaries such as stage 04 chunk embedding or planned-only scaffolds.

Examples of the current convention:

- pipeline modules state which pipeline stage they own and what they do not do
- loader modules state the source type, extraction strategy, and metadata they
  preserve
- retrieval modules state whether they perform query embedding, local reranking,
  or citation-ready context assembly
- scripts state the command purpose and whether normal execution runs stage 04
  chunk embedding

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
a compact citation-oriented metadata set from normalized blocks.

`data/processed/03_chunks_preview/` contains readable chunk previews.

`data/processed/04_vectorstore/` contains the local Chroma database.

`data/processed/report.md` summarizes stage outputs and warnings.

`data/eval/` contains golden evaluation examples and retrieval eval outputs.

## Planned Boundaries

These boundaries are planned by project rules but not yet implemented:

- MCP server code should live in `mcp_server/`.
- Business logic should not be placed directly in API route files.

## Current Limitations

The current answer generator is a first-pass implementation. It has no
tool-calling loop, no retry/repair loop for invalid model output, and no judge
step.

There is no judge step and no independent confidence explanation beyond the
answer model's structured `confidence` field plus the deterministic
weak-evidence cutoff.

The browser UI currently supports streaming chat and retrieval debugging. It
does not have a working upload workflow; the file input is visible but disabled
until an upload route exists.

There is no answer-level eval runner yet.
