"""Tests for downloading the raw demo source corpus through the website API."""

from __future__ import annotations

from io import BytesIO
from zipfile import ZipFile

from fastapi.testclient import TestClient

from app.main import app


def test_raw_data_download_returns_zip_without_agent_instructions() -> None:
    """The raw source ZIP should include demo files but omit local AGENTS.md files."""
    client = TestClient(app)

    response = client.get("/api/downloads/raw-data.zip")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
    assert (
        response.headers["content-disposition"]
        == 'attachment; filename="atlas-raw-policy-corpus.zip"'
    )

    with ZipFile(BytesIO(response.content)) as archive:
        names = set(archive.namelist())

    assert names == {
        "airport_transfer_eligibility_decision_tree.png",
        "corporate_travel_card_rules.png",
        "expense_policy.html",
        "extended_expense_scenarios.txt",
        "per_diem_caps.xlsx",
        "travel_policy.pdf",
    }
    assert "AGENTS.md" not in names
