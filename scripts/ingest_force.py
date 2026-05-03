import _bootstrap  # noqa: F401

from app.core.config import get_settings
from app.ingest.pipeline import ingest_sources


def main() -> None:
    settings = get_settings()
    # Force mode rebuilds every Markdown file from data/raw, even if hashes match.
    result = ingest_sources(settings, force=True)
    print(
        f"Force re-ingested {len(result.ingested_documents)} documents; "
        f"removed {len(result.removed_documents)} orphaned Markdown files."
    )
    if result.warnings:
        print(f"Warning: skipped {len(result.warnings)} unsupported files.")


if __name__ == "__main__":
    main()
