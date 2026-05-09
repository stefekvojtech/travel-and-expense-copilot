# LangChain Chunking Experiment Report

- generated_at: `2026-05-08T19:00:09.189922+00:00`
- output_dir: `data/processed_langchain_experiment`
- documents_chunked: `3`
- chunks_generated: `19`
- warnings: `4`

## Documents

| Source | Loader | Loaded docs | Chunks | Preview |
| --- | --- | ---: | ---: | --- |
| `data/raw/expense_policy.html` | `BSHTMLLoader` | 1 | 4 | `data/processed_langchain_experiment/previews/expense-policy-aead3745bd.md` |
| `data/raw/extended_expense_scenarios.txt` | `TextLoader` | 1 | 8 | `data/processed_langchain_experiment/previews/extended-expense-scenarios-b3f521ebe6.md` |
| `data/raw/travel_policy.pdf` | `PyPDFLoader` | 4 | 7 | `data/processed_langchain_experiment/previews/travel-policy-2c55f3d095.md` |

## Warnings

- `data/raw/AGENTS.md` `unsupported_suffix`: Skipped .md.
- `data/raw/airport_transfer_eligibility_decision_tree.png` `skipped_paid_vision`: Images are skipped because extracting them would require a paid vision call.
- `data/raw/corporate_travel_card_rules.png` `skipped_paid_vision`: Images are skipped because extracting them would require a paid vision call.
- `data/raw/per_diem_caps.xlsx` `unsupported_in_experiment`: XLSX is intentionally skipped in this first LangChain chunking experiment.
