# Evaluation

The project has a golden eval dataset and a retrieval-focused automated eval
runner. It does not yet have answer-level faithfulness or judge evaluation.

Dataset:

```text
data/eval/golden_eval_set.jsonl
```

Current command:

```powershell
python scripts/20_run_eval.py
```

This command embeds each eval question through the retrieval stack and therefore
uses the configured paid embedding provider.

Evaluation scripts use the `20_*` numbering band. The first runner should be
`scripts/20_run_eval.py` because ingestion occupies `01_*` through `09_*`, and
retrieval/debug entrypoints occupy `10_*` through `19_*`.

Outputs:

- `data/eval/20_retrieval_eval_report.md`
- `data/eval/20_retrieval_eval_results.jsonl`

## Current Golden Eval Format

Each JSONL row currently includes fields like:

- `id`
- `question`
- `expected_answer`
- `required_sources`
- `required_chunk_groups`
- `expected_filters`
- `should_abstain`
- `tags`

`required_chunk_groups` is stricter than `required_sources`. Each inner list is
one evidence requirement, and any chunk ID in that inner list can satisfy that
requirement. This lets the eval accept equivalent chunks that contain the same
policy fact while still checking for answer-relevant evidence instead of only
checking that the right source file appeared.

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

## Current Metrics

The retrieval eval runner currently tracks:

- retrieval hit@k
- reranked source hit
- assembled-context source hit
- retrieved, reranked, and assembled-context chunk-group hits
- tag-level context source hit rates
- tag-level context chunk hit rates

For each eval row, the runner:

1. Load each eval row.
2. Run vector retrieval.
3. Rerank results.
4. Assemble context.
5. Check whether required sources appear in the evidence blocks.
6. Check whether required chunk groups appear in the retrieved, reranked, and
   assembled-context chunks.

Rows with no `required_sources` or `required_chunk_groups`, such as current
abstention cases, are excluded from those hit-rate denominators. Abstention
correctness remains answer-level future work.

Answer-level metrics such as faithfulness, confidence, and citation correctness
need a future answer-level eval runner and judge flow.

## Current Limitations

There is no answer-level eval runner to compare `scripts/30_ask.py` outputs
against `expected_answer`.

There is no judge prompt or automated groundedness grader.

There is no deterministic calculation tool yet for reimbursement arithmetic.

There is no query embedding cache, so repeated eval runs call the configured
embedding provider for every evaluated question.

## Retrieval Eval Output

The Markdown report is intended for quick human inspection. It contains:

- run timestamp
- eval input and output paths
- retrieval settings
- retrieved, reranked, and context source hit rates
- retrieved, reranked, and context chunk case/group hit rates
- tag breakdown
- failed context-source-hit cases
- failed context-chunk-hit cases

The JSONL results file contains one row per eval case with retrieved sources,
reranked sources, context sources, chunk IDs, source-hit flags, chunk-hit flags,
matched chunk groups, missing chunk groups, and missing required sources.
