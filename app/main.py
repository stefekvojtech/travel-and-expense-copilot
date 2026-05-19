"""FastAPI application entrypoint for the local copilot backend and UI."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.api.chat import router as chat_router
from app.api.downloads import router as downloads_router
from app.api.ui import router as ui_router


UI_DIRECTORY = Path(__file__).resolve().parent / "ui"

app = FastAPI(
    title="Travel and Expense Policy Copilot",
    version="0.1.0",
)
app.include_router(chat_router)
app.include_router(downloads_router)
app.include_router(ui_router)
app.mount("/ui", StaticFiles(directory=UI_DIRECTORY, html=True), name="ui")


@app.get("/", include_in_schema=False)
def ui_root() -> RedirectResponse:
    """Redirect local browser users to the static copilot UI."""
    return RedirectResponse(url="/ui/")
