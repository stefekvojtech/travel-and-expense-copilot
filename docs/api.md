# API, UI, and Answer Status

The project now has a first FastAPI backend for grounded answer generation. The
browser UI, upload route, agent tool-calling loop, and judge flow are still not
implemented. Standalone deterministic tools exist under `app/tools/`, but they
are not wired into the API or answer agent.

## Current API

The FastAPI app entrypoint is:

```text
app/main.py
```

Run it locally with:

```powershell
python -m uvicorn app.main:app --reload
```

Implemented routes:

- `GET /health`
- `POST /api/chat`
- `POST /api/chat/stream`

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

`retrieval_complete` includes evidence blocks and assembled context for a future
debug panel. `answer_complete` uses the same shape as `POST /api/chat`.

## Current Answer Behavior

Answer generation is implemented in `app/agents/answer.py`. It reads prompts
from:

- `app/prompts/system.md`
- `app/prompts/answer_fewshot.md`

The answer path uses LangChain/OpenAI for the final model call. Normal chat
execution performs paid OpenAI calls for the query embedding and final answer
model. The default answer model is `gpt-5.5` unless `ANSWER_MODEL` overrides it.

The non-streaming path uses LangChain structured output with the
`AnswerModelOutput` Pydantic schema. The streaming path streams normal chat
model chunks, parses the final JSON response with the same schema, and then runs
the same citation validation.

If evidence is missing or below the weak-evidence threshold, the answer layer
abstains before calling the answer model. If model output fails validation, the
answer layer returns a deterministic abstention instead of the unsupported
draft.

## Current UI Status

There is no browser UI yet.

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

## Still Not Implemented

- Browser UI
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
