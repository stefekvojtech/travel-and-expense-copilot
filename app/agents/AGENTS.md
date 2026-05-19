# AGENTS.md

## Scope

Applies to `app/agents/`.

This is an empty scaffold for future agent orchestration.

## Planned Role

Agent code should coordinate retrieval, deterministic tools, prompts, answer
generation, confidence explanation, and judge behavior.

## Rules

- Keep prompts in `app/prompts/`, not embedded as large strings in agent modules.
- Keep deterministic business calculations in `app/tools/` or future MCP tools.
- Final grounded answers must include citations and confidence once implemented.
- Final grounded answers should pass through a judge step once implemented.
- If evidence is weak, the agent should abstain instead of guessing.
- Update `docs/architecture.md`, `docs/retrieval.md`, and `docs/api.md` when agent
  behavior becomes implemented.
