"""Force raw ingestion for all supported source files.

This rebuilds preview Markdown and block JSONL artifacts even when source
hashes match previous manifest entries. Image ingestion may call a paid vision
model when an OpenAI API key is configured.
"""

from app.core.config import get_settings
from app.ingest.pipeline_raw import ingest_sources


def main() -> None:
    settings = get_settings()
    # Force mode rebuilds every preview file from data/raw, even if hashes match.
    result = ingest_sources(settings, force=True)
    print(
        f"Force re-ingested {len(result.ingested_documents)} documents; "
        f"removed {len(result.removed_documents)} orphaned preview files."
    )
    if result.warnings:
        print(f"Warning: skipped {len(result.warnings)} unsupported files.")


if __name__ == "__main__":
    main()
