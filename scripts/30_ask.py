"""Ask a policy question and generate a grounded answer.

This script runs retrieval, local reranking, context assembly, and OpenAI-backed
answer generation. Running it performs paid model calls for the query embedding
and final answer model.
"""

import argparse
import sys

from app.agents.answer import answer_policy_question
from app.core.config import get_settings
from app.retrieval.step01_search_chunks import RetrievalFilters


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Generate a grounded policy answer with citations."
    )
    parser.add_argument("question", nargs="?", help="Policy question to answer.")
    parser.add_argument("--k", type=int, help="Number of vector candidates to retrieve.")
    parser.add_argument("--doc-type", help="Filter by source document type, e.g. pdf, xlsx, image.")
    parser.add_argument("--source-path", help="Filter by project-relative source path.")
    parser.add_argument("--section-path", help="Filter by exact section path.")
    parser.add_argument(
        "--show-context",
        action="store_true",
        help="Print the assembled evidence context after the answer.",
    )
    args = parser.parse_args()

    if not args.question:
        parser.error("question is required")

    settings = get_settings()
    filters = RetrievalFilters(
        doc_type=args.doc_type,
        source_path=args.source_path,
        section_path=args.section_path,
    )
    result = answer_policy_question(
        settings,
        args.question,
        filters=filters,
        search_k=args.k,
    )

    print("=== Answer ===\n")
    print(result.answer)
    print(f"\nconfidence: {result.confidence}")
    print(f"abstained: {str(result.abstained).lower()}")
    print(f"citations: {', '.join(result.citations) if result.citations else 'none'}")

    if args.show_context:
        print("\n=== Assembled Context ===\n")
        print(result.context_text)


if __name__ == "__main__":
    main()
