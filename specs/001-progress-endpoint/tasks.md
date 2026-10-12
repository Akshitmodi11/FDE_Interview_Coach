# Tasks: Spec 001 `GET /progress`

Each task is one small diff with its own test, and can be reviewed and merged on its own.
Do them in order: each task builds on the one before.
**Done when** (every task): `python -m pytest -q`, `python -m ruff check .` and
`python -m mypy app` all pass.

Status reflects the code as of this writing. "Gap" means a spec criterion with no test yet.

---

### T1. `ProgressResponse` model ✅ Done
- **Change:** `app/models.py`: `ProgressResponse(attempts: int, rounds_practised: int,
  average_total: float | None)`.
- **Test:** covered by T2's tests (they construct and assert on it).
- **Review:** field names and types match the spec's response table.

### T2. `summarize_progress()`: empty and happy path ✅ Done
- **Change:** new `app/progress.py`, a pure function with no I/O.
- **Tests:** `test_summarize_progress_empty`, `test_summarize_progress_counts_and_averages`.
- **Covers:** acceptance criterion (AC) 1 (pure logic), part of AC2, and AC6 (no I/O).

### T3. `summarize_progress()`: skip incomplete records ✅ Done
- **Change:** filter to records that have both `round` and `total`.
- **Test:** `test_summarize_progress_skips_incomplete_records`.
- **Covers:** AC3.

### T4. `data.load_results()` ✅ Done
- **Change:** `app/data.py`: read `results.json`, return `[]` if it's missing.
- **Test:** `test_progress_with_no_results_file`, through the endpoint (see T5).
- **Review:** this is the only disk access, and it never writes.

### T5. `GET /progress` route ✅ Done
- **Change:** `app/main.py`, a one-line delegation:
  `summarize_progress(data.load_results())`.
- **Tests:** `test_progress_with_no_results_file`, `test_progress_reflects_scored_answers`.
- **Covers:** AC1 (missing file), AC4 (successful scores counted), AC6 (thin route), and AC7 (temp folder).

---

### T6. Pin the spec's worked example and rounding ⏳ Gap (AC2)
- **Why:** the existing test averages to `9.0`, so 2-decimal rounding is never exercised.
- **Change (test only):** `summarize_progress` on `[{decomposition, 10}, {decomposition, 12},
  {behavioral, 13}]` returns `(3, 2, 11.67)`.
- **Review:** one test, no production code.

### T7. Only invalid records means the empty result ⏳ Gap (AC3)
- **Change (test only):** `summarize_progress([{"round": "x"}, {"total": 5}])` returns
  `(0, 0, None)`.
- **Review:** guards the `if not valid` branch against invalid records, not only `[]`.

### T8. Endpoint empty case with `[]` ⏳ Gap (AC1)
- **Why:** only the missing-file case is tested through HTTP. `[]` is the real default.
- **Change (test only):** with the `temp_data` fixture, which writes `[]`, `GET /progress` returns `200`
  and `{"attempts": 0, "rounds_practised": 0, "average_total": null}`.

### T9. A 404 from `/score` doesn't change progress ⏳ Gap (AC4)
- **Change (test only):** `POST /score` with an unknown `question_id`, then `GET /progress`
  still reports `attempts == 0`.
- **Review:** complements the existing file-level 404 test, asserted at the API level.

### T10. `/progress` is read-only ⏳ Gap (AC5)
- **Change (test only):** seed `results.json` in `temp_data`, call `GET /progress` twice, and
  assert the file's bytes are unchanged.

---

**Remaining work:** T6–T10 add tests only, one per commit. If any one fails, it has found a
real bug: fix the code in that task's diff and note it in the review.
