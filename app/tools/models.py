"""Shared typed models for deterministic claim evaluation tools.

The models in this module represent structured claim facts and policy facts
after retrieval has already found the relevant evidence. They do not perform
policy lookup and they intentionally keep source citations as caller-provided
metadata.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time
from decimal import Decimal, ROUND_HALF_UP
from typing import Literal


ExpenseCategory = Literal[
    "meal",
    "hotel",
    "taxi",
    "mileage",
    "entertainment",
    "other",
]
LineCategory = Literal[
    "food",
    "alcohol",
    "hotel",
    "taxi",
    "mileage",
    "tip",
    "tax",
    "personal",
    "other",
]
DecisionStatus = Literal[
    "eligible",
    "partially_eligible",
    "not_eligible",
    "manual_review",
    "needs_clarification",
]


@dataclass(frozen=True)
class Money:
    """Currency amount with deterministic decimal arithmetic."""

    amount: Decimal
    currency: str

    @classmethod
    def from_value(cls, amount: Decimal | int | float | str, currency: str) -> "Money":
        """Build money from common primitive input types."""
        return cls(amount=_to_decimal(amount), currency=normalize_currency(currency))

    def rounded(self) -> "Money":
        """Return the amount rounded to normal currency precision."""
        return Money(amount=round_money(self.amount), currency=self.currency)


@dataclass(frozen=True)
class ClaimLine:
    """One structured line item from a claim or receipt."""

    description: str
    amount: Money
    category: LineCategory = "other"
    source_id: str | None = None


@dataclass(frozen=True)
class TripContext:
    """Structured trip and claim context used by deterministic tools."""

    expense_category: ExpenseCategory
    city: str | None = None
    country_code: str | None = None
    expense_date: date | None = None
    trip_end_date: date | None = None
    submitted_date: date | None = None
    local_time: time | None = None
    nights: int | None = None
    distance_km: Decimal | None = None
    business_purpose_provided: bool = False
    approval_provided: bool = False
    preapproved: bool = False
    is_client_entertainment: bool = False
    public_transport_exception_reason: str | None = None


@dataclass(frozen=True)
class PolicyReference:
    """Citation-like reference for retrieved policy facts used by tools."""

    citation_id: str | None = None
    source_path: str | None = None
    section_path: str | None = None
    sheet: str | None = None
    row_number: int | None = None
    note: str | None = None


@dataclass(frozen=True)
class EligibilityPolicyFacts:
    """Retrieved policy facts required by the claim eligibility evaluator."""

    expense_category: ExpenseCategory
    cap: Money | None = None
    cap_applies_per: Literal["claim", "night", "km"] = "claim"
    taxi_allowed_after: time | None = None
    non_reimbursable_line_categories: frozenset[LineCategory] = frozenset(
        {"personal"}
    )
    alcohol_requires_preapproved_entertainment: bool = True
    approval_required_if_above_cap: bool = True
    references: tuple[PolicyReference, ...] = ()


@dataclass(frozen=True)
class EvidencePolicyFacts:
    """Retrieved policy facts required by the evidence completeness checker."""

    expense_category: ExpenseCategory
    required_fields: frozenset[str] = frozenset()
    category_required_fields: dict[ExpenseCategory, frozenset[str]] = field(
        default_factory=dict
    )
    receipt_required_above: Money | None = None
    missing_receipt_approval_above: Money | None = None
    manual_review_if_missing: frozenset[str] = frozenset()
    references: tuple[PolicyReference, ...] = ()


def normalize_currency(currency: str) -> str:
    """Normalize and validate a three-letter currency code."""
    normalized = currency.strip().upper()
    if len(normalized) != 3 or not normalized.isalpha():
        raise ValueError(f"Currency must be a three-letter ISO code, got {currency!r}.")
    return normalized


def round_money(value: Decimal) -> Decimal:
    """Round money to two decimals using normal half-up behavior."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def zero_money(currency: str) -> Money:
    """Return a zero amount for the given currency."""
    return Money(amount=Decimal("0.00"), currency=normalize_currency(currency))


def _to_decimal(value: Decimal | int | float | str) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))
