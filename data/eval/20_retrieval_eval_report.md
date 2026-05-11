# Retrieval Eval Report

- generated_at: `2026-05-11T18:54:25.355784+00:00`
- eval_path: `data/eval/golden_eval_set.jsonl`
- results_path: `data/eval/20_retrieval_eval_results.jsonl`
- report_path: `data/eval/20_retrieval_eval_report.md`
- total_cases: `36`
- source_required_cases: `34`
- abstention_cases: `2`
- retrieval_top_k: `12`
- retrieval_rerank_k: `5`
- retrieval_context_k: `4`

## Summary

| Metric | Hits | Total | Rate |
| --- | ---: | ---: | ---: |
| Retrieved source hit | 33 | 34 | 97.1% |
| Reranked source hit | 29 | 34 | 85.3% |
| Context source hit | 29 | 34 | 85.3% |

## Tag Breakdown

| Tag | Cases | Context hits | Rate |
| --- | ---: | ---: | ---: |
| `alcohol` | 2 | 2 | 100.0% |
| `approval` | 1 | 1 | 100.0% |
| `booking` | 1 | 1 | 100.0% |
| `calculation` | 2 | 1 | 50.0% |
| `clarification` | 1 | 1 | 100.0% |
| `corporate_card` | 1 | 1 | 100.0% |
| `deadline` | 2 | 2 | 100.0% |
| `entertainment` | 1 | 1 | 100.0% |
| `evidence` | 5 | 5 | 100.0% |
| `flights` | 2 | 2 | 100.0% |
| `groundedness` | 1 | 0 | 0.0% |
| `guardrails` | 3 | 2 | 66.7% |
| `hotel` | 6 | 5 | 83.3% |
| `html` | 18 | 15 | 83.3% |
| `lowest_logical` | 2 | 2 | 100.0% |
| `manual_review` | 1 | 1 | 100.0% |
| `meals` | 3 | 3 | 100.0% |
| `mileage` | 2 | 2 | 100.0% |
| `non_reimbursable` | 3 | 3 | 100.0% |
| `pdf` | 13 | 11 | 84.6% |
| `policy` | 1 | 1 | 100.0% |
| `recursive_chunking` | 6 | 6 | 100.0% |
| `source_priority` | 3 | 2 | 66.7% |
| `table_lookup` | 2 | 2 | 100.0% |
| `taxi` | 3 | 1 | 33.3% |
| `text` | 6 | 6 | 100.0% |
| `time_rule` | 1 | 0 | 0.0% |
| `transport` | 1 | 1 | 100.0% |
| `xlsx` | 11 | 8 | 72.7% |

## Failed Context Source Hits

| ID | Missing sources | Context sources | Tags | Question |
| --- | --- | --- | --- | --- |
| `eval_004` | `expense_policy.html` | `data/raw/per_diem_caps.xlsx` | `xlsx`, `html`, `taxi`, `time_rule` | Can I claim a taxi in Prague at 20:30 under the default after-hours rule? |
| `eval_014` | `per_diem_caps.xlsx` | `data/raw/expense_policy.html`, `data/raw/extended_expense_scenarios.txt`, `data/raw/travel_policy.pdf` | `taxi`, `pdf`, `html`, `xlsx` | Can employees use private taxis by default during business travel? |
| `eval_022` | `expense_policy.html` | `data/raw/travel_policy.pdf`, `data/raw/extended_expense_scenarios.txt`, `data/raw/per_diem_caps.xlsx` | `source_priority`, `pdf` | Which source has priority for travel logistics and approval requirements? |
| `eval_025` | `expense_policy.html` | `data/raw/per_diem_caps.xlsx` | `xlsx`, `html`, `hotel`, `calculation` | A Zurich hotel costs 260 EUR equivalent per night. Is it within cap? |
| `eval_030` | `expense_policy.html` | `data/raw/travel_policy.pdf`, `data/raw/extended_expense_scenarios.txt` | `guardrails`, `groundedness` | Can the assistant answer from general knowledge if the sources do not support the answer? |
