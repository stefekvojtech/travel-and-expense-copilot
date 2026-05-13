"""Unit tests for deterministic currency conversion behavior."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from app.core.config import ROOT_DIR, Settings
from app.tools.currency import CurrencyConversionError, convert_currency


def test_convert_currency_uses_company_exchange_rates_first() -> None:
    settings = _settings_with_raw_dir(ROOT_DIR / "data" / "raw")

    result = convert_currency(settings, "100", "CZK", "EUR", rate_date="2026-02-15")

    assert result.converted_amount == Decimal("3.96")
    assert result.exchange_rate == Decimal("0.0396")
    assert result.source == "company_exchange_rates"
    assert result.rate_date == "2026-02"


def test_convert_currency_cross_converts_company_rates() -> None:
    settings = _settings_with_raw_dir(ROOT_DIR / "data" / "raw")

    result = convert_currency(settings, "100", "USD", "CZK", rate_date="2026-02")

    assert result.converted_amount == Decimal("2348.48")
    assert result.source == "company_exchange_rates"


def test_convert_currency_falls_back_to_frankfurter() -> None:
    settings = _settings_with_raw_dir(Path("does-not-exist"))

    result = convert_currency(
        settings,
        "10",
        "JPY",
        "EUR",
        rate_date="2026-02-15",
        http_get_json=lambda _url, _timeout: {
            "amount": 1,
            "base": "JPY",
            "quote": "EUR",
            "date": "2026-02-13",
            "rate": 0.0062,
        },
    )

    assert result.converted_amount == Decimal("0.06")
    assert result.exchange_rate == Decimal("0.0062")
    assert result.source == "frankfurter"
    assert result.rate_date == "2026-02-13"
    assert result.warnings


def test_convert_currency_can_disable_external_fallback() -> None:
    settings = _settings_with_raw_dir(Path("does-not-exist"))

    try:
        convert_currency(
            settings,
            "10",
            "JPY",
            "EUR",
            allow_external_fallback=False,
        )
    except CurrencyConversionError as exc:
        assert "external fallback is disabled" in str(exc)
    else:
        raise AssertionError("Expected CurrencyConversionError")


def test_convert_currency_identity_does_not_need_rates() -> None:
    settings = _settings_with_raw_dir(Path("does-not-exist"))

    result = convert_currency(settings, "12.345", "eur", "EUR")

    assert result.converted_amount == Decimal("12.35")
    assert result.exchange_rate == Decimal("1")
    assert result.source == "identity"


def _settings_with_raw_dir(raw_dir: Path) -> Settings:
    return Settings(
        embedding_model="text-embedding-3-large",
        vision_model="gpt-4.1-mini",
        answer_model="gpt-5.5",
        raw_data_dir=raw_dir,
        processed_data_dir=raw_dir / "processed",
        vector_store_dir=raw_dir / "processed" / "04_vectorstore",
        vector_collection_name="test",
        retrieval_top_k=12,
        retrieval_rerank_k=5,
        retrieval_context_k=4,
        retrieval_context_max_tokens=3000,
        retrieval_context_max_block_tokens=800,
        rerank_model="ms-marco-MiniLM-L-12-v2",
        chunk_size=600,
        chunk_overlap=120,
        max_chunk_tokens=1200,
    )
