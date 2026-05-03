from __future__ import annotations

from pathlib import Path

from app.ingest.loaders.models import NormalizedSource, SourceBlock


def normalize_image(source_path: Path) -> NormalizedSource:
    # Future: add OCR or a vision model pass for image-heavy policy sources.
    # The placeholder block keeps images visible in the manifest until extraction exists.
    markdown_text = "\n".join(
        [
            f"Image source: `{source_path.name}`",
            "",
            "Image extraction is not implemented yet.",
        ]
    )
    return NormalizedSource(
        markdown_text=markdown_text,
        blocks=[
            SourceBlock(
                text=markdown_text,
                block_type="image_placeholder",
            )
        ],
        extraction_method="image_placeholder",
        extraction_warning="image_extraction_not_implemented",
    )
