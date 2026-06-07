# Deployment

This project can run as a Docker-based Hugging Face Space. The deployed app uses
the committed FastAPI backend, static browser UI, and existing Chroma vector
store artifacts.

The hosted Space is for the public retrieval and answering demo. It does not run
ingestion, rebuild embeddings, run evals, or accept new source documents from
visitors. Those workflows stay in the local repository and are handled by
scripts.

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

The hosted Space does not receive or use the local `.env` file. The file is
ignored by Git and excluded by `.dockerignore`, so it is not uploaded to the
Space repository or copied into the Docker image.

Configure these values manually in the Hugging Face Space settings:

```text
OPENAI_API_KEY=<private Space Secret>
PUBLIC_DEMO_MODE=true <public Space Variable>
```

Hugging Face stores these settings separately from the repository. They are not
added when `scripts/deploy_hf_space.py` uploads the committed repository, and
they are not copied into the Docker image during its build.

Instead, when Hugging Face starts or restarts the built Space container, it
injects the Secrets and Variables currently configured in the Space settings
into that running container as environment variables. The FastAPI backend then
reads them with `os.getenv(...)`.

For example, the deployment upload contains neither the local `.env` file nor
the OpenAI key. At container startup, Hugging Face supplies the separately
stored `OPENAI_API_KEY` Secret to the running backend process.

Keep `OPENAI_API_KEY` as a Secret, not a public Variable. It has no application
default and must be configured for hosted OpenAI-backed retrieval and answer
generation. The key is available to the backend process but is not sent to
browser code.

`PUBLIC_DEMO_MODE` has an application default of `false`, which is appropriate
for local development. It must be manually configured as `true` in the hosted
Space so public rate limiting and safe error messages are active.

Other non-secret settings do not need to be configured in Hugging Face unless
the hosted demo should override their application defaults. For example,
`QUESTION_MAX_CHARACTERS` defaults to `1000`; add it as a public Space Variable
only when the hosted limit should be different.

Configuration precedence for the hosted app is:

1. At container startup, a Secret or Variable manually configured in the
   Hugging Face Space settings is injected and used.
2. If no Space setting was configured for that key, the built-in default in
   `app/core/config.py` is used when one exists.
3. If no Space setting and no application default exist, the value is
   unavailable. This is why `OPENAI_API_KEY` must be manually configured.

`.env.example` documents available configuration keys but is not loaded as
runtime configuration. The real local `.env` is used only for local development.

See the official Hugging Face documentation for
[Spaces secrets and variables](https://huggingface.co/docs/hub/main/spaces-overview#managing-secrets-and-environment-variables)
and
[Docker Spaces runtime environment management](https://huggingface.co/docs/hub/main/spaces-sdks-docker#secrets-and-variables-management).

## Publish Flow

GitHub is the routine source-control and backup remote. Hugging Face Spaces is
the public hosted demo environment, so publishing there is a separate explicit
step and should not happen automatically after every commit.
Ask for publish permission through the command approval flow, not as a casual
text question. Use this exact approval question: "Do you want to publish this
version to Hugging Face Space? This might take a while." Declining a publish
request is expected and is not a failed deployment.

Deploy the current committed repository snapshot with:

```powershell
python scripts/deploy_hf_space.py
```

The script uploads `HEAD` through the Hugging Face Hub API, waits for the Space
build/runtime status, streams new build logs while waiting, and exits
successfully only after the Space reports `RUNNING`. It uses temporary export
files internally and removes them automatically, including on failures.

The script does not read `.env` and does not store Hugging Face credentials in
the repo. It uses an existing Hugging Face login token or the Git credential
stored for `https://huggingface.co`.

Plain `git push hf main` is not the preferred publish path for this project
because the committed Chroma vector store includes binary files that Hugging Face
handles more reliably through its upload API.

## Deployment Notes

- Do not commit `.env` or secrets.
- Do not run ingestion at startup; the app reads `data/processed/04_vectorstore/`.
- Rebuild and commit a clean vector store deliberately when source documents or
  chunking/embedding behavior changes.
- The public demo guardrails are intentionally simple:
  `QUESTION_MAX_CHARACTERS`-limited questions, default retrieval fanout, 500
  answer tokens, and 10 requests per 10 minutes per client IP when
  `PUBLIC_DEMO_MODE=true`.
