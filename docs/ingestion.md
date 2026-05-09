# Ingestion

Ingestion turns raw source files into two artifacts:

- Markdown previews for humans
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
- the previous Markdown output exists
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

Blocks are the canonical input for chunking. Markdown previews are not used for
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
MARKDOWN_DIR=data/processed/markdown
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
