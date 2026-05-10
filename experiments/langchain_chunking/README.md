# LangChain Chunking Experiment

This folder is intentionally separate from the production ingestion pipeline.

The experiment loads raw files with LangChain community document loaders where
possible, normalizes the same sources with the project's existing ingestion
loaders, chunks the normalized blocks with a direct LangChain splitter path, and
writes all outputs under:

```text
data/processed_langchain_experiment/
```

It does not read or write the existing production artifacts in
`data/processed/`.

Chunk sizing uses the shared `.env` settings: `CHUNK_SIZE`, `CHUNK_OVERLAP`, and
`MAX_CHUNK_TOKENS`. The experiment uses the smaller of `CHUNK_SIZE` and
`MAX_CHUNK_TOKENS` as the effective splitter size and validates generated chunks
before writing them.

The loaded-document stage keeps LangChain `Document` objects for inspection. PDF
files are loaded page by page, then merged into one source-level document so the
raw LangChain loader output is easier to inspect. The chunking stage assembles
the project's normalized block artifacts into Markdown, applies
`MarkdownHeaderTextSplitter`, then applies
`RecursiveCharacterTextSplitter.from_tiktoken_encoder(...)`. The experiment maps
split text back to source blocks so generated chunks still carry block IDs,
pages, sheets, and section metadata.

`run_experiment(...)` defaults to `chunking_mode="langchain_direct"`. For quick
fallback comparison, callers can pass `chunking_mode="production_wrapped"` to use
the production chunking wrapper against the same normalized block artifacts.

Run from the repository root:

```powershell
python scripts/experiment_langchain_chunking.py
```

Current scope:

- PDF via `langchain_community.document_loaders.PyPDFLoader`
- HTML via `langchain_community.document_loaders.BSHTMLLoader`
- TXT via `langchain_community.document_loaders.TextLoader`
- XLSX is skipped unless a future experiment adds an Excel-specific dependency
- images are skipped to avoid paid vision calls

Generated outputs:

- `01_loaded_documents/*.jsonl`: loaded LangChain document records, one JSONL
  file per source document
- `01_loaded_documents_preview/*.md`: full readable previews of the loaded
  documents
- `02_normalized_blocks/*.jsonl`: normalized block artifacts from the existing
  project loaders
- `02_normalized_blocks_preview/*.md`: full readable previews of those blocks
- `03_chunks/*.jsonl`: shared `ChunkArtifact` records per source document
- `03_chunks_preview/*.md`: full readable previews of every generated chunk
- `report.md`: summary table plus skipped files and loader warnings

The numbered folders are ordered by pipeline stage:

```text
raw files
  -> 01_loaded_documents
  -> 01_loaded_documents_preview
  -> 02_normalized_blocks
  -> 02_normalized_blocks_preview
  -> 03_chunks
  -> 03_chunks_preview
  -> report.md
```
