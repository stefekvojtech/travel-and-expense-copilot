"""Run retrieval evaluation against the golden eval set.

This command embeds each eval question through the retrieval stack, so a normal
run uses the configured paid embedding provider. It writes a Markdown report and
JSONL row-level results under `data/eval/`.
"""

import argparse
import sys
from pathlib import Path

from app.core.config import ROOT_DIR, get_settings
from app.eval.step01_run_retrieval_eval import run_retrieval_eval


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Run retrieval eval against data/eval/golden_eval_set.jsonl."
    )
    parser.add_argument(
        "--eval-path",
        default="data/eval/golden_eval_set.jsonl",
        help="Path to the golden eval JSONL file.",
    )
    parser.add_argument(
        "--results-path",
        help="Optional path for row-level JSONL results.",
    )
    parser.add_argument(
        "--report-path",
        help="Optional path for the Markdown eval report.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Evaluate only the first N rows. Useful for smoke checks.",
    )
    args = parser.parse_args()

    settings = get_settings()
    eval_path = _resolve_project_path(args.eval_path)
    results_path = _resolve_project_path(args.results_path) if args.results_path else None
    report_path = _resolve_project_path(args.report_path) if args.report_path else None

    eval_run = run_retrieval_eval(
        settings,
        eval_path=eval_path,
        results_path=results_path,
        report_path=report_path,
        limit=args.limit,
    )
    summary = eval_run.summary
    print(f"Evaluated {summary.total_cases} cases.")
    print(
        "retrieved_source_hit: "
        f"{summary.retrieved_source_hits}/{summary.source_required_cases}"
    )
    print(
        "reranked_source_hit: "
        f"{summary.reranked_source_hits}/{summary.source_required_cases}"
    )
    print(
        "context_source_hit: "
        f"{summary.context_source_hits}/{summary.source_required_cases}"
    )
    print(f"abstention_cases: {summary.abstention_cases}")
    print(f"Report: {summary.report_path}")
    print(f"Results: {summary.results_path}")


def _resolve_project_path(path_value: str) -> Path:
    path = Path(path_value)
    return path if path.is_absolute() else ROOT_DIR / path


if __name__ == "__main__":
    main()
