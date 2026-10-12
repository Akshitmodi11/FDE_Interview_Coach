# CLAUDE.md — FDE Interview Prep Assistant

## What we're building
A small FastAPI app that runs mock Forward Deployed Engineer interviews and scores
answers against a 4-category rubric (Clarifying questions, Decomposition, Risk
identification, Communication; 0–5 each, max 20). It's a teaching project built
module by module: favour **clarity over cleverness**, since every line should be
explainable in an interview.

## Stack
- Python 3.11+ (local machine runs 3.14), **FastAPI** + uvicorn, **Pydantic v2**
- Data: plain **JSON files** in `data/`, with no database
- Scoring: offline **mock** scorer by default; **OpenAI** when `OPENAI_API_KEY` is set.
  The model id comes from `app/config.MODEL_ID` (env `OPENAI_MODEL`, default `gpt-4o-mini`)
- Tests: **pytest** + FastAPI `TestClient`
- Quality: **ruff** (line length 100, rules E+F), **mypy** (py3.11, see `pyproject.toml`)

## Project layout
- `app/main.py`: HTTP routes only (`/health`, `/rounds`, `/questions`, `/score`, `/progress`).
  Thin, no logic
- `app/models.py`: Pydantic schemas for every request/response
- `app/scoring.py`: scoring logic (mock, OpenAI, totals, scorecard summary)
- `app/progress.py`: `summarize_progress()` (attempts, distinct rounds, average total). Pure, no I/O
- `app/data.py`: **the only module that touches disk** (questions, rubric, results)
- `app/config.py`: all settings, paths, and env vars in one place
- `data/`: `questions.json` (question bank), `rubric.md`, `results.json` (append-only log)
- `resources/`: interview-technique guides (STAR, decomposition, system design)
- `tests/`: pytest suite. `test_basic.py` covers the read endpoints; `test_scoring.py` covers
  `compute_total()` and every summary band; `test_score_and_progress.py` covers `/score` and
  `/progress` against a temp data folder
- `mcp/server.py`: FastMCP server `interview-guides` serving `resources/` (see below).
  No `__init__.py` on purpose, so it never shadows the real `mcp` package
- `.claude/settings.json` + `.claude/hooks/`: project hooks (see below)
- `.mcp.json`: project-scope MCP registration for `interview-guides`

## Conventions
- Type-hint everything; `from __future__ import annotations` at the top of each module.
- Small functions named for what they do, each with a one-line docstring.
- Routes stay thin: validate with Pydantic, delegate to `data` / `scoring`.
- Disk I/O goes through `app/data.py`; settings go through `app/config.py`.
  Never read env vars or JSON files elsewhere.
- LLM prompts live as named constants in `scoring.py`, never inline strings.
- Each `results.json` record is `{"round", "question_id", "total", "max"}` (documented on
  `data.save_result()`). `/progress` depends on that shape, so change both together.
- Rubric categories come from `RUBRIC_CATEGORIES`. Keep them in sync with `data/rubric.md`.
- Summary labels come from the `SUMMARY_BANDS` lookup table in `scoring.py` (via
  `summary_for()`). Change a band there, never with new if/else branches. "Full marks"
  is the fixed `FULL_MARKS = 20`, not the computed maximum.
- Refactors are behaviour-preserving: pin current behaviour with tests first, then refactor
  with the suite green.
- Errors: raise `HTTPException` with a clear `detail`; never leak a stack trace.
- New behaviour ships with a test. Tests must never hit the network (rely on mock
  mode) and must not write to the real `data/results.json` (use `tmp_path` + monkeypatch).

## Hooks (`.claude/settings.json`)
These run automatically; they are enforcement, not suggestions.
- **PreToolUse `Read` → `.claude/hooks/block_env.py`**: blocks reading any path containing
  `.env` (except `.env.example`), exit 2. Don't try to get around it (e.g. `cat .env` via Bash);
  if a task needs a secret, ask the user.
- **PostToolUse `Edit|Write|MultiEdit` → `.claude/hooks/checks.py`**: runs
  `ruff check app tests` and `mypy app` after every edit. On failure it prints the output
  to stderr and exits 2. Fix the reported code problem; don't edit the hook to silence it.
  A tool that isn't installed is skipped with a note (setup issue, not a code defect).

## MCP server: `interview-guides`
- Registered at project scope in `.mcp.json` (`python mcp/server.py`, stdio). Needs one-time
  approval in a session started from `my-coach/`; check with `/mcp`.
- Tools: `list_guides()` returns guide names (the `.md` files in `resources/`, no extension);
  `get_guide(name)` returns one guide's markdown (`.md` optional). Unknown names raise a
  `ToolError` listing the valid ones; only listed names are accepted, so no path traversal.
- Prefer these tools when you need interview-technique content. A new guide is just a new
  `.md` file in `resources/`, with no code change.

## Guardrails for you, the agent
- **Intentional workshop seeds: don't "fix" them unprompted.** The `score_with_openai()`
  stub is there on purpose for Module 3. Point it out if relevant; change it only when asked.
  (Done so far: `compute_total()` bug fixed, `format_scorecard()` refactored, `/score` wired
  to `score_answer()` + `save_result()` with a 404 for unknown questions, `/progress` added.)
- Work in `my-coach/` only. **Never edit `checkpoints/`**: those are reference snapshots.
- Show a plan before multi-file or structural changes; keep diffs small and focused.
- Small loop: one change → run `pytest -q` → report results honestly (paste failures).
- When debugging, rank hypotheses before editing code.
- Don't add dependencies, a database, or new frameworks without asking.
- Never commit `.env`, API keys, or `results.json` test noise. Don't commit unless asked.
- Two credentials exist: the app uses **OpenAI** (`OPENAI_API_KEY`), and Claude Code uses
  **Anthropic**. Don't conflate them.

## How to run (Windows / PowerShell)
`pip` and installed scripts aren't on PATH here, so use `python -m` (bare `pytest`,
`ruff`, `uvicorn` fail with "command not found"):
```
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload   # UI: http://127.0.0.1:8000/docs  (/ is a 404, that's expected)
python -m pytest -q
python -m ruff check .
python -m mypy app
python mcp/server.py                      # MCP server on stdio (normally Claude Code starts it)
```
Hooks and the MCP server only load when Claude Code is launched from inside `my-coach/`.
