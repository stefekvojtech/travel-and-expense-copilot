"""Create readable Markdown previews from production chunk JSONL artifacts."""

from app.core.config import get_settings
from app.ingest.pipeline_chunk_preview import preview_all_chunks


def main() -> None:
    settings = get_settings()
    result = preview_all_chunks(settings)
    print(
        f"Generated chunk previews for {len(result.previewed_documents)} documents "
        f"and {result.chunk_count} chunks."
    )
    print(f"Output written to {result.output_dir}")


if __name__ == "__main__":
    main()
