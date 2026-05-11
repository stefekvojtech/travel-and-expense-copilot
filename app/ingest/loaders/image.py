"""Normalize image files through OpenAI vision extraction.

The image loader converts receipts and other image sources into Markdown text
and a single image-derived source block. It returns a warning placeholder when
`OPENAI_API_KEY` is unavailable.
"""

from __future__ import annotations

import base64
import mimetypes
import os
from pathlib import Path
from typing import Any

from app.core.config import get_settings
from app.ingest.loaders.models import NormalizedSource, SourceBlock


IMAGE_EXTRACTION_PROMPT = """Extract the useful text from this image for a RAG corpus.

Return clean Markdown only. Preserve visible headings, labels, receipt fields, tables,
totals, dates, vendor names, currencies, and policy-relevant notes when present.
If text is unclear, mark it as [unclear] rather than guessing.
Do not add commentary about the task.
"""


def normalize_image(source_path: Path) -> NormalizedSource:
    """Normalize an image through a vision model into Markdown and source blocks."""
    settings = get_settings()
    if not os.getenv("OPENAI_API_KEY"):
        markdown_text = _missing_key_markdown(source_path)
        return NormalizedSource(
            markdown_text=markdown_text,
            blocks=[
                SourceBlock(
                    text=markdown_text,
                    block_type="image_vision_missing_api_key",
                    section_path="Image Extraction",
                    metadata={"vision_model": settings.vision_model},
                )
            ],
            extraction_method="image_vision_openai",
            extraction_warning="missing_openai_api_key",
        )

    markdown_text = _extract_markdown_with_openai_vision(source_path, settings.vision_model)
    return NormalizedSource(
        markdown_text=markdown_text,
        blocks=[
            SourceBlock(
                text=markdown_text,
                block_type="image_vision_text",
                section_path="Image Extraction",
                metadata={
                    "vision_model": settings.vision_model,
                    "mime_type": _guess_mime_type(source_path),
                },
            )
        ],
        extraction_method="image_vision_openai",
        extraction_warning=None,
    )


def _extract_markdown_with_openai_vision(source_path: Path, vision_model: str) -> str:
    try:
        from langchain_openai import ChatOpenAI
    except ImportError as exc:
        raise RuntimeError(
            "Image vision extraction requires langchain-openai. "
            "Run `uv sync` after updating pyproject.toml."
        ) from exc

    model = ChatOpenAI(model=vision_model, temperature=0)
    response = model.invoke(
        [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": IMAGE_EXTRACTION_PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": _image_data_url(source_path),
                            "detail": "high",
                        },
                    },
                ],
            }
        ]
    )
    return _message_content_to_text(response.content).strip()


def _image_data_url(source_path: Path) -> str:
    encoded_image = base64.b64encode(source_path.read_bytes()).decode("ascii")
    return f"data:{_guess_mime_type(source_path)};base64,{encoded_image}"


def _guess_mime_type(source_path: Path) -> str:
    mime_type, _ = mimetypes.guess_type(source_path.name)
    return mime_type or "application/octet-stream"


def _message_content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts: list[str] = []
        for part in content:
            if isinstance(part, str):
                text_parts.append(part)
            elif isinstance(part, dict) and isinstance(part.get("text"), str):
                text_parts.append(part["text"])
        return "\n".join(text_parts)
    return str(content)


def _missing_key_markdown(source_path: Path) -> str:
    return "\n".join(
        [
            "## Image Extraction",
            "",
            f"Image source: `{source_path.name}`",
            "",
            "Vision extraction requires `OPENAI_API_KEY`.",
        ]
    )
