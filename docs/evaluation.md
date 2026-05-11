# Evaluation

The project has a golden eval dataset but does not yet have an automated eval
runner.

Dataset:

```text
data/eval/golden_eval_set.jsonl
```

Expected future command:

```powershell
python scripts/run_eval.py
```

That script is not yet developed.

## Current Golden Eval Format

Each JSONL row currently includes fields like:

- `id`
- `question`
- `expected_answer`
- `required_sources`
- `expected_filters`
- `should_abstain`
- `tags`

Example question categories currently represented include:

- alcohol and meal reimbursement
- required evidence for flights
- spreadsheet table lookup
- taxi threshold lookup
- receipt sufficiency
- reimbursement cap behavior
- abstention behavior

## Intended Coverage

The eval suite should cover:

- policy lookup
- table lookup
- citation correctness
- receipt/image extraction
- reimbursement calculation
- abstention behavior

## Intended Metrics

Planned metrics:

- retrieval hit@k
- faithfulness or groundedness
- citation presence
- abstention correctness

The current code can support retrieval-oriented evaluation before full answer
generation exists. For example, an early eval runner could:

1. Load each eval row.
2. Run vector retrieval.
3. Rerank results.
4. Assemble context.
5. Check whether required sources appear in the evidence blocks.
6. Check whether expected metadata filters would have helped.

Answer-level metrics such as faithfulness, confidence, and citation correctness
need the future answer generator and judge flow.

## Current Limitations

There is no `scripts/run_eval.py`.

There is no answer-generation stage to compare against `expected_answer`.

There is no judge prompt or automated groundedness grader.

There is no deterministic calculation tool yet for reimbursement arithmetic.

There is no persistent eval report format yet.

## Suggested First Eval Runner

A practical first implementation would focus on retrieval:

- read `data/eval/golden_eval_set.jsonl`
- run `search_chunks()` for each question
- rerank with `rerank_chunks()`
- assemble context with `assemble_context()`
- mark pass/fail for required source hit in top-k and assembled context
- write a local JSON or Markdown report under `data/eval/`

This avoids answer-generation calls. Retrieval still embeds each query unless
query embeddings are cached or the vector search is replaced with a local test
double.
