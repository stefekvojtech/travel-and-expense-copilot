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
python -m uvicorn app.main:app --reload
```

Open the browser UI at:

```text
http://127.0.0.1:8000/ui/
```

Implemented routes:

- `GET /health`
- `POST /api/chat`
- `POST /api/chat/stream`
- `GET /api/downloads/raw-data.zip`

Routes live in `app/api/`. Pydantic request and response models live in
`app/api/schemas.py`. Route handlers stay thin and call reusable answer and
streaming modules.

## Health Route

`GET /health` returns a minimal liveness response:

```json
{
  "status": "ok",
  "app": "travel-and-expense-copilot"
}
```

It does not currently check Chroma, OpenAI credentials, or model availability.

## Raw Data Download Route

`GET /api/downloads/raw-data.zip` returns a ZIP archive of files from
`data/raw/`, excluding local `AGENTS.md` instruction files. The browser UI links
to this route with a download button in the top bar.

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
`doc_type`, `source_path`, and `section_path`.

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
available, and validation warnings.

## Streaming Chat Route

`POST /api/chat/stream` runs the same grounded answer path and returns
server-sent events with media type `text/event-stream`.

Current event types:

- `retrieval_started`
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

`retrieval_complete` includes evidence blocks and assembled context for the
browser debug panel. `answer_complete` uses the same shape as `POST /api/chat`.

## Current Answer Behavior

Answer generation is implemented in `app/agents/answer.py`. It reads prompts
from:

- `app/prompts/system.md`
- `app/prompts/answer_fewshot.md`

The answer path uses LangChain/OpenAI for the final model call. Normal chat
execution performs paid OpenAI calls for the query embedding and final answer
model. `ANSWER_MODEL` must be set in the environment; the runtime no longer
falls back to a built-in answer-model default.

The non-streaming path uses LangChain structured output with the
`AnswerModelOutput` Pydantic schema. The streaming path streams normal chat
model chunks, parses the final JSON response with the same schema, and then runs
the same citation validation.

If evidence is missing or below the weak-evidence threshold, the answer layer
abstains before calling the answer model. If model output fails validation, the
answer layer returns a deterministic abstention instead of the unsupported
draft.

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
- sideways scrolling example-question ribbon with buttons that insert text at
  the chat input cursor
- send button
- streaming answer panel

Pressing `Enter` in the chat input sends the current question. Pressing
`Shift+Enter` inserts a newline.

The chat input starts as a single line, grows upward to 12 lines as text is
entered, and then scrolls internally. The send button sits beside the input so
the composer stays compact on smaller screens.

Implemented debug fields:

- retrieved chunks
- rerank scores
- citations
- confidence
- validation warnings
- assembled retrieval context
- judge result placeholder, currently shown as not implemented

Citation markers in completed answers are interactive. Hovering or focusing a
citation highlights the matching retrieved chunk and scrolls it to the top of
the retrieved-chunks panel.

Tool-call display is not implemented because the answer path does not yet have a
tool-calling loop.

The UI is sized as a full-height app surface on desktop so the composer remains
visible while the answer and debug panels scroll. On narrower screens, the debug
panel moves below the chat panel.

On desktop, the debug panel keeps status details at the top, retrieved chunks in
the middle, and assembled retrieval context always visible at the bottom with
its own scrollbar.

The example ribbon slowly scrolls on its own, pauses on hover or focus, supports
left/right arrow buttons, and can be dragged horizontally.

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
