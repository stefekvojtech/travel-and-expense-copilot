"""Rebuild stage 03 chunk artifacts and previews from normalized blocks."""

from app.core.config import get_settings
from app.ingest.pipeline_report import write_pipeline_report
from app.ingest.step03_chunk_blocks import chunk_all_blocks


def main() -> None:
    settings = get_settings()
    result = chunk_all_blocks(settings)
    write_pipeline_report(settings)
    print(
        f"Generated {result.chunk_count} chunks "
        f"from {len(result.chunked_documents)} block files."
    )


if __name__ == "__main__":
    main()
