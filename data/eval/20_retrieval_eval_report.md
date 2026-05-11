# Retrieval Eval Report

- generated_at: `2026-05-11T19:22:19.405977+00:00`
- eval_path: `data/eval/golden_eval_set.jsonl`
- results_path: `data/eval/20_retrieval_eval_results.jsonl`
- report_path: `data/eval/20_retrieval_eval_report.md`
- total_cases: `36`
- source_required_cases: `34`
- chunk_required_cases: `34`
- chunk_required_groups: `52`
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
| Retrieved chunk case hit | 32 | 34 | 94.1% |
| Reranked chunk case hit | 28 | 34 | 82.4% |
| Context chunk case hit | 27 | 34 | 79.4% |
| Retrieved chunk group hit | 50 | 52 | 96.2% |
| Reranked chunk group hit | 45 | 52 | 86.5% |
| Context chunk group hit | 44 | 52 | 84.6% |

## Tag Breakdown

| Tag | Source cases | Context source hits | Source rate | Chunk cases | Context chunk hits | Chunk rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `alcohol` | 2 | 2 | 100.0% | 2 | 2 | 100.0% |
| `approval` | 1 | 1 | 100.0% | 1 | 1 | 100.0% |
| `booking` | 1 | 1 | 100.0% | 1 | 1 | 100.0% |
| `calculation` | 2 | 1 | 50.0% | 2 | 1 | 50.0% |
| `clarification` | 1 | 1 | 100.0% | 1 | 1 | 100.0% |
| `corporate_card` | 1 | 1 | 100.0% | 1 | 1 | 100.0% |
| `deadline` | 2 | 2 | 100.0% | 2 | 2 | 100.0% |
| `entertainment` | 1 | 1 | 100.0% | 1 | 1 | 100.0% |
| `evidence` | 5 | 5 | 100.0% | 5 | 4 | 80.0% |
| `flights` | 2 | 2 | 100.0% | 2 | 1 | 50.0% |
| `groundedness` | 1 | 0 | 0.0% | 1 | 1 | 100.0% |
| `guardrails` | 3 | 2 | 66.7% | 3 | 3 | 100.0% |
| `hotel` | 6 | 5 | 83.3% | 6 | 4 | 66.7% |
| `html` | 18 | 15 | 83.3% | 18 | 13 | 72.2% |
| `lowest_logical` | 2 | 2 | 100.0% | 2 | 1 | 50.0% |
| `manual_review` | 1 | 1 | 100.0% | 1 | 1 | 100.0% |
| `meals` | 3 | 3 | 100.0% | 3 | 3 | 100.0% |
| `mileage` | 2 | 2 | 100.0% | 2 | 2 | 100.0% |
| `non_reimbursable` | 3 | 3 | 100.0% | 3 | 2 | 66.7% |
| `pdf` | 13 | 11 | 84.6% | 13 | 9 | 69.2% |
| `policy` | 1 | 1 | 100.0% | 1 | 1 | 100.0% |
| `recursive_chunking` | 6 | 6 | 100.0% | 6 | 5 | 83.3% |
| `source_priority` | 3 | 2 | 66.7% | 3 | 2 | 66.7% |
| `table_lookup` | 2 | 2 | 100.0% | 2 | 2 | 100.0% |
| `taxi` | 3 | 1 | 33.3% | 3 | 1 | 33.3% |
| `text` | 6 | 6 | 100.0% | 6 | 5 | 83.3% |
| `time_rule` | 1 | 0 | 0.0% | 1 | 0 | 0.0% |
| `transport` | 1 | 1 | 100.0% | 1 | 1 | 100.0% |
| `xlsx` | 11 | 8 | 72.7% | 11 | 8 | 72.7% |

## Failed Context Source Hits

