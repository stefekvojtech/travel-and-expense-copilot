"""Run retrieval-focused evaluation against the golden eval dataset.

This module evaluates whether the current retrieval stack finds the expected
policy sources for each golden question. It calls query embedding through
retrieval, so a normal run uses the configured paid embedding provider.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.config import Settings
from app.ingest.artifact_io import write_jsonl
from app.ingest.artifact_paths import project_relative_path, write_text_if_changed
from app.retrieval.step01_search_chunks import RetrievedChunk, search_chunks
from app.retrieval.step02_rerank_chunks import RerankedChunk, rerank_chunks
from app.retrieval.step03_assemble_context import AssembledContext, assemble_context


DEFAULT_RESULTS_FILENAME = "20_retrieval_eval_results.jsonl"
DEFAULT_REPORT_FILENAME = "20_retrieval_eval_report.md"
ChunkGroup = list[str]


@dataclass(frozen=True)
class EvalExample:
    id: str
    question: str
    expected_answer: str
    required_sources: list[str]
    required_chunk_groups: list[ChunkGroup]
    expected_filters: dict[str, Any]
    should_abstain: bool
    tags: list[str]


@dataclass(frozen=True)
class RetrievalEvalResult:
    id: str
    question: str
    required_sources: list[str]
    required_chunk_groups: list[ChunkGroup]
    should_abstain: bool
    tags: list[str]
    retrieved_sources: list[str]
    reranked_sources: list[str]
    context_sources: list[str]
    retrieved_chunk_ids: list[str]
    reranked_chunk_ids: list[str]
    context_chunk_ids: list[str]
    required_sources_in_retrieved: list[str]
    required_sources_in_reranked: list[str]
    required_sources_in_context: list[str]
    missing_sources_in_retrieved: list[str]
    missing_sources_in_reranked: list[str]
    missing_sources_in_context: list[str]
    matched_chunk_groups_in_retrieved: list[ChunkGroup]
    matched_chunk_groups_in_reranked: list[ChunkGroup]
    matched_chunk_groups_in_context: list[ChunkGroup]
    missing_chunk_groups_in_retrieved: list[ChunkGroup]
    missing_chunk_groups_in_reranked: list[ChunkGroup]
    missing_chunk_groups_in_context: list[ChunkGroup]
    passed_retrieved_source_hit: bool | None
    passed_reranked_source_hit: bool | None
    passed_context_source_hit: bool | None
    passed_retrieved_chunk_hit: bool | None
    passed_reranked_chunk_hit: bool | None
    passed_context_chunk_hit: bool | None


@dataclass(frozen=True)
class RetrievalEvalSummary:
    generated_at: str
    eval_path: str
    results_path: str
    report_path: str
    total_cases: int
    source_required_cases: int
    chunk_required_cases: int
    chunk_required_groups: int
    abstention_cases: int
    retrieved_source_hits: int
    reranked_source_hits: int
    context_source_hits: int
    retrieved_chunk_case_hits: int
    reranked_chunk_case_hits: int
    context_chunk_case_hits: int
    retrieved_chunk_group_hits: int
    reranked_chunk_group_hits: int
    context_chunk_group_hits: int
    retrieval_top_k: int
    retrieval_rerank_k: int
    retrieval_context_k: int


@dataclass(frozen=True)
class RetrievalEvalRun:
    summary: RetrievalEvalSummary
    results: list[RetrievalEvalResult]
    report_text: str


def run_retrieval_eval(
    settings: Settings,
    *,
    eval_path: Path,
    results_path: Path | None = None,
    report_path: Path | None = None,
    limit: int | None = None,
    write_outputs: bool = True,
) -> RetrievalEvalRun:
    """Run retrieval eval and optionally write JSONL and Markdown outputs."""
    examples = load_eval_examples(eval_path)
    if limit is not None:
        examples = examples[:limit]

    output_results_path = results_path or eval_path.parent / DEFAULT_RESULTS_FILENAME
    output_report_path = report_path or eval_path.parent / DEFAULT_REPORT_FILENAME

    results = [
        _evaluate_example(settings, example)
        for example in examples
    ]
    summary = _summarize_results(
        settings,
        eval_path=eval_path,
        results_path=output_results_path,
        report_path=output_report_path,
        results=results,
    )
    report_text = _format_report(summary, results)

    if write_outputs:
        write_jsonl(output_results_path, [asdict(result) for result in results])
        write_text_if_changed(output_report_path, report_text)

    return RetrievalEvalRun(summary=summary, results=results, report_text=report_text)


def load_eval_examples(eval_path: Path) -> list[EvalExample]:
    """Load golden eval rows from JSONL."""
    examples: list[EvalExample] = []
    for line in eval_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        examples.append(
            EvalExample(
                id=str(row["id"]),
                question=str(row["question"]),
                expected_answer=str(row.get("expected_answer", "")),
                required_sources=list(row.get("required_sources", [])),
                required_chunk_groups=_read_chunk_groups(row),
                expected_filters=dict(row.get("expected_filters", {})),
                should_abstain=bool(row.get("should_abstain", False)),
                tags=list(row.get("tags", [])),
            )
        )
    return examples


def _evaluate_example(settings: Settings, example: EvalExample) -> RetrievalEvalResult:
    retrieved_chunks = search_chunks(
        settings,
        example.question,
        k=settings.retrieval_top_k,
    )
    reranked_chunks = rerank_chunks(
        example.question,
        retrieved_chunks,
        model_name=settings.rerank_model,
        top_k=min(settings.retrieval_rerank_k, len(retrieved_chunks)),
    )
    assembled_context = assemble_context(
        reranked_chunks,
        max_blocks=settings.retrieval_context_k,
        max_total_tokens=settings.retrieval_context_max_tokens,
        max_block_tokens=settings.retrieval_context_max_block_tokens,
    )

    retrieved_sources = _unique_sources_from_chunks(retrieved_chunks)
    reranked_sources = _unique_sources_from_chunks(reranked_chunks)
    context_sources = _unique_sources_from_context(assembled_context)
    retrieved_chunk_ids = _chunk_ids(retrieved_chunks)
    reranked_chunk_ids = _chunk_ids(reranked_chunks)
    context_chunk_ids = [
        block.chunk_id
        for block in assembled_context.evidence_blocks
        if block.chunk_id is not None
    ]

    retrieved_hits, retrieved_missing = _source_hits(
        required_sources=example.required_sources,
        found_sources=retrieved_sources,
    )
    reranked_hits, reranked_missing = _source_hits(
        required_sources=example.required_sources,
        found_sources=reranked_sources,
    )
    context_hits, context_missing = _source_hits(
        required_sources=example.required_sources,
        found_sources=context_sources,
    )
    retrieved_chunk_hits, retrieved_chunk_missing = _chunk_group_hits(
        required_chunk_groups=example.required_chunk_groups,
        found_chunk_ids=retrieved_chunk_ids,
    )
    reranked_chunk_hits, reranked_chunk_missing = _chunk_group_hits(
        required_chunk_groups=example.required_chunk_groups,
        found_chunk_ids=reranked_chunk_ids,
    )
    context_chunk_hits, context_chunk_missing = _chunk_group_hits(
        required_chunk_groups=example.required_chunk_groups,
        found_chunk_ids=context_chunk_ids,
    )

    has_required_sources = bool(example.required_sources)
    has_required_chunk_groups = bool(example.required_chunk_groups)
    return RetrievalEvalResult(
        id=example.id,
        question=example.question,
        required_sources=example.required_sources,
        required_chunk_groups=example.required_chunk_groups,
        should_abstain=example.should_abstain,
        tags=example.tags,
        retrieved_sources=retrieved_sources,
        reranked_sources=reranked_sources,
        context_sources=context_sources,
        retrieved_chunk_ids=retrieved_chunk_ids,
        reranked_chunk_ids=reranked_chunk_ids,
        context_chunk_ids=context_chunk_ids,
        required_sources_in_retrieved=retrieved_hits,
        required_sources_in_reranked=reranked_hits,
        required_sources_in_context=context_hits,
        missing_sources_in_retrieved=retrieved_missing,
        missing_sources_in_reranked=reranked_missing,
        missing_sources_in_context=context_missing,
        matched_chunk_groups_in_retrieved=retrieved_chunk_hits,
        matched_chunk_groups_in_reranked=reranked_chunk_hits,
        matched_chunk_groups_in_context=context_chunk_hits,
        missing_chunk_groups_in_retrieved=retrieved_chunk_missing,
        missing_chunk_groups_in_reranked=reranked_chunk_missing,
        missing_chunk_groups_in_context=context_chunk_missing,
        passed_retrieved_source_hit=(
            not retrieved_missing if has_required_sources else None
        ),
        passed_reranked_source_hit=not reranked_missing if has_required_sources else None,
        passed_context_source_hit=not context_missing if has_required_sources else None,
        passed_retrieved_chunk_hit=(
            not retrieved_chunk_missing if has_required_chunk_groups else None
        ),
        passed_reranked_chunk_hit=(
            not reranked_chunk_missing if has_required_chunk_groups else None
        ),
        passed_context_chunk_hit=(
            not context_chunk_missing if has_required_chunk_groups else None
        ),
    )


def _summarize_results(
    settings: Settings,
    *,
    eval_path: Path,
    results_path: Path,
    report_path: Path,
    results: list[RetrievalEvalResult],
) -> RetrievalEvalSummary:
    source_results = [
        result
        for result in results
        if result.passed_retrieved_source_hit is not None
    ]
    chunk_results = [
        result
        for result in results
        if result.passed_retrieved_chunk_hit is not None
    ]
    return RetrievalEvalSummary(
        generated_at=datetime.now(timezone.utc).isoformat(),
        eval_path=project_relative_path(eval_path),
        results_path=project_relative_path(results_path),
        report_path=project_relative_path(report_path),
        total_cases=len(results),
        source_required_cases=len(source_results),
        chunk_required_cases=len(chunk_results),
        chunk_required_groups=sum(
            len(result.required_chunk_groups)
            for result in chunk_results
        ),
        abstention_cases=sum(1 for result in results if result.should_abstain),
        retrieved_source_hits=sum(
            1 for result in source_results if result.passed_retrieved_source_hit
        ),
        reranked_source_hits=sum(
            1 for result in source_results if result.passed_reranked_source_hit
        ),
        context_source_hits=sum(
            1 for result in source_results if result.passed_context_source_hit
        ),
        retrieved_chunk_case_hits=sum(
            1 for result in chunk_results if result.passed_retrieved_chunk_hit
        ),
        reranked_chunk_case_hits=sum(
            1 for result in chunk_results if result.passed_reranked_chunk_hit
        ),
        context_chunk_case_hits=sum(
            1 for result in chunk_results if result.passed_context_chunk_hit
        ),
        retrieved_chunk_group_hits=sum(
            len(result.matched_chunk_groups_in_retrieved)
            for result in chunk_results
        ),
        reranked_chunk_group_hits=sum(
            len(result.matched_chunk_groups_in_reranked)
            for result in chunk_results
        ),
        context_chunk_group_hits=sum(
            len(result.matched_chunk_groups_in_context)
            for result in chunk_results
        ),
        retrieval_top_k=settings.retrieval_top_k,
        retrieval_rerank_k=settings.retrieval_rerank_k,
        retrieval_context_k=settings.retrieval_context_k,
    )


def _format_report(
    summary: RetrievalEvalSummary,
    results: list[RetrievalEvalResult],
) -> str:
    lines = [
        "# Retrieval Eval Report",
        "",
        f"- generated_at: `{summary.generated_at}`",
        f"- eval_path: `{summary.eval_path}`",
        f"- results_path: `{summary.results_path}`",
        f"- report_path: `{summary.report_path}`",
        f"- total_cases: `{summary.total_cases}`",
        f"- source_required_cases: `{summary.source_required_cases}`",
        f"- chunk_required_cases: `{summary.chunk_required_cases}`",
        f"- chunk_required_groups: `{summary.chunk_required_groups}`",
        f"- abstention_cases: `{summary.abstention_cases}`",
        f"- retrieval_top_k: `{summary.retrieval_top_k}`",
        f"- retrieval_rerank_k: `{summary.retrieval_rerank_k}`",
        f"- retrieval_context_k: `{summary.retrieval_context_k}`",
        "",
        "## Summary",
        "",
        "| Metric | Hits | Total | Rate |",
        "| --- | ---: | ---: | ---: |",
        _metric_row(
            "Retrieved source hit",
            summary.retrieved_source_hits,
            summary.source_required_cases,
        ),
        _metric_row(
            "Reranked source hit",
            summary.reranked_source_hits,
            summary.source_required_cases,
        ),
        _metric_row(
            "Context source hit",
            summary.context_source_hits,
            summary.source_required_cases,
        ),
        _metric_row(
            "Retrieved chunk case hit",
            summary.retrieved_chunk_case_hits,
            summary.chunk_required_cases,
        ),
        _metric_row(
            "Reranked chunk case hit",
            summary.reranked_chunk_case_hits,
            summary.chunk_required_cases,
        ),
        _metric_row(
            "Context chunk case hit",
            summary.context_chunk_case_hits,
            summary.chunk_required_cases,
        ),
        _metric_row(
            "Retrieved chunk group hit",
            summary.retrieved_chunk_group_hits,
            summary.chunk_required_groups,
        ),
        _metric_row(
            "Reranked chunk group hit",
            summary.reranked_chunk_group_hits,
            summary.chunk_required_groups,
        ),
        _metric_row(
            "Context chunk group hit",
            summary.context_chunk_group_hits,
            summary.chunk_required_groups,
        ),
        "",
        "## Tag Breakdown",
        "",
        "| Tag | Source cases | Context source hits | Source rate | Chunk cases | Context chunk hits | Chunk rate |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    lines.extend(_format_tag_rows(results))
    lines.extend(
        [
            "",
            "## Failed Context Source Hits",
            "",
            "| ID | Missing sources | Context sources | Tags | Question |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    lines.extend(_format_failed_rows(results))
    lines.extend(
        [
            "",
            "## Failed Context Chunk Hits",
            "",
            "| ID | Missing chunk groups | Context chunks | Tags | Question |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    lines.extend(_format_failed_chunk_rows(results))
    return "\n".join(lines) + "\n"


def _metric_row(label: str, hits: int, total: int) -> str:
    return f"| {label} | {hits} | {total} | {_rate(hits, total)} |"


def _format_tag_rows(results: list[RetrievalEvalResult]) -> list[str]:
    source_tag_cases: dict[str, list[RetrievalEvalResult]] = defaultdict(list)
    chunk_tag_cases: dict[str, list[RetrievalEvalResult]] = defaultdict(list)
    for result in results:
        for tag in result.tags:
            if result.passed_context_source_hit is not None:
                source_tag_cases[tag].append(result)
            if result.passed_context_chunk_hit is not None:
                chunk_tag_cases[tag].append(result)

    all_tags = sorted(set(source_tag_cases) | set(chunk_tag_cases))
    if not all_tags:
        return ["| No tagged metric cases. | 0 | 0 | n/a | 0 | 0 | n/a |"]

    rows: list[str] = []
    for tag in all_tags:
        source_cases = source_tag_cases.get(tag, [])
        source_hits = sum(
            1 for result in source_cases if result.passed_context_source_hit
        )
        chunk_cases = chunk_tag_cases.get(tag, [])
        chunk_hits = sum(
            1 for result in chunk_cases if result.passed_context_chunk_hit
        )
        rows.append(
            f"| `{tag}` | {len(source_cases)} | {source_hits} | "
            f"{_rate(source_hits, len(source_cases))} | {len(chunk_cases)} | "
            f"{chunk_hits} | {_rate(chunk_hits, len(chunk_cases))} |"
        )
    return rows


def _format_failed_rows(results: list[RetrievalEvalResult]) -> list[str]:
    failed_results = [
        result
        for result in results
        if result.passed_context_source_hit is False
    ]
    if not failed_results:
        return ["| No failed context source hits. |  |  |  |  |"]

    return [
        (
            f"| `{result.id}` | {_md_list(result.missing_sources_in_context)} | "
            f"{_md_list(result.context_sources)} | {_md_list(result.tags)} | "
            f"{_escape_table_text(result.question)} |"
        )
        for result in failed_results
    ]


def _format_failed_chunk_rows(results: list[RetrievalEvalResult]) -> list[str]:
    failed_results = [
        result
        for result in results
        if result.passed_context_chunk_hit is False
    ]
    if not failed_results:
        return ["| No failed context chunk hits. |  |  |  |  |"]

    return [
        (
            f"| `{result.id}` | {_md_chunk_groups(result.missing_chunk_groups_in_context)} | "
            f"{_md_list(result.context_chunk_ids)} | {_md_list(result.tags)} | "
            f"{_escape_table_text(result.question)} |"
        )
        for result in failed_results
    ]


def _source_hits(
    *,
    required_sources: list[str],
    found_sources: list[str],
) -> tuple[list[str], list[str]]:
    hits: list[str] = []
    missing: list[str] = []
    for required_source in required_sources:
        if _source_is_present(required_source, found_sources):
            hits.append(required_source)
        else:
            missing.append(required_source)
    return hits, missing


def _chunk_group_hits(
    *,
    required_chunk_groups: list[ChunkGroup],
    found_chunk_ids: list[str],
) -> tuple[list[ChunkGroup], list[ChunkGroup]]:
    found_ids = set(found_chunk_ids)
    hits: list[ChunkGroup] = []
    missing: list[ChunkGroup] = []
    for required_group in required_chunk_groups:
        matched_chunks = [
            chunk_id
            for chunk_id in required_group
            if chunk_id in found_ids
        ]
        if matched_chunks:
            hits.append(matched_chunks)
        else:
            missing.append(required_group)
    return hits, missing


def _source_is_present(required_source: str, found_sources: list[str]) -> bool:
    normalized_required = required_source.replace("\\", "/").lower()
    required_name = Path(normalized_required).name
    for found_source in found_sources:
        normalized_found = found_source.replace("\\", "/").lower()
        if normalized_found.endswith(normalized_required):
            return True
        if Path(normalized_found).name == required_name:
            return True
    return False


def _unique_sources_from_chunks(
    chunks: list[RetrievedChunk] | list[RerankedChunk],
) -> list[str]:
    sources: list[str] = []
    for chunk in chunks:
        source_path = chunk.source_path
        if source_path and source_path not in sources:
            sources.append(source_path)
    return sources


def _unique_sources_from_context(assembled_context: AssembledContext) -> list[str]:
    sources: list[str] = []
    for block in assembled_context.evidence_blocks:
        if block.source_path and block.source_path not in sources:
            sources.append(block.source_path)
    return sources


def _chunk_ids(chunks: list[RetrievedChunk] | list[RerankedChunk]) -> list[str]:
    return [
        chunk.chunk_id
        for chunk in chunks
        if chunk.chunk_id is not None
    ]


def _read_chunk_groups(row: dict[str, Any]) -> list[ChunkGroup]:
    raw_groups = row.get("required_chunk_groups", [])
    groups: list[ChunkGroup] = []
    for raw_group in raw_groups:
        if isinstance(raw_group, list):
            group = [str(chunk_id) for chunk_id in raw_group if chunk_id]
            if group:
                groups.append(group)
    return groups


def _rate(hits: int, total: int) -> str:
    if total == 0:
        return "n/a"
    return f"{hits / total:.1%}"


def _md_list(values: list[str]) -> str:
    if not values:
        return ""
    return ", ".join(f"`{_escape_table_text(value)}`" for value in values)


def _md_chunk_groups(groups: list[ChunkGroup]) -> str:
    if not groups:
        return ""
    return "<br>".join(
        " OR ".join(f"`{_escape_table_text(chunk_id)}`" for chunk_id in group)
        for group in groups
    )


def _escape_table_text(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")
