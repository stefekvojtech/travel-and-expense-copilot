# AGENTS.md

## Scope

Applies to `app/ui/`.

This directory contains the implemented static browser UI served by FastAPI
under `/ui/`.

Run it locally from the repository root with:

```powershell
python scripts/run_local_server.py
```

## Role

The UI is minimal and implemented with plain HTML, CSS, and JavaScript.

Current behavior includes:

- chat input
- example questions
- server-sent event streaming
- runtime status and trace display
- grounded answer rendering
- citations and confidence display
- raw policy data download

Potential future behavior includes:

- file upload
- richer retrieval and rerank debug details
- tool-call display
- judge-result display

## Rules

- Do not add React, Vue, Next.js, or another frontend framework.
- Keep the interface simple and operational, not a marketing landing page.
- Preserve server-sent event streaming behavior.
- Keep the UI compatible with FastAPI serving it under `/ui/`.
- Update `docs/api.md` and `README.md` when UI usage changes.
