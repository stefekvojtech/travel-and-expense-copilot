# Ingestion Pipeline Report

- generated_at: `2026-05-19T22:31:10.266476+00:00`
- output_dir: `data/processed`
- documents_loaded: `6`
- blocks_normalized: `255`
- chunks_generated: `148`
- warnings: `0`

## Documents

| Source | Loader | Loaded docs | Blocks | Chunks | Loaded docs | Loaded preview | Blocks | Blocks preview | Chunks | Chunk preview |
| --- | --- | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- |
| `data/raw/airport_transfer_eligibility_decision_tree.png` | `image_vision_openai` | 1 | 1 | 7 | `data/processed/01_loaded_documents/airport-transfer-eligibility-decision-tree-544132a482.jsonl` | `data/processed/01_loaded_documents_preview/airport-transfer-eligibility-decision-tree-544132a482.md` | `data/processed/02_normalized_blocks/airport-transfer-eligibility-decision-tree-544132a482.jsonl` | `data/processed/02_normalized_blocks_preview/airport-transfer-eligibility-decision-tree-544132a482.md` | `data/processed/03_chunks/airport-transfer-eligibility-decision-tree-544132a482.jsonl` | `data/processed/03_chunks_preview/airport-transfer-eligibility-decision-tree-544132a482.md` |
| `data/raw/corporate_travel_card_rules.png` | `image_vision_openai` | 1 | 1 | 9 | `data/processed/01_loaded_documents/corporate-travel-card-rules-b50727f8ce.jsonl` | `data/processed/01_loaded_documents_preview/corporate-travel-card-rules-b50727f8ce.md` | `data/processed/02_normalized_blocks/corporate-travel-card-rules-b50727f8ce.jsonl` | `data/processed/02_normalized_blocks_preview/corporate-travel-card-rules-b50727f8ce.md` | `data/processed/03_chunks/corporate-travel-card-rules-b50727f8ce.jsonl` | `data/processed/03_chunks_preview/corporate-travel-card-rules-b50727f8ce.md` |
| `data/raw/expense_policy.html` | `BSHTMLLoader` | 1 | 70 | 13 | `data/processed/01_loaded_documents/expense-policy-aead3745bd.jsonl` | `data/processed/01_loaded_documents_preview/expense-policy-aead3745bd.md` | `data/processed/02_normalized_blocks/expense-policy-aead3745bd.jsonl` | `data/processed/02_normalized_blocks_preview/expense-policy-aead3745bd.md` | `data/processed/03_chunks/expense-policy-aead3745bd.jsonl` | `data/processed/03_chunks_preview/expense-policy-aead3745bd.md` |
| `data/raw/extended_expense_scenarios.txt` | `TextLoader` | 1 | 1 | 8 | `data/processed/01_loaded_documents/extended-expense-scenarios-b3f521ebe6.jsonl` | `data/processed/01_loaded_documents_preview/extended-expense-scenarios-b3f521ebe6.md` | `data/processed/02_normalized_blocks/extended-expense-scenarios-b3f521ebe6.jsonl` | `data/processed/02_normalized_blocks_preview/extended-expense-scenarios-b3f521ebe6.md` | `data/processed/03_chunks/extended-expense-scenarios-b3f521ebe6.jsonl` | `data/processed/03_chunks_preview/extended-expense-scenarios-b3f521ebe6.md` |
| `data/raw/per_diem_caps.xlsx` | `openpyxl_row_level` | 1 | 105 | 89 | `data/processed/01_loaded_documents/per-diem-caps-1639db42ae.jsonl` | `data/processed/01_loaded_documents_preview/per-diem-caps-1639db42ae.md` | `data/processed/02_normalized_blocks/per-diem-caps-1639db42ae.jsonl` | `data/processed/02_normalized_blocks_preview/per-diem-caps-1639db42ae.md` | `data/processed/03_chunks/per-diem-caps-1639db42ae.jsonl` | `data/processed/03_chunks_preview/per-diem-caps-1639db42ae.md` |
| `data/raw/travel_policy.pdf` | `PyPDFLoader` | 1 | 77 | 22 | `data/processed/01_loaded_documents/travel-policy-2c55f3d095.jsonl` | `data/processed/01_loaded_documents_preview/travel-policy-2c55f3d095.md` | `data/processed/02_normalized_blocks/travel-policy-2c55f3d095.jsonl` | `data/processed/02_normalized_blocks_preview/travel-policy-2c55f3d095.md` | `data/processed/03_chunks/travel-policy-2c55f3d095.jsonl` | `data/processed/03_chunks_preview/travel-policy-2c55f3d095.md` |

## Warnings

| Source | Type | Message | Observed at |
| --- | --- | --- | --- |
|  |  | No warnings. |  |
