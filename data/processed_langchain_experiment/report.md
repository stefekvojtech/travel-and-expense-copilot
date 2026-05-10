# LangChain Chunking Experiment Report

- generated_at: `2026-05-10T14:44:10.873167+00:00`
- output_dir: `data/processed_langchain_experiment`
- documents_chunked: `3`
- chunks_generated: `19`
- warnings: `3`

## Documents

| Source | Loader | Loaded docs | Chunks | Documents | Document preview | Chunks | Chunk preview |
| --- | --- | ---: | ---: | --- | --- | --- | --- |
| `data/raw/expense_policy.html` | `BSHTMLLoader` | 1 | 4 | `data/processed_langchain_experiment/01_documents/expense-policy-aead3745bd.jsonl` | `data/processed_langchain_experiment/02_documents_preview/expense-policy-aead3745bd.md` | `data/processed_langchain_experiment/03_chunks/expense-policy-aead3745bd.jsonl` | `data/processed_langchain_experiment/04_chunks_preview/expense-policy-aead3745bd.md` |
| `data/raw/extended_expense_scenarios.txt` | `TextLoader` | 1 | 8 | `data/processed_langchain_experiment/01_documents/extended-expense-scenarios-b3f521ebe6.jsonl` | `data/processed_langchain_experiment/02_documents_preview/extended-expense-scenarios-b3f521ebe6.md` | `data/processed_langchain_experiment/03_chunks/extended-expense-scenarios-b3f521ebe6.jsonl` | `data/processed_langchain_experiment/04_chunks_preview/extended-expense-scenarios-b3f521ebe6.md` |
| `data/raw/travel_policy.pdf` | `PyPDFLoader` | 1 | 7 | `data/processed_langchain_experiment/01_documents/travel-policy-2c55f3d095.jsonl` | `data/processed_langchain_experiment/02_documents_preview/travel-policy-2c55f3d095.md` | `data/processed_langchain_experiment/03_chunks/travel-policy-2c55f3d095.jsonl` | `data/processed_langchain_experiment/04_chunks_preview/travel-policy-2c55f3d095.md` |

## Warnings

| Source | Type | Message | Observed at |
| --- | --- | --- | --- |
| `data/raw/airport_transfer_eligibility_decision_tree.png` | `skipped_paid_vision` | Images are skipped because extracting them would require a paid vision call. | `2026-05-10T14:44:09.998698+00:00` |
| `data/raw/corporate_travel_card_rules.png` | `skipped_paid_vision` | Images are skipped because extracting them would require a paid vision call. | `2026-05-10T14:44:09.999147+00:00` |
| `data/raw/per_diem_caps.xlsx` | `unsupported_in_experiment` | XLSX is intentionally skipped in this first LangChain chunking experiment. | `2026-05-10T14:44:10.151532+00:00` |
