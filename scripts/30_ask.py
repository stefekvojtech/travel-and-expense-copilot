"""Ask a policy question and generate a grounded answer.

This script runs retrieval, local reranking, context assembly, and OpenAI-backed
answer generation. Running it performs paid model calls for the query embedding
and final answer model.
"""

import argparse
import logging
import sys

from app.agents.answer import AnswerGenerationError, answer_policy_question
from app.core.config import get_settings
from app.retrieval.step01_search_chunks import RetrievalFilters


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)

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
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Re-raise errors with full tracebacks instead of friendly CLI messages.",
    )
    args = parser.parse_args()

    if not args.question:
        parser.error("question is required")

    try:
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
    except Exception as exc:
        if args.debug:
            raise
        prefix = "Answer generation failed"
        if isinstance(exc, AnswerGenerationError):
            prefix = "Answer generation failed validation"
        print(f"{prefix}: {exc}", file=sys.stderr)
        return 1

    print("=== Answer ===\n")
    print(result.answer)
    print(f"\nconfidence: {result.confidence}")
    print(f"abstained: {str(result.abstained).lower()}")
    print(f"citations: {', '.join(result.citations) if result.citations else 'none'}")
    if result.validation_warnings:
        print("validation_warnings:")
        for warning in result.validation_warnings:
            print(f"- {warning}")

    if args.show_context:
        print("\n=== Assembled Context ===\n")
        print(result.context_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
