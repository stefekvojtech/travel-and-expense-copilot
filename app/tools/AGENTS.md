# AGENTS.md

## Scope

Applies to `app/tools/`.

This is an empty scaffold for future deterministic Python tools.

## Planned Tools

- `search_policy_corpus`
- `fetch_source_window`
- `explain_confidence`

Related future MCP tools may live under `mcp_server/` once that directory exists:

- `compute_per_diem`
- `policy_cap_lookup`
- `sum_receipt_lines`
- `normalize_currency`

## Rules

- Use deterministic code for arithmetic and policy-cap lookup.
- Add docstrings to tools.
- Keep tool inputs and outputs typed.
- Do not call an LLM for calculations that local code can perform.
- Update `.env.example` if a tool introduces configuration.
- Update docs when adding a tool or changing tool behavior.
