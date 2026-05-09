"""Embed processed chunk JSONL files into the local Chroma vector store.

Use `--dry-run` to inspect chunk counts and target paths without making paid
embedding calls.
"""

import argparse

from app.core.config import get_settings
from app.ingest.pipeline_embed import embed_all_chunks


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Embed processed chunk JSONL files into the local Chroma store."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Count chunks and validate paths without calling the embedding model.",
    )
    args = parser.parse_args()

    settings = get_settings()
    result = embed_all_chunks(settings, dry_run=args.dry_run)
    if result.embedded:
        print(
            f"Embedded {result.chunk_count} chunks into Chroma collection "
            f"`{result.collection_name}` at {result.vector_store_path}."
        )
    else:
        print(
            f"Dry run: found {result.chunk_count} chunks for Chroma collection "
            f"`{result.collection_name}` at {result.vector_store_path}."
        )


if __name__ == "__main__":
    main()
