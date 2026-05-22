# Answer Trace UI Guide

This file documents the streaming trace contract for a future UI pass. Read it
before changing the expandable answer-progress widget.

## Goal

The UI should keep the current simple runtime status, such as `Retrieving`,
`Answering`, `Complete`, and `Error`.

Separately, it should collect detailed trace events into an expandable widget
similar to:

```text
Processed for 17s >
```

When expanded, the widget should show the detailed backend steps in order. The
right-facing arrow should turn downward when the trace is expanded.

## Stream Events

`POST /api/chat/stream` emits these trace events in addition to the existing
answer and retrieval events:

- `status_changed`
- `trace_started`
- `trace_step_started`
- `trace_step_completed`
- `trace_complete`

Unknown events should be ignored so future backend steps do not break the UI.

## Detailed Steps

Current detailed labels are:

```text
Embedding query...
Searching vector index...
Reranking retrieved chunks...
Assembling cited context...
Streaming grounded answer...
```

Future deterministic tools should emit one step per tool call:

```text
Running tool: <ToolName>...
```

Use the backend-provided `label` field for display text. Do not rebuild these
strings in the frontend.

## Suggested UI Behavior

Use `trace_started` to initialize an empty trace list.

On `trace_step_started`, add a row with `status: running`.

On `trace_step_completed`, update the matching row by `sequence` and show it as
completed. The payload includes `duration_ms`, which can be displayed later if
the design needs per-step timing.

On `trace_complete`, use `elapsed_ms` to render the collapsed summary:

```text
Processed for 17s >
```

Round seconds for the summary. Keep raw milliseconds available if later UI wants
more exact timing.

## Separation From Answer Text

The trace is operational metadata. It is not model reasoning. Avoid labels such
as `Thought for 17s`, because the backend is not exposing hidden model thoughts.

The streamed answer still comes from:

- `answer_delta`
- `answer_replaced`
- `answer_complete`

The trace widget should not replace the answer stream or the evidence/debug
panel.
