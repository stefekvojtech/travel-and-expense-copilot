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

- `documents.jsonl`: loaded LangChain document records
- `chunks/*.jsonl`: shared `ChunkArtifact` records per source file
- `previews/*.md`: readable chunk previews
- `warnings.jsonl`: skipped files and loader issues
- `report.md`: summary table and sample chunks
