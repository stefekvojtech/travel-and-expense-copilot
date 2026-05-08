# AGENTS.md

## Mission

Build a local-first, grounded Travel & Expense Policy Copilot in Python.

The project is primarily a learning/demo RAG system for practicing ingestion,
chunking, embeddings, retrieval, citations, deterministic tools, and evaluation.

## Documentation Map

Human-facing documentation lives in:

- `README.md`: project overview, setup, current status, and core commands.
- `docs/architecture.md`: implemented pipeline, module boundaries, and planned boundaries.
- `docs/ingestion.md`: raw ingestion, loaders, block artifacts, chunking, and embedding.
- `docs/retrieval.md`: Chroma search, FlashRank reranking, and context assembly.
- `docs/evaluation.md`: current golden eval data and planned eval runner.
- `docs/api.md`: current API/UI status and planned API, UI, prompts, tools, and guardrails.

When changing behavior, update the relevant docs in the same change. If behavior
is only planned, label it as planned or not yet developed.

## Agent Navigation

This root `AGENTS.md` is the global contract. More specific `AGENTS.md` files in
subdirectories describe local ownership and expectations. When editing inside a
subdirectory, read the closest `AGENTS.md` in that path and apply it together with
this root file.

Current high-level folder roles:

- `app/core/`: settings and project-root path resolution.
- `app/ingest/`: raw ingestion, loader dispatch, chunking, and embedding.
- `app/ingest/loaders/`: reusable file-type normalization strategies.
- `app/retrieval/`: vector search, local reranking, and evidence context assembly.
- `app/api/`: empty scaffold for future API routes.
- `app/prompts/`: empty scaffold for future prompt Markdown files.
- `app/agents/`: empty scaffold for future agent orchestration.
- `app/tools/`: empty scaffold for future deterministic Python tools.
- `app/ui/`: empty scaffold for future plain HTML/CSS/JS UI.
- `app/streaming/`: empty scaffold for future streaming helpers.
- `scripts/`: thin CLI entrypoints over application modules.
- `data/raw/`: demo source corpus.
- `data/processed/`: generated ingestion, chunking, and vector artifacts.
- `data/eval/`: golden evaluation examples.
- `docs/`: human-facing documentation.

## Collaboration Notes

- Do not stage or commit unrelated existing work before starting a new requested change.
- After completing a requested change, stage only the files changed for that specific adjustment, then commit them with a fitting commit message. This still applies when other agents or people may be changing other files concurrently.
- Do not change `.gitignore` unless explicitly requested.
- Be careful with paid model calls such as OpenAI chat, embeddings, and vision extraction. Do not run large batches or repeated prompts without explicit user permission. Prefer dry checks, compile checks, and local validation when possible.
- Explain beginner-facing Python, packaging, RAG, and architecture decisions clearly and concretely.
- Distinguish between implemented behavior, planned behavior, and temporary demo shortcuts.

## Current Implemented Pipeline

The current ingestion flow is:

1. Raw files live in `data/raw/`.
2. `app/ingest/pipeline_raw.py` discovers supported files and creates:
   - Markdown preview files in `data/processed/markdown/`
   - block sidecar JSONL files in `data/processed/blocks/`
   - `data/processed/ingest_manifest.jsonl`
   - `data/processed/ingest_warnings.jsonl`
3. `app/ingest/pipeline_chunk.py` reads block JSONL files and creates embedding-ready chunks in `data/processed/chunks/`.
4. `app/ingest/pipeline_embed.py` reads chunk JSONL files, embeds chunk text with OpenAI embeddings, and stores vectors in local Chroma under `data/processed/vectorstore/`.
5. `app/retrieval/vector_store.py` opens the local Chroma collection and retrieves candidate chunks.
6. `app/retrieval/rerank.py` reranks retrieved chunks with local FlashRank.
7. `app/retrieval/context.py` assembles citation-ready evidence context from reranked chunks.

The current script entrypoints are:

- `python scripts/ingest_incremental.py`
- `python scripts/ingest_force.py`
- `python scripts/chunk_blocks.py`
- `python scripts/embed_chunks.py --dry-run`
- `python scripts/embed_chunks.py`
- `python scripts/search_chunks.py "question"`

