"""Tests for POST /score and GET /progress.  Run:  pytest -q

Every endpoint test points app.data at a temp folder, so the real
data/results.json is never touched.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import data
from app.config import DATA_DIR
from app.main import app
from app.progress import summarize_progress

client = TestClient(app)

ANSWER = {"round": "decomposition", "question_id": "dec-01", "answer": "Ask about data.\nScope."}


@pytest.fixture
def temp_data(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Copy the question bank into tmp_path and start with no saved results."""
    shutil.copy(DATA_DIR / "questions.json", tmp_path / "questions.json")
    (tmp_path / "results.json").write_text("[]", encoding="utf-8")
    monkeypatch.setattr(data, "DATA_DIR", tmp_path)
    return tmp_path


def test_summarize_progress_empty() -> None:
    progress = summarize_progress([])
    assert (progress.attempts, progress.rounds_practised, progress.average_total) == (0, 0, None)


def test_summarize_progress_counts_and_averages() -> None:
    results = [
        {"round": "decomposition", "total": 10},
        {"round": "decomposition", "total": 12},
        {"round": "behavioral", "total": 5},
    ]
    progress = summarize_progress(results)
    assert progress.attempts == 3
    assert progress.rounds_practised == 2
    assert progress.average_total == 9.0


def test_summarize_progress_rounds_average_to_two_places() -> None:
    results = [
        {"round": "decomposition", "total": 10},
        {"round": "decomposition", "total": 12},
        {"round": "behavioral", "total": 13},
    ]
    progress = summarize_progress(results)
    assert (progress.attempts, progress.rounds_practised, progress.average_total) == (3, 2, 11.67)


def test_summarize_progress_skips_incomplete_records() -> None:
    progress = summarize_progress([{"round": "behavioral"}, {"round": "behavioral", "total": 8}])
    assert progress.attempts == 1
    assert progress.average_total == 8.0


def test_score_saves_result(temp_data: Path) -> None:
    resp = client.post("/score", json=ANSWER)
    assert resp.status_code == 200
    saved = json.loads((temp_data / "results.json").read_text(encoding="utf-8"))
    assert len(saved) == 1
    assert saved[0]["round"] == "decomposition"
    assert saved[0]["question_id"] == "dec-01"
    assert saved[0]["total"] == resp.json()["total"]


def test_score_unknown_question_returns_404_and_saves_nothing(temp_data: Path) -> None:
    resp = client.post("/score", json={**ANSWER, "question_id": "nope"})
    assert resp.status_code == 404
    assert json.loads((temp_data / "results.json").read_text(encoding="utf-8")) == []


def test_progress_reflects_scored_answers(temp_data: Path) -> None:
    client.post("/score", json=ANSWER)
    client.post("/score", json={**ANSWER, "round": "behavioral", "question_id": "beh-01"})
    progress = client.get("/progress").json()
    assert progress["attempts"] == 2
    assert progress["rounds_practised"] == 2


def test_progress_with_no_results_file(temp_data: Path) -> None:
    (temp_data / "results.json").unlink()
    assert client.get("/progress").json() == {
        "attempts": 0,
        "rounds_practised": 0,
        "average_total": None,
    }
