# AGENTS.md

## Scope

Applies to `app/api/`.

This is an empty scaffold for future API routes.

## Planned Role

API route modules should expose HTTP behavior and delegate business logic to
`app/ingest/`, `app/retrieval/`, `app/agents/`, `app/tools/`, or other reusable
modules.

## Rules

- Keep route handlers thin.
- Use Pydantic models for request and response schemas once API work begins.
- Do not embed prompts or policy business rules directly in route files.
- Do not make policy answers without retrieval-backed evidence.
- Update `docs/api.md` when adding routes or changing API behavior.
