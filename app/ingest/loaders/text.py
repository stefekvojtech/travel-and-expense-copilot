from __future__ import annotations

from pathlib import Path

from app.ingest.loaders.common import clean_text
from app.ingest.loaders.models import NormalizedSource, SourceBlock


def normalize_text(source_path: Path) -> NormalizedSource:
    text = source_path.read_text(encoding="utf-8")
    paragraphs = [clean_text(paragraph) for paragraph in text.split("\n\n")]
    markdown_text = "\n\n".join(paragraph for paragraph in paragraphs if paragraph)

    # Keep plain text as one large block so chunking tests the recursive splitter.
    return NormalizedSource(
        markdown_text=markdown_text,
        blocks=[
            SourceBlock(
                text=markdown_text,
                block_type="plain_text",
            )
        ],
        extraction_method="plain_text",
    )
