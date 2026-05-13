"""Unit tests for claim eligibility and evidence completeness tools."""

from __future__ import annotations

from datetime import time
from decimal import Decimal

from app.tools.eligibility import evaluate_claim_eligibility
from app.tools.evidence import check_evidence_completeness
from app.tools.models import (
    ClaimLine,
    EligibilityPolicyFacts,
    EvidencePolicyFacts,
    Money,
    TripContext,
)


def test_evidence_checker_flags_missing_receipt_above_threshold() -> None:
    result = check_evidence_completeness(
        expense_category="meal",
        amount=Money.from_value("30", "EUR"),
        provided_fields={"business_purpose"},
        policy_facts=EvidencePolicyFacts(
            expense_category="meal",
            required_fields=frozenset({"business_purpose"}),
            receipt_required_above=Money.from_value("10", "EUR"),
            missing_receipt_approval_above=Money.from_value("25", "EUR"),
            manual_review_if_missing=frozenset({"receipt"}),
        ),
    )

    assert result.status == "manual_review"
    assert result.manual_review_required is True
    assert "receipt" in result.missing_fields
    assert "itemized_receipt" in result.missing_fields
    assert result.clarification_questions


def test_evidence_checker_handles_taxi_route_requirements() -> None:
    result = check_evidence_completeness(
        expense_category="taxi",
        amount=Money.from_value("42", "EUR"),
        provided_fields={"receipt", "business_purpose"},
        policy_facts=EvidencePolicyFacts(
            expense_category="taxi",
            category_required_fields={
                "taxi": frozenset({"receipt", "business_purpose", "route"})
            },
            manual_review_if_missing=frozenset({"route"}),
        ),
    )

    assert result.status == "manual_review"
    assert result.missing_fields == ["route"]
    assert result.manual_review_required is True


def test_eligibility_excludes_alcohol_and_applies_meal_cap() -> None:
    result = evaluate_claim_eligibility(
        claim_lines=[
            ClaimLine("Food", Money.from_value("32", "EUR"), category="food"),
            ClaimLine("Wine", Money.from_value("8", "EUR"), category="alcohol"),
        ],
        trip_context=TripContext(expense_category="meal", city="Vienna"),
        policy_facts=EligibilityPolicyFacts(
            expense_category="meal",
            cap=Money.from_value("35", "EUR"),
        ),
    )

    assert result.status == "partially_eligible"
    assert result.total_claimed.amount == Decimal("40.00")
    assert result.reimbursable_amount.amount == Decimal("32.00")
    assert result.excluded_amount.amount == Decimal("8.00")
    assert result.above_cap_amount.amount == Decimal("0.00")
    assert result.required_approval is False


def test_eligibility_caps_above_cap_hotel_and_requires_approval() -> None:
    result = evaluate_claim_eligibility(
        claim_lines=[
            ClaimLine("Hotel", Money.from_value("260", "CHF"), category="hotel"),
        ],
        trip_context=TripContext(expense_category="hotel", city="Zurich", nights=1),
        policy_facts=EligibilityPolicyFacts(
            expense_category="hotel",
            cap=Money.from_value("240", "CHF"),
            cap_applies_per="night",
        ),
    )

    assert result.status == "manual_review"
    assert result.reimbursable_amount.amount == Decimal("240.00")
    assert result.above_cap_amount.amount == Decimal("20.00")
    assert result.required_approval is True
    assert result.manual_review_reasons


def test_eligibility_can_include_evidence_checker_result() -> None:
    result = evaluate_claim_eligibility(
        claim_lines=[
            ClaimLine("Taxi", Money.from_value("20", "EUR"), category="taxi"),
        ],
        trip_context=TripContext(
            expense_category="taxi",
            city="Prague",
            local_time=time(hour=20, minute=30),
        ),
        policy_facts=EligibilityPolicyFacts(
            expense_category="taxi",
            taxi_allowed_after=time(hour=21),
        ),
        evidence_policy_facts=EvidencePolicyFacts(
            expense_category="taxi",
            category_required_fields={
                "taxi": frozenset({"receipt", "business_purpose", "route"})
            },
            manual_review_if_missing=frozenset({"route"}),
        ),
        provided_evidence_fields={"receipt"},
    )

    assert result.status == "needs_clarification"
    assert result.evidence_result is not None
    assert "business_purpose" in result.evidence_result.missing_fields
    assert any("Taxi time is before" in reason for reason in result.manual_review_reasons)


def test_eligibility_requires_cap_for_meal_decision() -> None:
    result = evaluate_claim_eligibility(
        claim_lines=[
            ClaimLine("Dinner", Money.from_value("40", "EUR"), category="food"),
        ],
        trip_context=TripContext(expense_category="meal", city="Vienna"),
        policy_facts=EligibilityPolicyFacts(expense_category="meal"),
    )

    assert result.status == "needs_clarification"
    assert result.clarification_questions == [
        "What retrieved policy cap or rate applies to this claim?"
    ]


def test_eligibility_calculates_mileage_from_rate_and_distance() -> None:
    result = evaluate_claim_eligibility(
        claim_lines=[
            ClaimLine("Private mileage", Money.from_value("42", "EUR"), category="mileage"),
        ],
        trip_context=TripContext(
            expense_category="mileage",
            country_code="AT",
            distance_km=Decimal("100"),
        ),
        policy_facts=EligibilityPolicyFacts(
            expense_category="mileage",
            cap=Money.from_value("0.42", "EUR"),
            cap_applies_per="km",
        ),
    )

    assert result.status == "eligible"
    assert result.reimbursable_amount.amount == Decimal("42.00")