| ID | Missing sources | Context sources | Tags | Question |
| --- | --- | --- | --- | --- |
| `eval_004` | `expense_policy.html` | `data/raw/per_diem_caps.xlsx` | `xlsx`, `html`, `taxi`, `time_rule` | Can I claim a taxi in Prague at 20:30 under the default after-hours rule? |
| `eval_014` | `per_diem_caps.xlsx` | `data/raw/expense_policy.html`, `data/raw/extended_expense_scenarios.txt`, `data/raw/travel_policy.pdf` | `taxi`, `pdf`, `html`, `xlsx` | Can employees use private taxis by default during business travel? |
| `eval_022` | `expense_policy.html` | `data/raw/travel_policy.pdf`, `data/raw/extended_expense_scenarios.txt`, `data/raw/per_diem_caps.xlsx` | `source_priority`, `pdf` | Which source has priority for travel logistics and approval requirements? |
| `eval_025` | `expense_policy.html` | `data/raw/per_diem_caps.xlsx` | `xlsx`, `html`, `hotel`, `calculation` | A Zurich hotel costs 260 EUR equivalent per night. Is it within cap? |
| `eval_030` | `expense_policy.html` | `data/raw/travel_policy.pdf`, `data/raw/extended_expense_scenarios.txt` | `guardrails`, `groundedness` | Can the assistant answer from general knowledge if the sources do not support the answer? |

## Failed Context Chunk Hits

| ID | Missing chunk groups | Context chunks | Tags | Question |
| --- | --- | --- | --- | --- |
| `eval_002` | `travel-policy-2c55f3d095:chunk:00009` | `expense-policy-aead3745bd:chunk:00003`, `extended-expense-scenarios-b3f521ebe6:chunk:00006`, `travel-policy-2c55f3d095:chunk:00010`, `extended-expense-scenarios-b3f521ebe6:chunk:00002` | `pdf`, `html`, `evidence`, `flights` | What evidence is required for a flight reimbursement? |
| `eval_004` | `expense-policy-aead3745bd:chunk:00006` | `per-diem-caps-1639db42ae:chunk:00037`, `per-diem-caps-1639db42ae:chunk:00076`, `per-diem-caps-1639db42ae:chunk:00038`, `per-diem-caps-1639db42ae:chunk:00036` | `xlsx`, `html`, `taxi`, `time_rule` | Can I claim a taxi in Prague at 20:30 under the default after-hours rule? |
| `eval_014` | `travel-policy-2c55f3d095:chunk:00011`<br>`per-diem-caps-1639db42ae:chunk:00010` OR `per-diem-caps-1639db42ae:chunk:00036` OR `per-diem-caps-1639db42ae:chunk:00037` OR `per-diem-caps-1639db42ae:chunk:00040` OR `per-diem-caps-1639db42ae:chunk:00041` | `expense-policy-aead3745bd:chunk:00006`, `extended-expense-scenarios-b3f521ebe6:chunk:00004`, `travel-policy-2c55f3d095:chunk:00012`, `extended-expense-scenarios-b3f521ebe6:chunk:00005` | `taxi`, `pdf`, `html`, `xlsx` | Can employees use private taxis by default during business travel? |
| `eval_022` | `expense-policy-aead3745bd:chunk:00002` OR `expense-policy-aead3745bd:chunk:00013` | `travel-policy-2c55f3d095:chunk:00003`, `extended-expense-scenarios-b3f521ebe6:chunk:00006`, `travel-policy-2c55f3d095:chunk:00002`, `per-diem-caps-1639db42ae:chunk:00069` | `source_priority`, `pdf` | Which source has priority for travel logistics and approval requirements? |
| `eval_025` | `expense-policy-aead3745bd:chunk:00012` | `per-diem-caps-1639db42ae:chunk:00077`, `per-diem-caps-1639db42ae:chunk:00025`, `per-diem-caps-1639db42ae:chunk:00026`, `per-diem-caps-1639db42ae:chunk:00023` | `xlsx`, `html`, `hotel`, `calculation` | A Zurich hotel costs 260 EUR equivalent per night. Is it within cap? |
| `eval_028` | `travel-policy-2c55f3d095:chunk:00019` | `expense-policy-aead3745bd:chunk:00009`, `travel-policy-2c55f3d095:chunk:00015`, `extended-expense-scenarios-b3f521ebe6:chunk:00007`, `extended-expense-scenarios-b3f521ebe6:chunk:00001` | `html`, `pdf`, `non_reimbursable` | Which expenses are never reimbursable according to the policy? |
| `eval_033` | `extended-expense-scenarios-b3f521ebe6:chunk:00001` | `travel-policy-2c55f3d095:chunk:00005`, `extended-expense-scenarios-b3f521ebe6:chunk:00004`, `travel-policy-2c55f3d095:chunk:00013`, `expense-policy-aead3745bd:chunk:00006` | `text`, `recursive_chunking`, `hotel`, `lowest_logical` | If a hotel far outside the city is cheaper but creates repeated taxi costs, should it automatically be considered the lowest logical option? |
