# API, UI, and Answer Status

The project now has a first FastAPI backend for grounded answer generation and a
minimal browser UI for streaming chat. The upload route, agent tool-calling
loop, and judge flow are still not implemented. Standalone deterministic tools
exist under `app/tools/`, but they are not wired into the API or answer agent.

## Current API

The FastAPI app entrypoint is:

```text
app/main.py
```

Run it locally with:

```powershell
python scripts/run_local_server.py
```

The launcher binds only to localhost, reloads after code changes, and opens the
browser UI at:

```text
http://127.0.0.1:8000/ui/
```

Implemented routes:

- `GET /health`
- `GET /api/ui/config`
- `POST /api/chat`
- `POST /api/chat/stream`
- `GET /api/downloads/raw-data.zip`

Routes live in `app/api/`. Pydantic request and response models live in
`app/api/schemas.py`. Route handlers stay thin and call reusable answer and
streaming modules. Every new API endpoint should be added with focused endpoint
tests under `tests/`; tests for paid or stateful paths should monkeypatch the
retrieval/model layer instead of making real OpenAI, Chroma, or reranker calls.

## Health Route

`GET /health` returns a minimal liveness response:

```json
{
  "status": "ok",
  "app": "travel-and-expense-copilot"
}
```

It does not currently check Chroma, OpenAI credentials, or model availability.

## UI Config Route

`GET /api/ui/config` returns non-sensitive author metadata used by the static
browser UI footer:

```json
{
  "author_name": "Vojtech Stefek",
  "author_linkedin_url": "https://www.linkedin.com/in/vojtech-stefek/",
  "author_github_url": "https://github.com/stefekvojtech"
}
```

The values come from `AUTHOR_NAME`, `AUTHOR_LINKEDIN_URL`, and
`AUTHOR_GITHUB_URL`.

## Raw Data Download Route

`GET /api/downloads/raw-data.zip` returns a ZIP archive of files from
`data/raw/`, excluding local `AGENTS.md` instruction files. The browser UI links
to this route with a `Download source files` button in the debug panel header.

## Public Demo Mode

`PUBLIC_DEMO_MODE=false` is the local default. Hosted public demos should set
`PUBLIC_DEMO_MODE=true` in the deployment environment. In demo mode, the chat
routes apply a per-client-IP limit of `PUBLIC_DEMO_RATE_LIMIT_REQUESTS` requests
per `PUBLIC_DEMO_RATE_LIMIT_WINDOW_SECONDS` seconds and return generic server
errors instead of raw exception text. The default public limit is 10 requests
per 10 minutes.

The chat request schema rejects questions longer than 1000 characters. The
browser input also caps entry at 1000 characters, but the API validation is the
authoritative protection for programmatic callers.

Caller-provided `search_k` values are accepted for request-shape compatibility
but ignored by the route layer. Runtime chat always uses the configured
`RETRIEVAL_TOP_K` default.

## Chat Route

`POST /api/chat` runs the full grounded answer path:

```text
question
  -> Chroma vector search
  -> FlashRank reranking
  -> citation-ready context assembly
  -> OpenAI-backed answer generation
  -> citation validation and weak-evidence checks
  -> JSON response
```

Example request:

```json
{
  "question": "Can I take a taxi from Prague airport after 21:00?",
  "search_k": 12,
  "filters": {
    "doc_type": "pdf",
    "source_path": null,
    "section_path": null
  }
}
```

`search_k` and `filters` are optional. Filters support exact matches for
`doc_type`, `source_path`, and `section_path`. Current API route behavior
ignores `search_k` and uses `RETRIEVAL_TOP_K` from settings so public callers
cannot increase vector-search fanout.

The response includes:

- `answer`
- `citations`
- `confidence`
- `abstained`
- `evidence_blocks`
- `judge_result`
- `debug`

`judge_result` is currently always `null` because the judge flow is not
implemented yet. `debug` includes the assembled context, raw model output when
available, and validation warnings for API/debug consumers.

## Streaming Chat Route

`POST /api/chat/stream` runs the same grounded answer path and returns
server-sent events with media type `text/event-stream`.

Current event types:

- `status_changed`
- `retrieval_started`
- `trace_started`
- `trace_step_started`
- `trace_step_completed`
- `trace_complete`
- `retrieval_complete`
- `answer_started`
- `answer_delta`
- `answer_replaced`
- `answer_complete`
- `error`

`answer_delta` streams the current answer text from the model's JSON `answer`
field as it is produced. The API still validates the final parsed model output
before emitting `answer_complete`. If final validation changes the streamed
draft, the stream emits `answer_replaced` and the UI should trust the final
`answer_complete` payload.

`status_changed` carries a simple user-facing state such as `retrieving`,
`answering`, `complete`, or `error`. Detailed progress is separate: `trace_*`
events describe collectible backend steps for the answer trace widget. The
current detailed labels are:

- `Embedding query...`
- `Searching vector index...`
- `Reranking retrieved chunks...`
- `Assembling cited context...`
- `Streaming grounded answer...`

