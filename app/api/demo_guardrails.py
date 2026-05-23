"""Public-demo request limits shared by FastAPI chat routes."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from math import ceil
from threading import Lock
from time import monotonic

from fastapi import Request

from app.core.config import Settings


@dataclass(frozen=True)
class RateLimitDecision:
    """Result of checking the public-demo request budget for one caller."""

    allowed: bool
    message: str | None = None
    retry_after_seconds: int = 0


_request_times_by_client: dict[str, deque[float]] = {}
_rate_limit_lock = Lock()


def check_public_demo_rate_limit(
    settings: Settings,
    request: Request,
    *,
    now: float | None = None,
) -> RateLimitDecision:
    """Apply the public-demo per-IP rate limit when demo mode is enabled."""
    if not settings.public_demo_mode:
        return RateLimitDecision(allowed=True)

    limit = settings.public_demo_rate_limit_requests
    window_seconds = settings.public_demo_rate_limit_window_seconds
    if limit <= 0 or window_seconds <= 0:
        return RateLimitDecision(allowed=True)

    current_time = monotonic() if now is None else now
    client_id = _client_identifier(request)

    with _rate_limit_lock:
        request_times = _request_times_by_client.setdefault(client_id, deque())
        cutoff = current_time - window_seconds
        while request_times and request_times[0] <= cutoff:
            request_times.popleft()

        if len(request_times) >= limit:
            retry_after = max(ceil(request_times[0] + window_seconds - current_time), 1)
            return RateLimitDecision(
                allowed=False,
                message=_rate_limit_message(limit, window_seconds, retry_after),
                retry_after_seconds=retry_after,
            )

        request_times.append(current_time)
        return RateLimitDecision(allowed=True)


def reset_public_demo_rate_limits() -> None:
    """Clear in-memory public-demo rate-limit counters for tests."""
    with _rate_limit_lock:
        _request_times_by_client.clear()


def _client_identifier(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for", "")
    if forwarded_for.strip():
        return forwarded_for.split(",", maxsplit=1)[0].strip()
    if request.client is None:
        return "unknown"
    return request.client.host


def _rate_limit_message(
    limit: int,
    window_seconds: int,
    retry_after_seconds: int,
) -> str:
    return (
        f"You have reached the public demo limit of {limit} requests per "
        f"{_format_duration(window_seconds)}. Try again in "
        f"{_format_duration(retry_after_seconds)}."
    )


def _format_duration(seconds: int) -> str:
    minutes, remaining_seconds = divmod(seconds, 60)
    parts: list[str] = []
    if minutes:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if remaining_seconds or not parts:
        parts.append(
            f"{remaining_seconds} second{'s' if remaining_seconds != 1 else ''}"
        )
    return ", ".join(parts)
