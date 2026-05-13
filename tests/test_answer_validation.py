"""Unit tests for answer-output validation and weak-evidence abstention."""

from app.agents.answer import (
    WEAK_EVIDENCE_MIN_RERANK_SCORE,
    AnswerModelOutput,
    parse_answer_model_json,
    _validate_model_output,
    _weak_evidence_reason,
)
from app.retrieval.step03_assemble_context import AssembledContext, EvidenceBlock
from app.streaming.chat import _extract_partial_json_string_field


def test_valid_answer_output_passes_validation() -> None:
    output = AnswerModelOutput(
        answer="Yes, this is supported. [1]",
        citations=["[1]"],
        confidence="high",
        abstained=False,
    )

    warnings = _validate_model_output(output, evidence_blocks=[_evidence_block("[1]")])

    assert warnings == []


def test_non_abstained_answer_requires_citation() -> None:
    output = AnswerModelOutput(
        answer="Yes, this is supported.",
        citations=[],
        confidence="high",
        abstained=False,
    )

    warnings = _validate_model_output(output, evidence_blocks=[_evidence_block("[1]")])

    assert "Non-abstained answers must include at least one citation." in warnings


def test_invalid_citation_id_is_rejected() -> None:
    output = AnswerModelOutput(
        answer="Yes, this is supported. [2]",
        citations=["[2]"],
        confidence="high",
        abstained=False,
    )

    warnings = _validate_model_output(output, evidence_blocks=[_evidence_block("[1]")])

    assert any("not in the assembled context" in warning for warning in warnings)


def test_weak_evidence_reason_triggers_below_threshold() -> None:
    context = AssembledContext(
        evidence_blocks=[
            _evidence_block("[1]", rerank_score=WEAK_EVIDENCE_MIN_RERANK_SCORE / 2)
        ],
        context_text="weak context",
    )

    reason = _weak_evidence_reason(context)

    assert reason is not None
    assert "minimum relevance threshold" in reason


def test_parse_answer_model_json_accepts_fenced_json() -> None:
    output = parse_answer_model_json(
        '```json\n{"answer":"Yes. [1]","citations":["[1]"],'
        '"confidence":"high","abstained":false}\n```'
    )

    assert output.answer == "Yes. [1]"
    assert output.citations == ["[1]"]


def test_partial_answer_extractor_reads_streamed_answer_field() -> None:
    buffer = '{"answer":"Line one\\nLine two [1]","citations":['

    partial = _extract_partial_json_string_field(buffer, "answer")

    assert partial == "Line one\nLine two [1]"


def _evidence_block(
    citation_id: str,
    *,
    rerank_score: float | None = 1.0,
) -> EvidenceBlock:
    return EvidenceBlock(
        citation_id=citation_id,
        chunk_id="chunk-1",
        source_path="data/raw/source.txt",
        doc_type="txt",
        title="Source",
        section_path=None,
        page_label=None,
        sheet_label=None,
        row_number=None,
        cosine_distance=0.1,
        approximate_cosine_similarity=0.9,
        rerank_score=rerank_score,
        text="Evidence text.",
    )
