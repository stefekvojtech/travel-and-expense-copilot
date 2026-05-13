"""Evaluate claim eligibility from structured claim and retrieved policy facts.

The eligibility evaluator performs deterministic arithmetic and rule application
only after retrieval or another upstream step has supplied policy facts. It can
compose with the evidence completeness checker, but it does not ask follow-up
questions itself and it does not retrieve policy from the corpus.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import time
from decimal import Decimal

from app.tools.evidence import EvidenceCompletenessResult, check_evidence_completeness
from app.tools.models import (
    ClaimLine,
    DecisionStatus,
    EligibilityPolicyFacts,
    EvidencePolicyFacts,
    Money,
    PolicyReference,
    TripContext,
    round_money,
    zero_money,
)


TOOL_USAGE_PROMPT = """Use evaluate_claim_eligibility after retrieval has supplied
the policy facts needed for the claim type.

The tool should receive structured claim lines, trip context, and retrieved
policy facts. It may call check_evidence_completeness when evidence policy facts
and provided evidence fields are available, so an agent can combine amount
eligibility with evidence completeness in one deterministic result.

Do not use this tool to look up policy, parse natural-language receipts, or make
conversation decisions. If required policy facts or claim facts are missing, the
tool returns `needs_clarification` plus questions for the agent or UI to ask.
"""


@dataclass(frozen=True)
class ExcludedLine:
    """Claim line excluded from reimbursement with a deterministic reason."""

    line: ClaimLine
    reason: str


@dataclass(frozen=True)
class ClaimEligibilityResult:
    """Structured result from claim eligibility evaluation."""

    status: DecisionStatus
    total_claimed: Money
    eligible_before_cap: Money
    reimbursable_amount: Money
    excluded_amount: Money
    above_cap_amount: Money
    required_approval: bool
    manual_review_reasons: list[str]
    clarification_questions: list[str]
    excluded_lines: list[ExcludedLine]
    evidence_result: EvidenceCompletenessResult | None
    references: tuple[PolicyReference, ...]


def evaluate_claim_eligibility(
    *,
    claim_lines: list[ClaimLine],
    trip_context: TripContext,
    policy_facts: EligibilityPolicyFacts,
    evidence_policy_facts: EvidencePolicyFacts | None = None,
    provided_evidence_fields: set[str] | None = None,
) -> ClaimEligibilityResult:
    """Evaluate a structured claim against retrieved eligibility policy facts."""
    if not claim_lines:
        raise ValueError("claim_lines must contain at least one line item.")

    currency = _single_currency(claim_lines)
    total_claimed = _sum_lines(claim_lines, currency)
    excluded_lines = _excluded_lines(claim_lines, trip_context, policy_facts)
    excluded_amount = _sum_lines([item.line for item in excluded_lines], currency)
    eligible_before_cap = Money(
        amount=round_money(total_claimed.amount - excluded_amount.amount),
        currency=currency,
    )

    manual_review_reasons: list[str] = []
    clarification_questions: list[str] = []
    required_approval = False

    cap = _effective_cap(policy_facts, trip_context)
    if cap is None and trip_context.expense_category in {"meal", "hotel", "mileage"}:
        clarification_questions.append(
            "What retrieved policy cap or rate applies to this claim?"
        )

    if cap is not None and cap.currency != currency:
        clarification_questions.append(
            "Currency conversion is required before applying the retrieved cap."
        )
        cap = None

    above_cap_amount = zero_money(currency)
    reimbursable_amount = eligible_before_cap
    if cap is not None and eligible_before_cap.amount > cap.amount:
        above_cap_amount = Money(
            amount=round_money(eligible_before_cap.amount - cap.amount),
            currency=currency,
        )
        reimbursable_amount = cap.rounded()
        if policy_facts.approval_required_if_above_cap and not (
            trip_context.approval_provided or trip_context.preapproved
        ):
            required_approval = True
            manual_review_reasons.append(
                "Claim exceeds the retrieved cap and no approval was provided."
            )

    taxi_review = _taxi_manual_review_reason(trip_context, policy_facts)
    if taxi_review is not None:
        manual_review_reasons.append(taxi_review)

    evidence_result = None
    if evidence_policy_facts is not None:
        evidence_result = check_evidence_completeness(
            expense_category=trip_context.expense_category,
            amount=total_claimed,
            provided_fields=provided_evidence_fields or set(),
            policy_facts=evidence_policy_facts,
        )
        if evidence_result.manual_review_required:
            manual_review_reasons.extend(evidence_result.manual_review_reasons)
        clarification_questions.extend(evidence_result.clarification_questions)

    status = _status(
        total_claimed=total_claimed,
        reimbursable_amount=reimbursable_amount,
        excluded_amount=excluded_amount,
        above_cap_amount=above_cap_amount,
        manual_review_reasons=manual_review_reasons,
        clarification_questions=clarification_questions,
    )

    return ClaimEligibilityResult(
        status=status,
        total_claimed=total_claimed.rounded(),
        eligible_before_cap=eligible_before_cap.rounded(),
        reimbursable_amount=reimbursable_amount.rounded(),
        excluded_amount=excluded_amount.rounded(),
        above_cap_amount=above_cap_amount.rounded(),
        required_approval=required_approval,
        manual_review_reasons=_dedupe(manual_review_reasons),
        clarification_questions=_dedupe(clarification_questions),
        excluded_lines=excluded_lines,
        evidence_result=evidence_result,
        references=policy_facts.references,
    )


def _single_currency(claim_lines: list[ClaimLine]) -> str:
    currencies = {line.amount.currency for line in claim_lines}
    if len(currencies) != 1:
        raise ValueError(
            "All claim lines must be in one currency before eligibility evaluation."
        )
    return next(iter(currencies))


def _sum_lines(claim_lines: list[ClaimLine], currency: str) -> Money:
    return Money(
        amount=round_money(sum((line.amount.amount for line in claim_lines), Decimal())),
        currency=currency,
    )


def _excluded_lines(
    claim_lines: list[ClaimLine],
    trip_context: TripContext,
    policy_facts: EligibilityPolicyFacts,
) -> list[ExcludedLine]:
    excluded: list[ExcludedLine] = []
    for line in claim_lines:
        if line.category in policy_facts.non_reimbursable_line_categories:
            excluded.append(
                ExcludedLine(
                    line=line,
                    reason=f"`{line.category}` is non-reimbursable in policy facts.",
                )
            )
            continue

        if (
            line.category == "alcohol"
            and policy_facts.alcohol_requires_preapproved_entertainment
            and not (
                trip_context.is_client_entertainment
                and (trip_context.preapproved or trip_context.approval_provided)
            )
        ):
            excluded.append(
                ExcludedLine(
                    line=line,
                    reason=(
                        "Alcohol is excluded unless the claim is pre-approved "
                        "client entertainment."
                    ),
                )
            )
    return excluded


def _effective_cap(
    policy_facts: EligibilityPolicyFacts,
    trip_context: TripContext,
) -> Money | None:
    if policy_facts.cap is None:
        return None
    if policy_facts.cap_applies_per == "night":
        if trip_context.nights is None:
            return None
        return Money(
            amount=round_money(policy_facts.cap.amount * trip_context.nights),
            currency=policy_facts.cap.currency,
        )
    if policy_facts.cap_applies_per == "km":
        if trip_context.distance_km is None:
            return None
        return Money(
            amount=round_money(policy_facts.cap.amount * trip_context.distance_km),
            currency=policy_facts.cap.currency,
        )
    return policy_facts.cap


def _taxi_manual_review_reason(
    trip_context: TripContext,
    policy_facts: EligibilityPolicyFacts,
) -> str | None:
    if trip_context.expense_category != "taxi":
        return None
    if policy_facts.taxi_allowed_after is None or trip_context.local_time is None:
        return None
    if _is_before(trip_context.local_time, policy_facts.taxi_allowed_after):
        if not trip_context.public_transport_exception_reason:
            return (
                "Taxi time is before the retrieved after-hours threshold and no "
                "public-transport exception reason was provided."
            )
    return None


def _is_before(left: time, right: time) -> bool:
    return (left.hour, left.minute, left.second) < (right.hour, right.minute, right.second)


def _status(
    *,
    total_claimed: Money,
    reimbursable_amount: Money,
    excluded_amount: Money,
    above_cap_amount: Money,
    manual_review_reasons: list[str],
    clarification_questions: list[str],
) -> DecisionStatus:
    if clarification_questions:
        return "needs_clarification"
    if manual_review_reasons:
        return "manual_review"
    if reimbursable_amount.amount <= 0 and total_claimed.amount > 0:
        return "not_eligible"
    if excluded_amount.amount > 0 or above_cap_amount.amount > 0:
        return "partially_eligible"
    return "eligible"


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            deduped.append(value)
    return deduped
