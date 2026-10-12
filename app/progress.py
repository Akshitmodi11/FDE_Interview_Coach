"""Summarise saved results into practice progress (no disk access here)."""
from __future__ import annotations

from .models import ProgressResponse


def summarize_progress(results: list[dict]) -> ProgressResponse:
    """Count attempts and distinct rounds, and average the totals."""
    valid = [r for r in results if "round" in r and "total" in r]
    if not valid:
        return ProgressResponse(attempts=0, rounds_practised=0, average_total=None)
    average = sum(r["total"] for r in valid) / len(valid)
    return ProgressResponse(
        attempts=len(valid),
        rounds_practised=len({r["round"] for r in valid}),
        average_total=round(average, 2),
    )
