import _bootstrap  # noqa: F401

from app.core.config import get_settings
from app.ingest.pipeline_chunk import chunk_all_blocks


def main() -> None:
    settings = get_settings()
    # Chunking is separate from ingestion: blocks are extracted evidence,
    # chunks are the embedding-ready work items built from those blocks.
    result = chunk_all_blocks(settings)
    print(
        f"Generated {result.chunk_count} chunks "
        f"from {len(result.chunked_documents)} block files."
    )


if __name__ == "__main__":
    main()
