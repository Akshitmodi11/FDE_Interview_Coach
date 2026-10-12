# Plan: `GET /progress` endpoint

## Context
Learners need a quick view of how much they've practised. `GET /progress` reads
`data/results.json` and returns how many rounds have been practised and the average
total score. Today `results.json` is `[]` and **nothing writes to it yet**:
`data.save_result()` has no callers, and `/score` is still a Module 3 stub.

## Response shape (recommended)
```json
{ "attempts": 3, "rounds_practised": 2, "average_total": 11.67 }
```
- `attempts`: number of scored answers (records in the file)
- `rounds_practised`: number of distinct round types (`decomposition`, `behavioral`, …)
- `average_total`: mean of each record's `total`, rounded to 2 dp; `null` when there are no results

Returning both counts settles the ambiguity of "how many rounds practised" at almost no cost.

## 1. Files to change
| File | Change |
|---|---|
| `app/models.py` | Add `ProgressResponse(attempts: int, rounds_practised: int, average_total: float \| None)` |
| `app/data.py` | Add `load_results() -> list[dict]`. Read `DATA_DIR / "results.json"`; return `[]` if the file is missing. All disk access stays here, per CLAUDE.md |
| `app/progress.py` (new, small) | Pure function `summarize_progress(results: list[dict]) -> ProgressResponse`. No I/O, so it's trivially unit-testable |
| `app/main.py` | Thin route: `@app.get("/progress")` returns `summarize_progress(data.load_results())` |
| `tests/test_progress.py` (new) | Unit tests for `summarize_progress`; endpoint tests that monkeypatch `app.data.DATA_DIR` to `tmp_path` |

Don't touch `scoring.py`: the seeded `compute_total()` bug and `/score` stub stay as-is (CLAUDE.md guardrail).

## 2. Order
1. `ProgressResponse` model in `models.py`
2. `summarize_progress()` plus its unit tests (empty list, one record, several records across rounds)
3. `load_results()` in `data.py`
4. `/progress` route in `main.py` plus endpoint tests using a temp `results.json`
5. `python -m pytest -q`, `python -m ruff check .`, `python -m mypy app`
6. Manual check at http://127.0.0.1:8000/docs

## 3. What could break / easy to get wrong
- **Divide by zero** on an empty file. The real file is empty right now, so this is the default case, not an edge case.
- **Tests polluting real data.** Tests must write their own `results.json` under `tmp_path`.
- **Patching the wrong name.** `data.py` does `from .config import DATA_DIR`, so tests must patch `app.data.DATA_DIR`, not `app.config.DATA_DIR`.
- **Missing or malformed file:** handle a missing file (return `[]`). A malformed file shouldn't produce a raw stack trace; let it surface as a clear 500, or catch `json.JSONDecodeError` and raise an `HTTPException`.
- **Records missing `total` or `round`**: skip such records instead of crashing with `KeyError`.
- **Wrong totals until Module 3.** Any results saved before `compute_total()` is fixed will be undercounted, so the average will be low. That's not the endpoint's fault, but it's easy to misdiagnose.
- **Type drift:** the average is a float while totals are ints; mypy will flag a mismatch if the model says `int`.

## 4. Riskiest assumption
**That each record in `results.json` will look like `{"round": ..., "question_id": ..., "total": ..., "max": ...}`.**
Nothing writes that file yet, so `/progress` is effectively *defining* the record contract
that `/score` must follow in Module 3. If `/score` later saves a different shape (e.g. nested
`scorecard.total`, or no `round`), `/progress` silently reports wrong numbers. Mitigation: write
down the record shape (docstring on `save_result`), and when `/score` is wired up, add a test that
scores an answer and then checks `/progress` reflects it.

## Verification
- `python -m pytest -q`: existing 3 tests plus new progress tests pass
- With an empty `results.json`: `GET /progress` → `{"attempts": 0, "rounds_practised": 0, "average_total": null}`
- `git status` / file check: real `data/results.json` is still `[]` after the test run
- ruff and mypy are clean
