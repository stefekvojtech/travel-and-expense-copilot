# AGENTS.md

## Scope

Applies to `data/eval/`.

This directory contains golden evaluation examples.

## Current Files

- `golden_eval_set.jsonl`: evaluation rows with questions, expected answers,
  required sources, expected filters, abstention flags, and tags.

## Rules

- Keep eval rows as JSONL unless the eval framework deliberately changes.
- Cover policy lookup, table lookup, citation correctness, receipt/image
  extraction, reimbursement calculation, and abstention behavior.
- Do not assume answer-level metrics are implemented yet.
- Update `docs/evaluation.md` when eval schema, coverage, or commands change.
