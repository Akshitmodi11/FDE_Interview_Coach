---
description: Summarise practice progress from data/results.json (rounds, average, weakest category, next focus)
allowed-tools: Read
---

Read `data/results.json` and write a short progress report. Read the file only; don't
modify it or any other file.

## If there are no results
If the file is missing, empty, or contains `[]`, reply with just:

> No results yet. Score an answer with `POST /score` (or say "let's practise") and run
> `/report` again.

Then stop.

## Otherwise, report these four things

Each record has the shape `{"round", "question_id", "total", "max"}`.

1. **Rounds practised:** the number of records (attempts), plus how many distinct round
   types they cover, e.g. "7 attempts across 3 round types (decomposition, behavioral,
   system-design)".
2. **Average total:** the mean of `total`, rounded to one decimal, shown out of 20
   (e.g. "13.4 / 20"). Also give the average per round type so the weakest round is visible.
3. **Weakest rubric category:** one of the four categories in `data/rubric.md`
   (Clarifying questions, Decomposition, Risk identification, Communication).
   - If records include per-category scores (e.g. a `categories` list), average each
     category and name the lowest.
   - If they don't (the current record shape stores only totals), say plainly that
     the log doesn't record per-category scores. Then name the category most likely to
     be weak, given the lowest-scoring round type, and label it as an inference, not a measurement.
4. **Focus next:** one concrete, actionable suggestion aimed at the weakest category or
   round, e.g. which round to practise next and one habit to apply in the answer.

Keep the report under about 12 lines, using a heading and a short bullet list. Don't
invent numbers: every figure must come from the file.
