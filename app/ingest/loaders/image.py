from __future__ import annotations

from pathlib import Path


def normalize_image(source_path: Path) -> tuple[str, str, str | None]:
    # Future: add OCR or a vision model pass for image-heavy policy sources.
    return (
        "\n".join(
            [
                f"Image source: `{source_path.name}`",
                "",
                "Image extraction is not implemented yet.",
            ]
        ),
        "image_placeholder",
        "image_extraction_not_implemented",
    )

