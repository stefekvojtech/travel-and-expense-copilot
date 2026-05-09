import argparse
import sys

from app.core.config import Settings, get_settings
from app.ingest.pipeline_chunk import chunk_all_blocks
from app.ingest.pipeline_embed import embed_all_chunks
from app.ingest.pipeline_raw import ingest_sources
from app.retrieval.context import assemble_context
from app.retrieval.rerank import rerank_chunks
from app.retrieval.vector_store import RetrievalFilters, get_vector_store_info, search_chunks


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Run the local Travel & Expense Copilot pipeline."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser(
        "ingest",
        help="Normalize raw sources into Markdown previews and block JSONL.",
    )
    ingest_parser.add_argument(
        "--force",
        action="store_true",
        help="Rebuild all supported raw sources even when content hashes match.",
    )

    subparsers.add_parser(
        "chunk",
        help="Build embedding-ready chunk JSONL from block artifacts.",
    )

    embed_parser = subparsers.add_parser(
        "embed",
        help="Embed chunk JSONL into the local Chroma vector store.",
    )
    embed_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Count chunks and validate paths without calling the embedding model.",
    )

    search_parser = subparsers.add_parser(
        "search",
        help="Search embedded chunks and print citation-ready assembled context.",
    )
    search_parser.add_argument(
        "query",
        nargs="?",
        help="Question or search phrase to embed and search.",
    )
    search_parser.add_argument("--k", type=int, help="Number of chunks to retrieve.")
    search_parser.add_argument(
        "--doc-type",
        help="Filter by source document type, e.g. pdf, xlsx, image.",
    )
    search_parser.add_argument(
        "--source-path",
        help="Filter by project-relative source path.",
    )
    search_parser.add_argument("--section-path", help="Filter by exact section path.")
    search_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Inspect the Chroma collection without calling the embedding model.",
    )

    args = parser.parse_args()
    settings = get_settings()

    if args.command == "ingest":
        _run_ingest(settings, force=args.force)
    elif args.command == "chunk":
        _run_chunk(settings)
    elif args.command == "embed":
        _run_embed(settings, dry_run=args.dry_run)
    elif args.command == "search":
        _run_search(args, settings, parser=search_parser)


def _run_ingest(settings: Settings, *, force: bool) -> None:
    result = ingest_sources(settings, force=force)
    action = "Force re-ingested" if force else "Ingested"
    print(
        f"{action} {len(result.ingested_documents)} documents; "
        f"skipped {len(result.skipped_documents)} unchanged documents; "
        f"removed {len(result.removed_documents)} orphaned Markdown/block files."
    )
    if result.warnings:
        print(f"Warning: skipped {len(result.warnings)} unsupported files.")


def _run_chunk(settings: Settings) -> None:
    result = chunk_all_blocks(settings)
    print(
        f"Generated {result.chunk_count} chunks "
        f"from {len(result.chunked_documents)} block files."
    )


def _run_embed(settings: Settings, *, dry_run: bool) -> None:
    result = embed_all_chunks(settings, dry_run=dry_run)
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


def _run_search(
    args: argparse.Namespace,
    settings: Settings,
    *,
    parser: argparse.ArgumentParser,
) -> None:
    if args.dry_run:
        info = get_vector_store_info(settings)
        print(
            f"Chroma collection `{info.collection_name}` contains {info.chunk_count} "
            f"chunks at {info.vector_store_path}."
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
        max_total_tokens=settings.retrieval_context_max_tokens,
        max_block_tokens=settings.retrieval_context_max_block_tokens,
    )
    print("=== Assembled Context ===\n")
    print(assembled_context.context_text)


if __name__ == "__main__":
    main()
