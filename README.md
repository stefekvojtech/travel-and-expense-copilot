---
title: "Travel & Expense Policy Copilot"
sdk: docker
app_port: 7860
---

# Travel & Expense Policy Copilot

**Live demo:** [Try the Hugging Face Space](https://huggingface.co/spaces/stefekvojtech/travel-and-expense-copilot)

A grounded RAG demo for answering travel and expense policy questions from a
synthetic company policy corpus.

This is a personal portfolio project. It is built to make the RAG lifecycle
inspectable: ingestion, normalization, chunking, embedding, retrieval,
reranking, citation assembly, answer generation, API routes, and a small browser
UI all live in one repository. That is useful for a demo and for reviewing the
implementation, but it is not the architecture I would present as a standard
enterprise deployment pattern.

In a production enterprise setup, corpus preparation, index management,
application runtime, observability, access control, and evaluation would usually
be split across clearer service and data boundaries. This repo keeps them close
so the full flow can be read, run, and improved in one place.

## Hosted Demo vs Local Repo

The hosted Hugging Face Space is the easiest way to try the project. It exposes
the retrieval and answering experience through the browser UI using a prebuilt
Chroma vector store committed with the repo.

The hosted demo does not run ingestion, rebuild embeddings, run evals, or accept
new source documents from users. Those workflows are local developer workflows
handled by repository scripts.

Use the two modes like this:

- **Hosted demo:** ask questions against the prebuilt synthetic travel and
  expense corpus.
- **Local repo:** inspect the code, rebuild the corpus, run retrieval/debug
  scripts, run evals, and develop new features.

## Demo Data Disclaimer

The policy corpus is for a fictional company named **Atlas Mobility Group**.
The source files under `data/raw/` are synthetically generated demo materials.

The project is not affiliated with, endorsed by, or intended to impersonate any
real company. Any match with an existing organization, policy, document, name,
or internal process is coincidental. The generated policy content is for software
demonstration only and should not be used as legal, HR, tax, finance, or
compliance advice.

## What It Can Do Today

- Answer English travel and expense policy questions from retrieved evidence.
- Stream the answer in the browser UI.
- Show citations, confidence, retrieved evidence, rerank scores, and assembled
  context in a debug panel.
- Use FastAPI routes for non-streaming and streaming chat responses.
- Build a local policy corpus from PDF, HTML, XLSX, TXT, and image sources.
- Store embeddings in a local Chroma vector store.
- Rerank retrieved candidates locally with FlashRank.
- Run retrieval evaluation against a small golden dataset.
- Use deterministic helper tools for currency conversion, evidence completeness,
  and claim eligibility logic, with full agent tool-calling still planned.

## Current Limitations

- English only.
- No persistent chat history.
- No user file upload or ingestion flow in the hosted demo.
- Hosted demo uses a fixed prebuilt corpus and vector store.
- Public demo mode applies simple guardrails: question length cap, answer token
  cap, fixed retrieval fanout, safe errors, and rate limiting.
- Answer generation is a first-pass grounded-answer flow, not a full agent loop.
- Judge/faithfulness checks and answer-level regression evals are not implemented
  yet.
- The project is still evolving and is not a final architecture or final UX.

## How It Works

```text
synthetic source files
  -> load documents
  -> normalize into canonical blocks
  -> chunk for retrieval
  -> embed into Chroma
  -> search + rerank
  -> assemble citation-ready context
  -> generate a grounded answer
  -> stream through FastAPI + browser UI
```

The hosted Space starts at the retrieval/answering part of this flow. It reads
the existing vector store from `data/processed/04_vectorstore/`; it does not
rebuild the corpus at startup.

## Try It Locally

Use Python 3.11 or newer. From the repository root:

```powershell
python -m pip install -e .
python -m uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/ui/
```

Create a local `.env` only when you need to override defaults or set
`OPENAI_API_KEY` for OpenAI-backed embedding, image extraction, retrieval, or
answer generation. The app has built-in defaults for non-secret settings shown
in `.env.example`.

Both local answer generation and some build/eval scripts can use paid OpenAI
API calls when configured.

## Main Scripts

The numbered scripts are thin command-line entrypoints over application modules.

Common local commands:

```powershell
python scripts/00_run_ingestion.py
python scripts/10_retrieve_context.py "Can I take a taxi from Prague airport after 21:00?"
python scripts/20_run_eval.py
python scripts/30_ask.py "Can I take a taxi from Prague airport after 21:00?"
```

High-level script groups:

- `00_*`: run multiple build stages.
- `01_*` through `09_*`: ingestion and corpus-build stages.
- `10_*` through `19_*`: retrieval and retrieval-debug commands.
- `20_*` through `29_*`: evaluation commands.
- `30_*` and above: runtime answer/demo commands.
- `deploy_hf_space.py`: publish the committed snapshot to Hugging Face Spaces.

See [Scripts](docs/scripts.md) for the full script map, paid-call notes, and
hosted-vs-local boundaries.

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
  raw/                  Synthetic demo source documents
  processed/            Generated artifacts and Chroma store
  eval/                 Golden evaluation examples
scripts/                CLI entrypoints and deployment helper
docs/                   Human documentation
AGENTS.md               Agent-facing project instructions
pyproject.toml          Package metadata and dependencies
```

## Documentation

Start here, then go deeper as needed:

- [Architecture](docs/architecture.md)
- [Ingestion](docs/ingestion.md)
- [Retrieval](docs/retrieval.md)
- [API and UI Status](docs/api.md)
- [Scripts](docs/scripts.md)
- [Deployment](docs/deployment.md)
- [Evaluation](docs/evaluation.md)
- [Deterministic Tools](docs/tools.md)
- [Future Improvements](docs/future_improvements.md)

`AGENTS.md` contains project rules and development constraints for coding agents.
The docs in `docs/` explain the project for humans working in the repo.

## Development Notes

This project intentionally favors local/open-source components where practical.
OpenAI is used for embeddings, image vision extraction, and first-pass answer
generation where configured.

The current project does not use `uv`; use `python -m pip install -e .` unless
`uv` is later added deliberately.

The project is a living demo. I expect to keep improving retrieval quality,
evaluation coverage, guardrails, tool use, UX, and deployment ergonomics over
time.

Code review notes PR.