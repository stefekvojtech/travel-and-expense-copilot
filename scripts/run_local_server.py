"""Run the local FastAPI development server and open its browser UI.

This launcher binds only to localhost and does not perform paid model calls at
startup. Chat requests can still use configured OpenAI services.
"""

from __future__ import annotations

import argparse
import threading
import time
import urllib.error
import urllib.request
import webbrowser

import uvicorn


LOCAL_HOST = "127.0.0.1"
DEFAULT_PORT = 8000


def parse_port(value: str) -> int:
    """Return a valid TCP port parsed from a command-line value."""
    port = int(value)
    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError("port must be between 1 and 65535")
    return port


def open_browser_when_ready(ui_url: str, health_url: str) -> None:
    """Open the UI after the local server starts responding."""
    for _ in range(60):
        try:
            with urllib.request.urlopen(health_url, timeout=0.5) as response:
                if response.status == 200:
                    webbrowser.open(ui_url, new=2)
                    return
        except (OSError, urllib.error.URLError):
            time.sleep(0.25)


def main() -> None:
    """Parse local-development options and run Uvicorn."""
    parser = argparse.ArgumentParser(
        description="Run the copilot UI locally at http://127.0.0.1:8000/ui/."
    )
    parser.add_argument(
        "--port",
        type=parse_port,
        default=DEFAULT_PORT,
        help=f"Localhost port to use (default: {DEFAULT_PORT}).",
    )
    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="Disable automatic server reloads after code changes.",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not open the UI in the default browser.",
    )
    args = parser.parse_args()

    base_url = f"http://{LOCAL_HOST}:{args.port}"
    ui_url = f"{base_url}/ui/"
    print(f"Starting local copilot UI at {ui_url}")

    if not args.no_browser:
        threading.Thread(
            target=open_browser_when_ready,
            args=(ui_url, f"{base_url}/health"),
            daemon=True,
        ).start()

    uvicorn.run(
        "app.main:app",
        host=LOCAL_HOST,
        port=args.port,
        reload=not args.no_reload,
    )


if __name__ == "__main__":
    main()
