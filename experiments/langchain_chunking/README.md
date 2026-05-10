# LangChain Chunking Experiment

This folder is intentionally separate from the production ingestion pipeline.

The experiment loads raw files with LangChain community document loaders where
possible, chunks the loaded documents with LangChain text splitters, and writes
all outputs under:

```text
data/processed_langchain_experiment/
```

It does not read or write the existing production artifacts in
`data/processed/`.

Chunk sizing uses the shared `.env` settings: `CHUNK_SIZE`, `CHUNK_OVERLAP`, and
`MAX_CHUNK_TOKENS`. The experiment uses the smaller of `CHUNK_SIZE` and
`MAX_CHUNK_TOKENS` as the effective splitter size and validates generated chunks
before writing them.

The implementation keeps LangChain `Document` objects through the splitting
phase. It uses `MarkdownHeaderTextSplitter` only when loaded text already
contains Markdown headings, then calls
`RecursiveCharacterTextSplitter.split_documents(...)` with `add_start_index=True`
so each chunk keeps loader metadata plus its source start offset.

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

- `01_documents/*.jsonl`: loaded LangChain document records, one JSONL file per
  source document
- `02_documents_preview/*.md`: full readable previews of the loaded documents
- `03_chunks/*.jsonl`: shared `ChunkArtifact` records per source document
- `04_chunks_preview/*.md`: full readable previews of every generated chunk
- `report.md`: summary table plus skipped files and loader warnings

The numbered folders are ordered by pipeline stage:

```text
raw files
  -> 01_documents
  -> 02_documents_preview
  -> 03_chunks
  -> 04_chunks_preview
  -> report.md
```