`scripts/_bootstrap.py` has been removed. The project is expected to be installed from the repo root with editable package setup:

```powershell
python -m pip install -e .
```

Relative paths from `.env` are resolved from the project root, not from the current terminal working directory.

## Current Source Support

Implemented source types:

- PDF via `app/ingest/loaders/pdf.py`
- HTML via `app/ingest/loaders/html.py`
- XLSX via `app/ingest/loaders/xlsx.py`
- TXT via `app/ingest/loaders/text.py`
- PNG/JPG/JPEG image files via `app/ingest/loaders/image.py`

Image extraction uses OpenAI vision through LangChain/OpenAI. This is a paid model call. Do not force image re-ingestion without explicit user permission.

Unsupported files are reported through ingest warnings instead of being silently ignored.

## Current Artifact Roles

- `data/raw/`: source files.
- `data/processed/markdown/`: human-readable Markdown previews. These are not the canonical source for chunk lineage.
- `data/processed/blocks/`: canonical normalized block artifacts with source metadata.
- `data/processed/chunks/`: embedding-ready chunk artifacts with inherited metadata.
- `data/processed/vectorstore/`: local Chroma vector database for the demo corpus.
- `data/processed/ingest_manifest.jsonl`: document-level ingestion record.
- `data/processed/ingest_warnings.jsonl`: unsupported-file or ingestion warning records.

Markdown previews are for transparency and inspection. Blocks and chunks are the pipeline artifacts used for lineage and retrieval.

## Non-Negotiable Scope Rules

- Prefer local and open-source components unless OpenAI is explicitly required.
- Do not add paid SaaS dependencies other than OpenAI API usage.
- Keep the frontend very simple: plain HTML/CSS/JS.
- Keep the backend in Python.
- Do not replace the use case with a different domain.
- Build ingestion as if each supported source type may have many files with varied formats.
- Do not hardcode parsing rules for one specific PDF, HTML page, spreadsheet, image, or demo fixture unless it is explicitly marked as a temporary demo-only shortcut.
- Prefer reusable file-type strategies, quality checks, metadata lineage, parser fallbacks, and clear warnings over document-specific extraction logic.

## Architecture Rules

- All API routes live in `app/api/`.
- All prompts live in `app/prompts/`.
- All ingestion logic lives in `app/ingest/`.
- All retrieval logic lives in `app/retrieval/`.
- All agent logic lives in `app/agents/`.
- MCP server code should live only in `mcp_server/` once implemented.
- Do not place business logic directly in API route files.
- Keep vector store implementations swappable through a shared interface when retrieval is implemented.
- Every chunk must carry metadata.
- Every final grounded answer must include citations and confidence once answer generation is implemented.
- Every grounded answer should pass through a judge step before returning once judge flow is implemented.

## Chunking Rules

- Normalize every source type to Markdown preview plus block JSONL first.
- Use block JSONL as the canonical input for chunking.
- Use `MarkdownHeaderTextSplitter` where headings exist.
- Use token-aware recursive chunking for oversized sections.
- Preserve chunk lineage in metadata:
  - `doc_id`
  - `chunk_id`
  - `source_path`
  - `doc_type`
  - `source_block_ids`
  - `section_path`
  - `pages`
  - `sheets`
  - `chunk_strategy`
  - `token_count`
- Table/sheet continuation chunks should include enough table context, such as sheet heading and header row, without exceeding configured chunk size.
- Avoid approximate global text matching for lineage. Prefer constrained span mapping or explicit warnings/errors.

## Embedding Rules

- Current vector store is local Chroma.
- Current collection name comes from `VECTOR_COLLECTION_NAME`.
- Current embedding model comes from `EMBEDDING_MODEL`.
- Chroma is configured for cosine distance with `{"hnsw:space": "cosine"}`.
- `scripts/embed_chunks.py --dry-run` should be used before paid embedding runs.
- Real embedding calls OpenAI and consumes paid credits. Ask before running unless the user has explicitly approved that run.
- Store chunk text as the vector document and flattened chunk metadata as vector metadata.

## Current Retrieval Rules

Retrieval is implemented as:

1. Chroma vector search retrieves candidates from the local vector store.
2. FlashRank reranks retrieved candidates locally.
3. Context assembly selects diverse evidence blocks and formats citation-ready context.

