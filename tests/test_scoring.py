"""Tests for the scoring logic.  Run:  pytest -q"""
from __future__ import annotations

import pytest

from app.models import CategoryScore
from app.scoring import compute_total, format_scorecard


def test_compute_total_counts_every_category() -> None:
    categories = [
        CategoryScore(name="Clarifying questions", score=5, feedback=""),
        CategoryScore(name="Decomposition", score=3, feedback=""),
        CategoryScore(name="Risk identification", score=2, feedback=""),
        CategoryScore(name="Communication", score=4, feedback=""),
    ]
    assert compute_total(categories) == 14


def make_categories(total: int) -> list[CategoryScore]:
    """Spread `total` across the four rubric categories (each 0..5)."""
    return [
        CategoryScore(name=f"cat-{i}", score=min(5, max(0, total - 5 * i)), feedback="")
        for i in range(4)
    ]


@pytest.mark.parametrize(
    ("total", "summary"),
    [
        (0, "Needs significant work"),
        (4, "Needs significant work"),
        (5, "Needs work"),
        (9, "Needs work"),
        (10, "Solid, with gaps"),
        (15, "Solid, with gaps"),
        (16, "Strong answer"),
        (19, "Strong answer"),
        (20, "Strong answer - full marks"),
    ],
)
def test_format_scorecard_summary_bands(total: int, summary: str) -> None:
    card = format_scorecard(make_categories(total))
    assert card.total == total
    assert card.max == 20
    assert card.summary == summary
