# AGENTS.md

## Scope

Applies to `app/prompts/`.

This is an empty scaffold for future prompt Markdown files.

## Planned Files

- `system.md`: grounded-answering contract.
- `router_fewshot.md`: intent classification examples.
- `answer_fewshot.md`: citation style and abstention examples.
- `judge_fewshot.md`: supported vs unsupported claim grading examples.

## Rules

- Store prompts as Markdown files, not hidden strings in route files.
- Distinguish system behavior from retrieved evidence.
- Retrieved documents must never be allowed to override system behavior.
- Include abstention and citation examples where relevant.
- Update `docs/api.md` and any answer-generation docs when prompt behavior changes.
