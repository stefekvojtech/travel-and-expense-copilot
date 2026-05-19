# AGENTS.md

## Scope

Applies to `app/streaming/`.

This is an empty scaffold for future streaming helpers.

## Planned Role

Streaming code should support incremental answer delivery from the future API/UI
without mixing transport details into retrieval or answer-generation logic.

## Rules

- Keep streaming helpers separate from core retrieval and answer-generation logic.
- Preserve citation and debug metadata when streaming final responses.
- Update `docs/api.md` when streaming behavior is implemented or changed.
