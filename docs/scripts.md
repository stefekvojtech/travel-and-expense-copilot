# Scripts

The `scripts/` directory contains thin command-line entrypoints over application
modules. The scripts are mainly for local development, corpus rebuilding,
retrieval debugging, and evaluation.

The hosted Hugging Face demo does not expose these scripts to visitors. It runs
the FastAPI app from `Dockerfile` and reads the existing committed vector store.

## Script Groups

Script numbers indicate workflow order and role:

- `00_*`: orchestration scripts that run multiple numbered stages
- `01_*` through `09_*`: corpus-build stages, from raw source files to indexes
- `10_*` through `19_*`: retrieval and retrieval-debug entrypoints
- `20_*` through `29_*`: evaluation entrypoints
- `30_*` and above: runtime answer/demo commands
- unnumbered scripts: local server and deployment helpers

## Corpus Build Scripts

These scripts turn files in `data/raw/` into artifacts under `data/processed/`.

```powershell
python scripts/01_load_documents.py
python scripts/02_normalize_blocks.py
python scripts/03_chunk_blocks.py
python scripts/04_embed_chunks.py
```

Run the full local raw-to-vector-store build with:

```powershell
python scripts/00_run_ingestion.py
```

The numbered build stages always rebuild their own output folders. There is no
incremental or force mode.

Stage 04 embeds chunks into Chroma and uses the configured paid embedding
provider. Ask before running `scripts/04_embed_chunks.py`, including when it is
triggered indirectly through `scripts/00_run_ingestion.py`.

## Retrieval And Answer Scripts

Retrieve citation-ready context without generating an answer:

```powershell
python scripts/10_retrieve_context.py "Can I take a taxi from Prague airport after 21:00?"
```

Generate a grounded answer from retrieved evidence:

```powershell
python scripts/30_ask.py "Can I take a taxi from Prague airport after 21:00?"
```

`scripts/30_ask.py` performs paid OpenAI calls for query embedding and final
answer generation when `OPENAI_API_KEY` is configured.

Run the same answer path through the local FastAPI server and browser UI:

```powershell
python scripts/run_local_server.py
```

The launcher binds only to localhost, reloads after code changes, and opens:

```text
http://127.0.0.1:8000/ui/
```

Use `--port` to select another localhost port, `--no-reload` to disable
development reloads, or `--no-browser` for a headless terminal.

Routes:

- `GET /health`
- `POST /api/chat`
- `POST /api/chat/stream`

`/api/chat` returns one validated JSON answer. `/api/chat/stream` returns
server-sent events for runtime status, trace steps, answer deltas, and the final
validated answer payload. The browser UI uses the streaming route and displays
retrieved evidence, rerank scores, citations, confidence, and the assembled
context in its debug panel.

## Evaluation Scripts

Run retrieval evaluation against the golden eval set:

```powershell
python scripts/20_run_eval.py
```

The first automated eval runner is `scripts/20_run_eval.py`. It evaluates
retrieval quality against:

```text
data/eval/golden_eval_set.jsonl
```

Retrieval evaluation writes:

- `data/eval/20_retrieval_eval_report.md`
- `data/eval/20_retrieval_eval_results.jsonl`

This command embeds each eval question and therefore uses the configured paid
embedding provider.

## Deployment Script

Publish the committed repository snapshot to the Hugging Face Space with:

```powershell
python scripts/deploy_hf_space.py
```

This script is for maintainers, not demo visitors. It uploads committed `HEAD`
through the Hugging Face Hub API, waits for build/runtime status, streams build
logs while waiting, and exits successfully only after the Space reports
`RUNNING`.

The script does not read `.env` and does not store Hugging Face credentials in
the repo. It uses an existing Hugging Face login token or the Git credential
stored for `https://huggingface.co`.

## Supported Source Types

Current local source loaders:

- PDF: `app/ingest/loaders/pdf.py`
- HTML/HTM: `app/ingest/loaders/html.py`
- XLSX: `app/ingest/loaders/xlsx.py`
- TXT: `app/ingest/loaders/text.py`
- PNG/JPG/JPEG: `app/ingest/loaders/image.py`

Unsupported files and loader warnings are shown in:

```text
data/processed/report.md
```
