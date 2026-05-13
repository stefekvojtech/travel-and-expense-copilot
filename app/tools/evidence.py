"""Check claim evidence completeness from retrieved policy facts.

The evidence checker is deterministic and strict. It does not retrieve policy,
infer missing facts from prose, or ask the user questions directly. When data is
missing, it returns structured missing fields and clarification questions for an
agent or UI layer to present.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from app.tools.models import (
    DecisionStatus,
    EvidencePolicyFacts,
    ExpenseCategory,
    Money,
    PolicyReference,
)


TOOL_USAGE_PROMPT = """Use check_evidence_completeness after retrieval has supplied
evidence requirements for the expense category.

The tool should run before returning a final claim decision when the user's claim
depends on receipt, route, attendee, approval, business-purpose, or other
supporting evidence. It can also run after evaluate_claim_eligibility so the
agent can combine amount eligibility with evidence completeness.

Do not use this tool to look up policy. Pass retrieved policy facts into it. If
required fields are missing, the agent or UI should ask the returned
clarification questions instead of guessing.
"""


@dataclass(frozen=True)
class EvidenceCompletenessResult:
    """Structured result from evidence completeness checking."""

    status: DecisionStatus
    expense_category: ExpenseCategory
    missing_fields: list[str]
    insufficient_reasons: list[str]
    manual_review_required: bool
    manual_review_reasons: list[str]
    clarification_questions: list[str]
    references: tuple[PolicyReference, ...]


def check_evidence_completeness(
    *,
    expense_category: ExpenseCategory,
    amount: Money,
    provided_fields: Iterable[str],
    policy_facts: EvidencePolicyFacts,
) -> EvidenceCompletenessResult:
    """Evaluate whether the claim has the evidence required by policy facts."""
    provided = {field.strip().lower() for field in provided_fields if field.strip()}
    required = _required_fields_for_category(expense_category, policy_facts)
    insufficient_reasons: list[str] = []
    manual_review_reasons: list[str] = []

    if _is_above_threshold(amount, policy_facts.receipt_required_above):
        required.add("receipt")
        required.add("itemized_receipt")
        insufficient_reasons.append(
            "Policy facts require receipt evidence above the configured threshold."
        )

    missing_fields = sorted(field for field in required if field not in provided)

    manual_review_required = False
    manual_review_fields = {
        field.lower()
        for field in policy_facts.manual_review_if_missing
    }
    for field in missing_fields:
        if field in manual_review_fields:
            manual_review_required = True
            manual_review_reasons.append(f"Missing `{field}` requires manual review.")

    if (
        "receipt" in missing_fields
        and _is_above_threshold(amount, policy_facts.missing_receipt_approval_above)
    ):
        manual_review_required = True
        manual_review_reasons.append(
            "Missing receipt above the policy threshold requires approval or review."
        )

    status: DecisionStatus
    if missing_fields:
        status = "manual_review" if manual_review_required else "needs_clarification"
    else:
        status = "eligible"

    return EvidenceCompletenessResult(
        status=status,
        expense_category=expense_category,
        missing_fields=missing_fields,
        insufficient_reasons=insufficient_reasons,
        manual_review_required=manual_review_required,
        manual_review_reasons=manual_review_reasons,
        clarification_questions=[
            _question_for_field(field)
            for field in missing_fields
        ],
        references=policy_facts.references,
    )


def _required_fields_for_category(
    expense_category: ExpenseCategory,
    policy_facts: EvidencePolicyFacts,
) -> set[str]:
    required = {field.lower() for field in policy_facts.required_fields}
    category_required = policy_facts.category_required_fields.get(
        expense_category,
        frozenset(),
    )
    required.update(field.lower() for field in category_required)
    return required


def _is_above_threshold(amount: Money, threshold: Money | None) -> bool:
    if threshold is None:
        return False
    if amount.currency != threshold.currency:
        return False
    return amount.amount > threshold.amount


def _question_for_field(field: str) -> str:
    labels = {
        "approval": "Was this expense pre-approved, and can you provide that approval?",
        "attendee_list": "Do you have the attendee list for this expense?",
        "business_purpose": "What business purpose should be attached to this claim?",
        "destination": "What destination or drop-off location is shown for this trip?",
        "hotel_folio": "Do you have a hotel folio showing stay details and payment?",
        "itemized_receipt": "Do you have an itemized receipt for this expense?",
        "origin": "What origin or pickup location is shown for this trip?",
        "receipt": "Do you have a receipt for this expense?",
        "route": "Do you have route, pickup, or drop-off evidence for this trip?",
    }
    return labels.get(field, f"Can you provide `{field}` for this claim?")
