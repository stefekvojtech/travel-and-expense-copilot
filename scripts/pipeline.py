"""Run the full raw-source to vector-store corpus build.

This command runs stages 01 through 04: load documents, normalize blocks, chunk
blocks, and embed chunks into Chroma. Image loading and embedding may call paid
OpenAI models when configured.
"""

import sys

from app.core.config import get_settings
from app.ingest.pipeline_report import write_pipeline_report
from app.ingest.step01_load_documents import load_all_documents
from app.ingest.step02_normalize_blocks import normalize_all_blocks
from app.ingest.step03_chunk_blocks import chunk_all_blocks
from app.ingest.step04_embed_chunks import embed_all_chunks


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    settings = get_settings()
    runtime_warnings = []

    load_result = load_all_documents(settings)
    runtime_warnings.extend(load_result.warnings)
    write_pipeline_report(settings, runtime_warnings=runtime_warnings)
    print(
        f"01 loaded {sum(document.loaded_document_count for document in load_result.documents)} "
        f"document records from {len(load_result.documents)} source files."
    )

    normalize_result = normalize_all_blocks(settings)
    runtime_warnings.extend(normalize_result.warnings)
    write_pipeline_report(settings, runtime_warnings=runtime_warnings)
    print(
        f"02 normalized {normalize_result.block_count} blocks "
        f"from {len(normalize_result.documents)} source files."
    )

    chunk_result = chunk_all_blocks(settings)
    write_pipeline_report(settings, runtime_warnings=runtime_warnings)
    print(
        f"03 generated {chunk_result.chunk_count} chunks "
        f"from {len(chunk_result.chunked_documents)} block files."
    )

    embed_result = embed_all_chunks(settings)
    print(
        f"04 embedded {embed_result.chunk_count} chunks into Chroma collection "
        f"`{embed_result.collection_name}` at {embed_result.vector_store_path}."
    )


if __name__ == "__main__":
    main()
