# LangChain Chunking Experiment Report

- generated_at: `2026-05-10T15:35:45.683444+00:00`
- output_dir: `data/processed_langchain_experiment`
- documents_chunked: `3`
- chunks_generated: `43`
- warnings: `3`

## Pipeline Stages

This experiment writes machine-readable artifacts and matching human-readable previews for each stage.

| Stage | Machine artifacts | Preview artifacts | Purpose |
| --- | --- | --- | --- |
| 1. Loaded documents | `01_loaded_documents/*.jsonl` | `01_loaded_documents_preview/*.md` | Raw LangChain loader output for inspection before project normalization. |
| 2. Normalized blocks | `02_normalized_blocks/*.jsonl` | `02_normalized_blocks_preview/*.md` | Project-normalized structural units with Markdown, source metadata, pages, sheets, tables, and block lineage. |
| 3. Chunks | `03_chunks/*.jsonl` | `03_chunks_preview/*.md` | Retrieval-sized `ChunkArtifact` records produced from normalized blocks. |

Preview files are generated only from the same-stage machine artifact; they are for reading and debugging, not downstream pipeline input.

Flow:

```text
raw files -> loaded documents -> normalized blocks -> chunks
```

## Documents

| Source | Loader | Loaded docs | Blocks | Chunks | Loaded docs | Loaded preview | Blocks | Blocks preview | Chunks | Chunk preview |
| --- | --- | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- |
| `data/raw/expense_policy.html` | `BSHTMLLoader` | 1 | 70 | 13 | `data/processed_langchain_experiment/01_loaded_documents/expense-policy-aead3745bd.jsonl` | `data/processed_langchain_experiment/01_loaded_documents_preview/expense-policy-aead3745bd.md` | `data/processed_langchain_experiment/02_normalized_blocks/expense-policy-aead3745bd.jsonl` | `data/processed_langchain_experiment/02_normalized_blocks_preview/expense-policy-aead3745bd.md` | `data/processed_langchain_experiment/03_chunks/expense-policy-aead3745bd.jsonl` | `data/processed_langchain_experiment/03_chunks_preview/expense-policy-aead3745bd.md` |
| `data/raw/extended_expense_scenarios.txt` | `TextLoader` | 1 | 1 | 8 | `data/processed_langchain_experiment/01_loaded_documents/extended-expense-scenarios-b3f521ebe6.jsonl` | `data/processed_langchain_experiment/01_loaded_documents_preview/extended-expense-scenarios-b3f521ebe6.md` | `data/processed_langchain_experiment/02_normalized_blocks/extended-expense-scenarios-b3f521ebe6.jsonl` | `data/processed_langchain_experiment/02_normalized_blocks_preview/extended-expense-scenarios-b3f521ebe6.md` | `data/processed_langchain_experiment/03_chunks/extended-expense-scenarios-b3f521ebe6.jsonl` | `data/processed_langchain_experiment/03_chunks_preview/extended-expense-scenarios-b3f521ebe6.md` |
| `data/raw/travel_policy.pdf` | `PyPDFLoader` | 1 | 77 | 22 | `data/processed_langchain_experiment/01_loaded_documents/travel-policy-2c55f3d095.jsonl` | `data/processed_langchain_experiment/01_loaded_documents_preview/travel-policy-2c55f3d095.md` | `data/processed_langchain_experiment/02_normalized_blocks/travel-policy-2c55f3d095.jsonl` | `data/processed_langchain_experiment/02_normalized_blocks_preview/travel-policy-2c55f3d095.md` | `data/processed_langchain_experiment/03_chunks/travel-policy-2c55f3d095.jsonl` | `data/processed_langchain_experiment/03_chunks_preview/travel-policy-2c55f3d095.md` |

## Warnings

| Source | Type | Message | Observed at |
| --- | --- | --- | --- |
| `data/raw/airport_transfer_eligibility_decision_tree.png` | `skipped_paid_vision` | Images are skipped because extracting them would require a paid vision call. | `2026-05-10T15:35:42.270439+00:00` |
| `data/raw/corporate_travel_card_rules.png` | `skipped_paid_vision` | Images are skipped because extracting them would require a paid vision call. | `2026-05-10T15:35:42.273637+00:00` |
| `data/raw/per_diem_caps.xlsx` | `unsupported_in_experiment` | XLSX is intentionally skipped in this first LangChain chunking experiment. | `2026-05-10T15:35:43.043266+00:00` |
