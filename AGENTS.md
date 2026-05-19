# AGENTS.md

## Mission

Build a local-first, grounded Travel & Expense Policy Copilot in Python.

The project is a learning/demo RAG system for practicing ingestion, chunking,
embeddings, retrieval, citations, deterministic tools, and evaluation.

## Navigation

This file contains project-wide rules. More specific `AGENTS.md` files in
subdirectories describe local ownership and expectations. When editing inside a
subdirectory, read the closest `AGENTS.md` and apply it together with this file.

Human-facing documentation lives in `README.md` and `docs/`. When behavior
changes, update the relevant docs in the same change. If behavior is only
planned, label it as planned or not yet developed.

## Global Rules

- Keep the backend in Python.
- Keep the frontend minimal and plain HTML/CSS/JS.
- Prefer local and open-source components unless OpenAI is explicitly required.
- Do not add paid SaaS dependencies other than approved OpenAI API usage.
- Do not run paid OpenAI chat, embedding, or vision calls without explicit user
  permission.
- Do not hardcode secrets.
- Do not replace the travel and expense policy use case with another domain.
- Do not stage or commit unrelated existing work.
- Never track, stage, or commit any `AGENTS.md` file.
- Do not change `.gitignore` unless explicitly requested.
- Explain beginner-facing Python, packaging, RAG, and architecture decisions
  clearly and concretely.
- Distinguish between implemented behavior, planned behavior, and temporary
  demo shortcuts.

## Architecture Boundaries

- `app/core/`: settings and project-root path resolution.
- `app/ingest/`: raw ingestion, loader dispatch, chunking, and embedding.
- `app/ingest/loaders/`: reusable file-type normalization strategies.
- `app/retrieval/`: vector search, local reranking, and evidence context assembly.
- `app/api/`: API routes.
- `app/prompts/`: prompt Markdown files.
- `app/agents/`: agent orchestration.
- `app/tools/`: deterministic Python tools.
- `app/ui/`: minimal browser UI.
- `app/streaming/`: streaming helpers.
- `scripts/`: thin CLI entrypoints over application modules.
- `data/`: raw corpus, generated artifacts, and golden eval examples.
- `docs/`: human-facing documentation.

Do not place business logic directly in API route files or scripts. Keep
ingestion, retrieval, agent, prompt, tool, and UI behavior inside their owning
packages.

## RAG And Grounding Rules

- Every chunk must carry metadata and lineage.
- Preserve citation lineage when touching ingestion, retrieval, or answering.
- Do not generate final policy answers directly from the user question once
  answer generation exists; retrieval must happen first.
- Every final grounded answer must include citations and confidence once answer
  generation is implemented.
- Every grounded answer should pass through a judge step once judge flow is
  implemented.
- If evidence is weak, abstain instead of guessing.
- Use deterministic code for arithmetic and policy-cap lookup instead of an LLM.

## Code Quality

- Use type hints where reasonable.
- Every Python module should have a concise top-level module docstring explaining
  the file's role.
- Keep module docstrings factual and specific to implemented behavior.
- Prefer small testable functions.
- Prefer Pydantic models for API request/response schemas once API work begins.
- Add docstrings to tools and MCP tools.
- Keep `.env.example` updated when config changes.
- Avoid pointless rewrites of generated files; write only when content changes
  where practical.

## Documentation MCP Usage

Use official documentation MCPs before general web search:

- Use `langchain-docs` for LangChain, LangGraph, LangSmith, and related `lang*`
  packages.
- Use `microsoft-learn` for Semantic Kernel, Azure SDKs, Azure AI, .NET, and
  other Microsoft platform work.
- Use `context7` as a secondary documentation check when implementation details
  are uncertain or external package behavior may be stale.

## Current Setup

Install the project from the repository root with:

```powershell
python -m pip install -e .
```

`uv` is not currently available in this environment. Do not assume `uv sync`
works unless `uv` is installed.

## Done Criteria

A task is not done until:

- the code runs locally, or any reason it cannot run is clearly stated
- relevant compile checks, tests, or scripts pass
- the feature respects repository architecture
- grounding and citation behavior are preserved when touching retrieval or answer
  generation
- UI streaming still works if runtime UI behavior is touched
- README, docs, `.env.example`, or inline docs are updated when behavior changes
- paid model calls were avoided unless explicitly approved
