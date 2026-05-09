"""Run incremental raw ingestion for changed source files.

This updates Markdown previews and block JSONL artifacts for new or changed
sources while reusing previous artifacts for unchanged files.
"""

from app.core.config import get_settings
from app.ingest.pipeline_raw import ingest_sources


def main() -> None:
    settings = get_settings()
    # Incremental mode keeps previous Markdown when the raw file hash did not change.
    result = ingest_sources(settings)
    print(
        f"Ingested {len(result.ingested_documents)} documents; "
        f"skipped {len(result.skipped_documents)} unchanged documents; "
        f"removed {len(result.removed_documents)} orphaned Markdown files."
    )
    if result.warnings:
        print(f"Warning: skipped {len(result.warnings)} unsupported files.")


if __name__ == "__main__":
    main()
