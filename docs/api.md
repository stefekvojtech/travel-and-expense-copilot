# API and UI Status

The API and UI are not yet developed.

This file documents the intended boundaries so future work has a clear place to
land.

## Current State

`app/api/` exists as an empty scaffold, but it contains no route modules yet.

There is no `app/main.py`.

There is no FastAPI application.

There is no browser UI.

There is no file-upload endpoint.

There is no streaming answer endpoint.

There is no answer-generation route.

`app/agents/`, `app/prompts/`, `app/tools/`, `app/ui/`, and `app/streaming/`
also exist as empty scaffolds.

The current way to use the project is through scripts in `scripts/`.
`python scripts/pipeline.py` rebuilds the corpus from raw files through Chroma
embedding. Retrieval is run separately with `python scripts/search_chunks.py`.

## Expected Future API Shape

When implemented, API routes should live under:

```text
app/api/
```

Business logic should remain in reusable modules, not directly inside route files.
Routes should call ingestion, retrieval, answer generation, tools, and judge
modules through small interfaces.

Likely future routes:

- health/status route
- file upload route
- chat or ask route
- streaming answer route
- debug retrieval route
- source/citation inspection route

The exact route names are not decided yet.

## Expected Future UI Shape

The frontend should stay minimal and use plain HTML/CSS/JS.

Required elements:

- chat input
- send button
- file upload
- streaming answer panel

Strongly preferred debug fields:

- retrieved chunks
- rerank scores
- citations
- tool calls
- confidence
- judge result

No React, Vue, Next.js, or similar frontend framework is planned.

## Expected Future Prompt Files

Prompt files should live under:

```text
app/prompts/
```

Planned files:

- `system.md`
- `router_fewshot.md`
- `answer_fewshot.md`
- `judge_fewshot.md`

These files are not yet developed.

## Expected Future Agent and Tool Layer

Agent logic should live under:

```text
app/agents/
```

Direct Python or LangChain tools should eventually include:

- `search_policy_corpus`
- `fetch_source_window`
- `explain_confidence`

Local MCP server code should live under:

```text
mcp_server/
```

Planned MCP tools:

- `compute_per_diem`
- `policy_cap_lookup`
- `sum_receipt_lines`
- `normalize_currency`

None of these tools are developed yet.

## Guardrails Not Yet Developed

Planned guardrails:

- redact obvious PII before model calls where practical
- sanitize HTML before indexing
- prevent retrieved documents from overriding system behavior
- abstain when evidence is weak
- judge generated answers for unsupported claims
- use deterministic tools for arithmetic instead of an LLM

The current code has only partial groundwork. HTML loading strips `script` and
`style`, but full sanitization and prompt-injection handling are not implemented.
