# Ingestion

Ingestion turns raw source files into numbered artifacts under `data/processed/`.
Each machine-readable stage has a matching `_preview` folder for human review.

The current build commands are:

```powershell
python scripts/01_load_documents.py
python scripts/02_normalize_blocks.py
python scripts/03_chunk_blocks.py
python scripts/04_embed_chunks.py
```

To run the full raw-to-vector-store build:

```powershell
python scripts/pipeline.py
```

Search is separate from the build pipeline:

```powershell
python scripts/search_chunks.py "Can I take a taxi from Prague airport after 21:00?"
```

## Artifact Order

```text
data/raw/*
  -> 01_loaded_documents/
  -> 02_normalized_blocks/
  -> 03_chunks/
  -> 04_vectorstore/
  -> report.md
```

Each numbered machine-readable stage writes its matching `_preview` folder beside
it for inspection.

The numbered stages always rebuild their own output folders. There is no
incremental/force mode and no manifest file. Warnings are written into
`data/processed/report.md`.

## Source Discovery

`app/ingest/source_files.py` discovers every file under `RAW_DATA_DIR`, currently
`data/raw/`. Local `AGENTS.md` instruction files are excluded.

Supported suffixes:

- `.pdf`
- `.html`
- `.htm`
- `.xlsx`
- `.txt`
- `.png`
- `.jpg`
- `.jpeg`

Unsupported files are not silently ignored. They are listed in the report's
Warnings table.

## Stage 01: Loaded Documents

`app/ingest/step01_load_documents.py` writes:

- `data/processed/01_loaded_documents/*.jsonl`
- `data/processed/01_loaded_documents_preview/*.md`

PDF, HTML, and TXT use LangChain community loaders:

- PDF: `PyPDFLoader`, loaded page-by-page and merged into one source-level
  inspection record
- HTML: `BSHTMLLoader`
- TXT: `TextLoader`

XLSX and image files use the project loaders so source coverage matches the
production pipeline. Image loading may call OpenAI vision when `OPENAI_API_KEY`
is configured.

This stage is for inspecting loaded source text. Chunking does not use these
records directly; chunking uses normalized blocks from stage 02.

## Stage 02: Normalized Blocks

`app/ingest/step02_normalize_blocks.py` writes:

- `data/processed/02_normalized_blocks/*.jsonl`
- `data/processed/02_normalized_blocks_preview/*.md`

Blocks are the canonical normalized artifacts used for chunking and citation
lineage. Each block has:

- `doc_id`
- `block_id`
- `source_path`
- `doc_type`
- `title`
- `block_type`
- `text`
- `section_path`
- `page`
- `sheet`
- `order`
- `metadata`

PDF normalization uses `pypdf` for text and `pdfplumber` for tables. It removes
repeated page-header noise, skips simple page labels, maps numbered headings to
Markdown headings, preserves bullets, and emits extracted tables as Markdown
tables with page metadata.

HTML normalization uses BeautifulSoup. It removes `script` and `style`,
preserves common semantic tags, renders tables and lists into Markdown, and
tracks section paths from headings.

XLSX normalization uses OpenPyXL with `read_only=True` and `data_only=True`.
Sheets are converted into a sheet heading, a table header block, and row-level
`table_row` blocks. Common row fields such as country, city, category, expense
category, and currency are copied into metadata when present.

TXT normalization reads UTF-8 text, cleans paragraph whitespace, and stores the
file as one plain-text block.

Image normalization reuses the stage 01 loaded image text when available. This
avoids calling vision twice in a normal pipeline run.

## Stage 03: Chunking

`app/ingest/step03_chunk_blocks.py` reads `02_normalized_blocks` and writes:

- `data/processed/03_chunks/*.jsonl`
- `data/processed/03_chunks_preview/*.md`

For XLSX sources, each table row becomes a chunk unless it exceeds `CHUNK_SIZE`,
in which case it is split recursively.

For other sources, blocks are assembled into Markdown and split with
`MarkdownHeaderTextSplitter`, then oversized sections are split with
`RecursiveCharacterTextSplitter.from_tiktoken_encoder(...)`.

`CHUNK_SIZE` and `CHUNK_OVERLAP` are passed directly into the LangChain splitter.
`MAX_CHUNK_TOKENS` remains a validation limit after chunking.

Chunk metadata includes:

- `doc_id`
- `chunk_id`
- `source_path`
- `doc_type`
- `title`
- `source_block_ids`
- `section_path`
- `pages`
- `sheets`
- `chunk_strategy`
- `token_count`
- `order`
- merged source metadata

The production table behavior is preserved: table header/context text is repeated
for continuation chunks where needed. Chunk-to-block mapping is strict; failure
to map split text back to source blocks raises an error.

## Stage 04: Embedding

`app/ingest/step04_embed_chunks.py` reads `03_chunks` and stores chunks in local
Chroma under:

```text
data/processed/04_vectorstore/
```

Real embedding calls OpenAI through `langchain_openai.OpenAIEmbeddings` and
consumes paid credits. The previous Chroma collection is not removed up front.
The embedder builds a temporary collection, adds all chunks, verifies the count,
then promotes the temporary collection to the configured collection name.

The embedder writes chunk text as the vector document. Chunk metadata is
flattened for Chroma. List-like fields such as `source_block_ids`, `pages`, and
`sheets` are stored as JSON strings.

## Report

`app/ingest/pipeline_report.py` writes `data/processed/report.md`.

The report contains:

- generation timestamp
- total loaded documents, blocks, chunks, and warnings
- a document table with artifact paths for all numbered stages
- a warnings table

There is no separate `ingest_manifest.jsonl` or `ingest_warnings.jsonl`.

## Configuration

Important ingestion and embedding settings in `.env.example`:

```text
RAW_DATA_DIR=data/raw
PROCESSED_DATA_DIR=data/processed
VECTOR_COLLECTION_NAME=travel_expense_policy_chunks

EMBEDDING_MODEL=text-embedding-3-large
VISION_MODEL=gpt-4.1-mini

CHUNK_SIZE=600
CHUNK_OVERLAP=120
MAX_CHUNK_TOKENS=1200
```

Artifact subfolders are derived from `PROCESSED_DATA_DIR`.
