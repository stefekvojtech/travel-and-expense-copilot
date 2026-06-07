"""Tests for the cross-platform local server launcher."""

from __future__ import annotations

import argparse
import sys
from typing import Any

import pytest

import scripts.run_local_server as local_server
from scripts.run_local_server import parse_port


@pytest.mark.parametrize("value", ["1", "8000", "65535"])
def test_parse_port_accepts_valid_ports(value: str) -> None:
    """Valid TCP ports should be accepted."""
    assert parse_port(value) == int(value)


@pytest.mark.parametrize("value", ["0", "65536"])
def test_parse_port_rejects_out_of_range_ports(value: str) -> None:
    """Ports outside the TCP range should be rejected."""
    with pytest.raises(argparse.ArgumentTypeError):
        parse_port(value)


def test_main_runs_on_localhost_and_schedules_browser(
    monkeypatch: Any,
    capsys: Any,
) -> None:
    """Default startup should remain local and open the UI when ready."""
    captured: dict[str, Any] = {}

    class FakeThread:
        def __init__(self, *, target: Any, args: tuple[str, str], daemon: bool) -> None:
            captured["thread_target"] = target
            captured["thread_args"] = args
            captured["thread_daemon"] = daemon

        def start(self) -> None:
            captured["thread_started"] = True

    def fake_uvicorn_run(app: str, **kwargs: Any) -> None:
        captured["app"] = app
        captured["uvicorn_kwargs"] = kwargs

    monkeypatch.setattr(sys, "argv", ["run_local_server.py"])
    monkeypatch.setattr(local_server.threading, "Thread", FakeThread)
    monkeypatch.setattr(local_server.uvicorn, "run", fake_uvicorn_run)

    local_server.main()

    assert captured["thread_args"] == (
        "http://127.0.0.1:8000/ui/",
        "http://127.0.0.1:8000/health",
    )
    assert captured["thread_daemon"] is True
    assert captured["thread_started"] is True
    assert captured["app"] == "app.main:app"
    assert captured["uvicorn_kwargs"] == {
        "host": "127.0.0.1",
        "port": 8000,
        "reload": True,
    }
    assert (
        "Starting local copilot UI at http://127.0.0.1:8000/ui/"
        in capsys.readouterr().out
    )
