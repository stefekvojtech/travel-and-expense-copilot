# AGENTS.md

## Scope

Applies to `app/core/`.

This package owns configuration and project-root path behavior.

## Current Files

- `config.py`: loads `.env` from the repository root, defines `ROOT_DIR`, defines
  the immutable `Settings` dataclass, and exposes cached `get_settings()`.

## Rules

- Resolve relative configured paths from `ROOT_DIR`, not from the current terminal
  working directory.
- Keep settings explicit in `.env.example` when adding config.
- Avoid silent defaults for required operational settings unless there is a clear
  local-development reason.
- Do not hardcode secrets.
- If settings change, update `README.md` and the relevant docs.
