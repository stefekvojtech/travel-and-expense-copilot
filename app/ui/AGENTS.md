# AGENTS.md

## Scope

Applies to `app/ui/`.

This is an empty scaffold for the future browser UI.

## Planned Role

The UI should be minimal and implemented with plain HTML, CSS, and JavaScript.

Required elements:

- chat input
- send button
- file upload
- streaming answer panel

Preferred debug fields:

- retrieved chunks
- rerank scores
- citations
- tool calls
- confidence
- judge result

## Rules

- Do not add React, Vue, Next.js, or another frontend framework.
- Keep the interface simple and operational, not a marketing landing page.
- Preserve streaming behavior once it exists.
- Update `docs/api.md` and `README.md` when UI usage changes.
