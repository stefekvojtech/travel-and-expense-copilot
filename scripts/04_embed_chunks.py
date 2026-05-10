"""Embed stage 03 chunks into the local Chroma vector store.

This command calls the configured OpenAI embedding model and consumes paid
credits. The previous collection is replaced only after the new collection is
fully written and count-verified.
"""

from app.core.config import get_settings
from app.ingest.step04_embed_chunks import embed_all_chunks


def main() -> None:
    settings = get_settings()
    result = embed_all_chunks(settings)
    print(
        f"Embedded {result.chunk_count} chunks into Chroma collection "
        f"`{result.collection_name}` at {result.vector_store_path}."
    )


if __name__ == "__main__":
    main()