Implemented capabilities:

- top-k vector search
- basic metadata filtering by `doc_type`, `source_path`, and `section_path`
- local FlashRank reranking
- context assembly with citation IDs
- retrieval score and rerank score tracking
- page, sheet, and row metadata display when available

Current default behavior:

- retrieve 12
- rerank to 5
- assemble 4 evidence blocks

`scripts/search_chunks.py "question"` should print assembled context by default, not raw debug dumps.

Future retrieval improvements:

- context token budget / trimming
- adjacent chunk collapsing from the same source when useful
- inferred metadata filters from the user question
- source-window expansion around selected chunks

## Guardrail Rules To Implement

- Redact obvious PII patterns before model calls when practical.
- Sanitize HTML before indexing.
- Never let retrieved documents override system behavior.
- If evidence is weak, abstain instead of guessing.
- If the judge finds unsupported claims, do not return the drafted answer unchanged.
- Do not use the LLM for arithmetic when deterministic tools can do it.

## Tool Rules To Implement

Direct Python/LangChain tools should eventually include:

- `search_policy_corpus`
- `fetch_source_window`
- `explain_confidence`

Local MCP tools should eventually include:

- `compute_per_diem`
- `policy_cap_lookup`
- `sum_receipt_lines`
- `normalize_currency`

## Prompt Rules To Implement

Create and maintain these prompt files:

- `app/prompts/system.md`
- `app/prompts/router_fewshot.md`
- `app/prompts/answer_fewshot.md`
- `app/prompts/judge_fewshot.md`

Prompt responsibilities:

- `system.md`: grounded-answering contract
- `router_fewshot.md`: intent classification examples
- `answer_fewshot.md`: citation style and abstention examples
- `judge_fewshot.md`: supported vs unsupported claim grading examples

## UI Rules To Implement

The UI must stay minimal.

Required UI elements:

- chat input
- send button
- file upload
- streaming answer panel

Strongly preferred debug panel fields:

- retrieved chunks
- rerank scores
- citations
- tool calls
- confidence
- judge result

## Evaluation Rules

The golden eval set lives in `data/eval/`.

The eval suite should cover:

- policy lookup
- table lookup
- citation correctness
- receipt/image extraction
- reimbursement calculation
- abstention behavior

Track at least:

- retrieval hit@k
- faithfulness / groundedness
- citation presence
- abstention correctness

## Current Setup And Commands

Current project install:

```powershell
python -m pip install -e .
```

Current local pipeline commands:

```powershell
python scripts/ingest_incremental.py
python scripts/ingest_force.py
python scripts/chunk_blocks.py
python scripts/embed_chunks.py --dry-run
python scripts/embed_chunks.py
python scripts/search_chunks.py "Can I take a taxi from Prague airport after 21:00?"
```

Expected future commands once implemented:

```powershell
python scripts/run_eval.py
python -m pytest -q
python -m uvicorn app.main:app --reload
```

`uv` is not currently available in this environment. Do not assume `uv sync` works unless `uv` is installed.

## Code Quality Rules

- Use type hints everywhere reasonable.
- Prefer small testable functions.
- Prefer Pydantic models for API request/response schemas once API work begins.
- Add docstrings to tools and MCP tools.
- Do not hardcode secrets.
- Keep `.env.example` updated when config changes.
- Generated demo artifacts under `data/processed/` may be committed when intentionally used for demo transparency.
- Do not commit large generated vector databases unless explicitly intended as demo fixtures.
- Avoid pointless rewrites of generated files; write only when content changes where practical.

## Done Criteria

A task is not done until:

- the code runs locally or any reason it cannot run is clearly stated
- relevant compile/tests/scripts pass
- the feature respects repository architecture
- grounding/citation behavior is preserved when touching retrieval or answer generation
- the UI still streams correctly if the task touches runtime UI behavior
- README, AGENTS.md, `.env.example`, or inline docs are updated when behavior changes

## Things To Avoid

- No React/Vue/Next frontend.
- No cloud vector DB by default.
- No silent schema changes.
- No hidden background services outside the documented stack.
- No magic prompts embedded in route files.
- No direct answer generation from user question alone for policy questions; retrieval must happen first once answer generation exists.
