# Deployment

This project can run as a Docker-based Hugging Face Space. The deployed app uses
the committed FastAPI backend, static browser UI, and existing Chroma vector
store artifacts. It does not run ingestion at container startup.

## Hugging Face Space

Current Space:

```text
https://huggingface.co/spaces/stefekvojtech/travel-and-expense-copilot
```

The Space should be configured as a Docker Space. The root `README.md` includes
the required Space metadata:

```yaml
---
title: Travel & Expense Policy Copilot
sdk: docker
app_port: 7860
---
```

Runtime startup is owned by `Dockerfile`:

```text
python -m uvicorn app.main:app --host 0.0.0.0 --port 7860
```

## Secrets And Variables

Set these in the Hugging Face Space settings:

```text
OPENAI_API_KEY=<private Space Secret>
PUBLIC_DEMO_MODE=true
```

Keep `OPENAI_API_KEY` as a Secret, not a public variable. The API key is read by
the backend process through the environment and is not sent to browser code.

The repo defaults and `.env.example` keep `PUBLIC_DEMO_MODE=false` for local
development. Set it to `true` in the hosted Space so public rate limiting and
safe error messages are active.

## Publish Flow

Add the Space repository as a Git remote once:

```powershell
git remote add hf https://huggingface.co/spaces/stefekvojtech/travel-and-expense-copilot
```

Push the current branch to the Space:

```powershell
git push hf main
```

Hugging Face may ask for credentials. Use a Hugging Face access token with write
permission as the Git password.

## Deployment Notes

- Do not commit `.env` or secrets.
- Do not run ingestion at startup; the app reads `data/processed/04_vectorstore/`.
- Rebuild and commit a clean vector store deliberately when source documents or
  chunking/embedding behavior changes.
- The public demo guardrails are intentionally simple: 1000-character questions,
  default retrieval fanout, 500 answer tokens, and 10 requests per 10 minutes per
  client IP when `PUBLIC_DEMO_MODE=true`.
