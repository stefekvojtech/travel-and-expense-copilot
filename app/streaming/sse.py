"""Server-sent event formatting helpers for streaming API responses."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any


def format_sse_event(event: str, data: Mapping[str, Any]) -> str:
    """Serialize an event name and JSON payload as an SSE message."""
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {payload}\n\n"
