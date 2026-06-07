"""Routes that expose non-sensitive browser UI configuration."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.schemas import UiConfigResponse
from app.core.config import get_settings


router = APIRouter()


@router.get("/api/ui/config", response_model=UiConfigResponse)
def ui_config() -> UiConfigResponse:
    """Return non-sensitive runtime configuration used by the static UI."""
    settings = get_settings()
    return UiConfigResponse(
        author_name=settings.author_name,
        author_linkedin_url=settings.author_linkedin_url,
        author_github_url=settings.author_github_url,
        question_max_characters=settings.question_max_characters,
    )
