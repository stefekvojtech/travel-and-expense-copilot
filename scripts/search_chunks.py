import argparse
import sys

from app.core.config import get_settings
from app.retrieval.context import assemble_context
from app.retrieval.rerank import rerank_chunks
from app.retrieval.vector_store import RetrievalFilters, get_vector_store_info, search_chunks


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Search embedded policy chunks in the local Chroma vector store."
    )
    parser.add_argument("query", nargs="?", help="Question or search phrase to embed and search.")
    parser.add_argument("--k", type=int, help="Number of chunks to return.")
    parser.add_argument("--doc-type", help="Filter by source document type, e.g. pdf, xlsx, image.")
    parser.add_argument("--source-path", help="Filter by project-relative source path.")
    parser.add_argument("--section-path", help="Filter by exact section path.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Inspect the Chroma collection without calling the embedding model.",
    )
    args = parser.parse_args()

    settings = get_settings()
    if args.dry_run:
        info = get_vector_store_info(settings)
        print(
            f"Chroma collection `{info.collection_name}` contains {info.chunk_count} chunks "
            f"at {info.vector_store_path}."
        )
        return

    if not args.query:
        parser.error("query is required unless --dry-run is used")

    filters = RetrievalFilters(
        doc_type=args.doc_type,
        source_path=args.source_path,
        section_path=args.section_path,
    )
    results = search_chunks(settings, args.query, k=args.k, filters=filters)
    if not results:
        print("No chunks found.")
        return
    reranked_results = rerank_chunks(
        args.query,
        results,
        model_name=settings.rerank_model,
        top_k=len(results),
    )

    assembled_context = assemble_context(
        reranked_results,
        max_blocks=settings.retrieval_context_k,
    )
    print("=== Assembled Context ===\n")
    print(assembled_context.context_text)


if __name__ == "__main__":
    main()
