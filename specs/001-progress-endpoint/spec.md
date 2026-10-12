# Spec 001: `GET /progress`

**Status:** Implemented (`app/progress.py`, route in `app/main.py`)

## Why
Learners need a quick answer to "how much have I practised, and how am I doing?" without
reading `results.json` by hand. `/progress` turns the results log into three numbers.

## What it returns
`200 OK` with a `ProgressResponse`:

```json
{ "attempts": 3, "rounds_practised": 2, "average_total": 11.67 }
```

| Field | Meaning |
|---|---|
| `attempts` | Number of valid scored answers |
| `rounds_practised` | Number of distinct round types among them (`decomposition`, `behavioral`, …) |
| `average_total` | Mean of `total` across valid records, rounded to 2 dp; `null` when there are none |

A record is **valid** if it has both `round` and `total`. Other records are skipped.

## What it reads
- `data/results.json` only, via `data.load_results()`. Records have the shape
  `{"round", "question_id", "total", "max"}` (written by `data.save_result()` from `/score`).
- Read-only: it never writes or modifies data.

## Acceptance criteria
1. **Empty case:** if `results.json` is `[]` or missing, the response is
   `{"attempts": 0, "rounds_practised": 0, "average_total": null}` with `200`, not an error and
   not a divide by zero.
2. With records `[{decomposition, 10}, {decomposition, 12}, {behavioral, 13}]`, the response is
   `attempts = 3`, `rounds_practised = 2` and `average_total = 11.67`.
3. Records missing `round` or `total` are skipped. If none are valid, the result is the same as the empty case.
4. After a successful `POST /score`, `/progress` reflects the new attempt. A `404` from
   `/score` (unknown question) adds nothing.
5. Calling `/progress` never changes `results.json`.
6. The logic lives in the pure `summarize_progress()` (no I/O). The route stays a one-line
   delegation, and all disk access goes through `app/data.py`.
7. Tests use a temp data folder (`tmp_path` + monkeypatch) and never touch the real
   `data/results.json`.

## Out of scope
- Per-category averages or "weakest category". Records store only totals, so adding these
  means changing the record shape (a separate spec).
- Trends over time, timestamps, per-question history, streaks.
- Filtering by round, or pagination.
- Multiple users or authentication. There is one learner and one local file.
- Changing how answers are scored.
