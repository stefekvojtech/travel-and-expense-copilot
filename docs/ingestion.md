# Ingestion

Ingestion turns raw source files into two artifacts:

- preview Markdown files for humans
- Block JSONL files for canonical lineage and downstream chunking

The current entrypoints are:

```powershell
python scripts/pipeline.py ingest
python scripts/pipeline.py ingest --force
python scripts/pipeline.py chunk
python scripts/pipeline.py embed --dry-run
python scripts/pipeline.py embed
```

The focused legacy script entrypoints remain available:

```powershell
python scripts/ingest_incremental.py
python scripts/ingest_force.py
python scripts/chunk_blocks.py
python scripts/embed_chunks.py --dry-run
python scripts/embed_chunks.py
```

## Source Discovery

`app/ingest/pipeline_raw.py` discovers every file under `RAW_DATA_DIR`, currently
`data/raw/`.

Local `AGENTS.md` instruction files are excluded from raw discovery because they
are agent guidance, not source corpus documents.

Supported suffixes:

- `.pdf`
- `.html`
- `.htm`
- `.xlsx`
- `.txt`
- `.png`
- `.jpg`
- `.jpeg`

Unsupported files are not silently ignored. They are written to
`data/processed/ingest_warnings.jsonl` with an `unsupported_suffix` warning.

## Incremental vs Force Ingestion

`python scripts/pipeline.py ingest` and `python scripts/ingest_incremental.py`
reuse existing artifacts when:

- the source path is still present
- the raw file hash has not changed
- the previous preview Markdown output exists
- the previous block JSONL output exists

`python scripts/pipeline.py ingest --force` and `python scripts/ingest_force.py`
rebuild all supported raw sources even when hashes match.

Force ingestion can trigger OpenAI vision calls for image files when
`OPENAI_API_KEY` is configured. Treat that as a paid model operation.

## Document IDs

Each supported source gets a stable `doc_id` built from:

- a slugified source filename stem
- a short SHA-1 digest of the project-relative source path

Example:

```text
expense-policy-aead3745bd
```

This keeps IDs readable while reducing collisions when two files have the same
name in different directories.

## Manifest

`data/processed/ingest_manifest.jsonl` stores one JSON row per ingested document.
Important fields include:

- `doc_id`
- `source_path`
- `output_markdown_path`
- `output_blocks_path`
- `doc_type`
- `title`
- `content_hash`
- `source_size_bytes`
- `source_modified_at`
- `ingested_at`
- `block_count`
- `extraction_method`
- `extraction_warning`

The manifest is used by incremental ingestion to decide whether a source can be
skipped.

## Blocks

Block JSONL files live in `data/processed/blocks/`.

Each block has:

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

Blocks are the canonical input for chunking. Preview Markdown files are not used for
chunk lineage.

## Loader Behavior

PDF loading uses `pypdf` for text extraction and `pdfplumber` for table extraction.
It removes repeated page-header noise, skips simple page labels, maps numbered
headings to Markdown headings, preserves bullets, and emits extracted tables as
Markdown tables with page metadata.

HTML loading uses BeautifulSoup. It removes `script` and `style`, preserves common
semantic tags, renders tables and lists into Markdown, and tracks section paths
from headings. This is basic sanitization, not a complete security sanitizer.

XLSX loading uses OpenPyXL with `read_only=True` and `data_only=True`, meaning
formula cells are read as cached visible values. Sheets are converted into a sheet
heading, a table header block, and row-level `table_row` blocks. Common row fields
such as country, city, category, expense category, and currency are copied into
metadata when present.

TXT loading reads UTF-8 text, cleans paragraph whitespace, and stores the file as
one plain-text block. This intentionally lets the chunking stage exercise recursive
splitting.

Image loading uses OpenAI vision through LangChain/OpenAI when `OPENAI_API_KEY` is
present. Without an API key, it writes a placeholder Markdown block and sets
`extraction_warning` to `missing_openai_api_key`.

Loader modules are documented with top-level module docstrings. Those docstrings
should summarize the supported source type, the extraction approach, and the
lineage metadata preserved for chunking and citations.

## Chunking

`app/ingest/pipeline_chunk.py` reads block JSONL files and writes chunk JSONL to
`data/processed/chunks/`.

For XLSX sources, each table row becomes a chunk unless it exceeds the configured
chunk size, in which case it is split recursively.

For other sources, blocks are assembled into Markdown and split with
`MarkdownHeaderTextSplitter`, then oversized sections are split with a
token-aware recursive splitter using the `cl100k_base` encoding.

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

Table continuation chunks can include header/context text so a row fragment stays
understandable.

## LangChain Chunking Experiment

`scripts/experiment_langchain_chunking.py` runs an isolated comparison path under
`data/processed_langchain_experiment/`. It loads raw PDF, HTML, and TXT files
with LangChain community loaders, then chunks the loaded documents with
LangChain text splitters. It does not read production blocks from
`data/processed/`.

PDF files are loaded page by page with LangChain, then merged into one
source-level experiment document before chunking. This allows experimental
chunks to span page boundaries while preserving overlapped page numbers in chunk
metadata.

The experiment writes numbered artifact folders in creation order:

- `01_documents/`: per-source JSONL files containing loaded LangChain document
  records
- `02_documents_preview/`: full readable previews of those loaded documents
- `03_chunks/`: per-source JSONL files containing experimental `ChunkArtifact`
  records
- `04_chunks_preview/`: full readable previews of every experimental chunk

`report.md` summarizes loaded documents, chunk counts, artifact paths, and
warnings in Markdown tables. XLSX is skipped in the current experiment, and image
files are skipped to avoid paid vision calls.

## Embedding

`app/ingest/pipeline_embed.py` reads all chunk JSONL files and stores them in a
local Chroma collection.

Dry run:

```powershell
python scripts/pipeline.py embed --dry-run
```

Legacy equivalent:

```powershell
python scripts/embed_chunks.py --dry-run
```

Real embedding:

```powershell
python scripts/pipeline.py embed
```

Legacy equivalent:

```powershell
python scripts/embed_chunks.py
```

Real embedding calls OpenAI through `langchain_openai.OpenAIEmbeddings` and
consumes paid credits.

The embedder writes chunk text as the vector document. Chunk metadata is flattened
for Chroma. List-like fields such as `source_block_ids`, `pages`, and `sheets` are
stored as JSON strings.

Embedding is designed as a replace operation:

1. Create a temporary collection.
2. Add all chunks.
3. Verify the temporary collection count.
4. Rename the previous collection to a backup name.
5. Promote the temporary collection to the configured collection name.
6. Delete backup/orphaned collections and vector directories when safe.

## Configuration

Important ingestion and embedding settings in `.env.example`:

```text
RAW_DATA_DIR=data/raw
PROCESSED_DATA_DIR=data/processed
PREVIEWS_DIR=data/processed/previews
CHUNKS_DIR=data/processed/chunks
VECTOR_STORE_DIR=data/processed/vectorstore
VECTOR_COLLECTION_NAME=travel_expense_policy_chunks

EMBEDDING_MODEL=text-embedding-3-large
VISION_MODEL=gpt-4.1-mini

CHUNK_SIZE=600
CHUNK_OVERLAP=120
MAX_CHUNK_TOKENS=1200
```

`MAX_CHUNK_TOKENS` is enforced as a hard upper bound. The chunking pipeline uses
the smaller of `CHUNK_SIZE` and `MAX_CHUNK_TOKENS` as the effective splitter size,
then validates that every produced chunk is within the configured maximum before
writing chunk artifacts.