Future deterministic tool calls should emit the same trace-step shape with a
label like `Running tool: <ToolName>...`. The stream includes `elapsed_ms` on
trace payloads and `duration_ms` on completed trace steps. While processing,
the browser UI shows the currently running trace label as a subtle one-line
status. After completion or error, the UI renders a collapsed summary such as
`Processed for 17s >`; expanding it shows the collected trace steps in order.
The UI implementation guide lives at `app/ui/ANSWER_TRACE_UI_GUIDE.md`.

`retrieval_complete` includes evidence blocks and assembled context for the
browser debug panel. `answer_complete` uses the same shape as `POST /api/chat`
plus `processing_ms` when returned from the streaming route.

## Current Answer Behavior

Answer generation is implemented in `app/agents/answer.py`. It reads prompts
from:

- `app/prompts/system.md`
- `app/prompts/answer_fewshot.md`

The answer path uses LangChain/OpenAI for the final model call. Normal chat
execution performs paid OpenAI calls for the query embedding and final answer
model. `ANSWER_MODEL` defaults to `gpt-4.1-mini` and can be overridden in the
environment. `ANSWER_MAX_TOKENS` defaults to 500 and is passed to the LangChain
`ChatOpenAI` answer model in both streaming and non-streaming paths.

The non-streaming path uses LangChain structured output with the
`AnswerModelOutput` Pydantic schema. The streaming path streams normal chat
model chunks, parses the final JSON response with the same schema, and then runs
the same citation validation.

If evidence is missing or below the weak-evidence threshold, the answer layer
abstains before calling the answer model. If model output fails validation, the
answer layer stops at the first validation failure and returns a deterministic
abstention instead of the unsupported draft.

## Current UI Status

The browser UI is implemented as static files in `app/ui/` and is served by
FastAPI under `/ui/`. The app root `/` redirects to `/ui/`.

The frontend uses plain HTML/CSS/JS. It sends a JSON `POST` request to
`/api/chat/stream`, reads the `text/event-stream` response with the Fetch
streaming API, and renders answer deltas as they arrive.

The UI uses light Atlas Mobility Group branding from the demo source corpus,
including the company name, Global Mobility & Finance ownership label, and the
navy/blue color cues from the raw expense policy HTML.

Implemented UI elements:

- chat input
- raw source ZIP download button
- author footer with LinkedIn and GitHub links
- sideways scrolling example-question ribbon with buttons that insert text at
  the chat input cursor
- rotating chat-input placeholder that randomly reuses the ribbon's example
  questions
- send button
- streaming answer panel
- expandable answer trace summary after streaming completes or errors

Pressing `Enter` in the chat input sends the current question. Pressing
`Shift+Enter` inserts a newline.

The chat input starts as a single line, grows upward to 12 lines as text is
entered, and then scrolls internally. The send button sits beside the input so
the composer stays compact on smaller screens.

The answer-card header shows answer metadata such as confidence and citation
count. Detailed backend trace steps render below that header as a quiet
one-line progress row while processing. The row becomes expandable only after
completion or error, provided at least one trace step was received.

Implemented debug fields:

- retrieved chunks, with source filenames shown instead of full source paths
  and an inline `more` control when chunk text is truncated
- rerank scores
- confidence
- assembled retrieval context

The retrieved-chunks panel includes a `Render markdown` toggle when chunks are
available. It switches all retrieved chunks between plain text and a safe
Markdown preview, and the retrieved-chunks header remains outside the card
scroll area so the toggle stays visible while scrolling through chunks.

Citation markers in completed answers are interactive. Hovering or focusing a
citation highlights the matching retrieved chunk and scrolls it below the
retrieved-chunks header with the same spacing as the panel side padding.

Tool-call display is not implemented because the answer path does not yet have a
tool-calling loop.

The UI is sized as a full-height app surface on desktop so the composer remains
visible while the answer and debug panels scroll. Compact desktop widths keep
the two-column layout with reduced spacing; only genuinely narrow/mobile widths
move the debug panel below the chat panel.

On desktop, the debug panel keeps retrieved chunks in the middle and assembled
retrieval context always visible at the bottom with its own scrollbar. The
assembled context header includes an icon-only copy control that copies the full
context text to the clipboard. Validation and runtime failures are shown in the
answer card instead of a separate debug panel section.

Desktop users can resize the main chat/debug split and the retrieved
chunks/assembled context split by dragging the separator bars. The app clamps
the resized panels to usable minimum sizes and stores the preference in browser
local storage.

The example ribbon loops with a transform-based virtual offset, slowly scrolls
on its own, pauses on hover or focus, supports left/right arrow buttons, and can
be dragged horizontally.

## Still Not Implemented

- File upload route
- Router prompt
- Judge prompt and judge execution
- Agent tool-calling loop for claim evaluation
- Local MCP tools under `mcp_server/`
- Answer-level eval runner

## Guardrails Not Yet Developed

Planned guardrails:

- redact obvious PII before model calls where practical
- sanitize HTML before indexing
- prevent retrieved documents from overriding system behavior
- judge generated answers for unsupported claims
- use deterministic tools for arithmetic instead of an LLM

The current code has partial groundwork. HTML loading strips `script` and
`style`, the answer prompt says retrieved documents cannot override system
behavior, and the answer layer has deterministic weak-evidence and
citation-validation checks.
