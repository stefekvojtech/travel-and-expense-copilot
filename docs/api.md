# API, UI, and Answer Status

The API and UI are not yet developed.

This file documents the current script-level answer path and the intended API/UI
boundaries so future work has a clear place to land.

## Current State

`app/api/` exists as an empty scaffold, but it contains no route modules yet.

There is no `app/main.py`.

There is no FastAPI application.

There is no browser UI.

There is no file-upload endpoint.

There is no streaming answer endpoint.

There is no answer-generation route. First-pass answer generation is available
through `app/agents/answer.py` and `scripts/30_ask.py`.

`app/tools/`, `app/ui/`, and `app/streaming/` exist as empty scaffolds.
`app/agents/` and `app/prompts/` now contain the script-level grounded answer
implementation. That answer path uses structured model output, validates
citations against assembled evidence IDs, fails closed on invalid model output,
and abstains when evidence is below the weak-evidence threshold.

The current way to use the project is through scripts in `scripts/`.
`python scripts/00_run_ingestion.py` rebuilds the corpus from raw files through
Chroma embedding. Retrieval is run separately with
`python scripts/10_retrieve_context.py`. First-pass grounded answers are run with
`python scripts/30_ask.py`.

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

`system.md` and `answer_fewshot.md` are implemented for the first answer path.
Router and judge prompts are still planned.

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
- judge generated answers for unsupported claims
- use deterministic tools for arithmetic instead of an LLM

The current code has only partial groundwork. HTML loading strips `script` and
`style`, the answer prompt says retrieved documents cannot override system
behavior, and the answer layer has a deterministic weak-evidence abstention
cutoff. Full sanitization, PII redaction, prompt-injection handling, judge
review, and deterministic arithmetic tools are not implemented.
