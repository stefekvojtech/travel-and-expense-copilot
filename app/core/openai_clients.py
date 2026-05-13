"""Build OpenAI HTTP clients for local runtime calls.

OpenAI calls should not inherit shell proxy settings by default. Some local
agent environments set HTTP proxy variables to closed ports, which prevents
retrieval and answer generation from reaching the OpenAI API.
"""

from __future__ import annotations

from typing import Any


def build_openai_http_client() -> Any:
    """Return an OpenAI-compatible HTTP client that ignores environment proxies."""
    try:
        from openai import DefaultHttpxClient
    except ImportError as exc:
        raise RuntimeError(
            "OpenAI HTTP client construction requires the openai package. Run "
            "`python -m pip install -e .` from the project root."
        ) from exc

    return DefaultHttpxClient(trust_env=False)
