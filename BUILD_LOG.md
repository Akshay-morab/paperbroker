# BUILD_LOG

The daily ritual (DESIGN.md §8.3): one entry per day — what worked, what bit, what's next.

## Mon Nov 23 — name day

- **What worked:** design doc re-baselined for the solo week; repo initialized under working title
  *PaperBroker* (final name locks before the video — renames are free).
- **What bit:** the name hunt. 11 candidates vetted; the "premium finance" vocabulary turned out to
  be a graveyard — Gold Seal Trading on regulator fraud lists, Auric on a cancelled ASIC licence,
  TradeMax/Breakwater/Keel/Redline are real firms. Lesson: in fintech, vet names like dependencies.
- **What's next:** scaffold backend + frontend, Kane flow #1 (signup credit) green tonight.
- **Scaffold landed (same day):** FastAPI backend (auth, deterministic price engine, quotes,
  personas seed with the tilted/cooldown constructions), Vite React shell (login/signup +
  watchlist dashboard), PRD with acceptance criteria, Kane flow #1 committed. Python 3.12.10
  installed via winget (machine had none); backend deps in a venv; frontend build green.
  Books-balance bug caught in review: persona holdings now constructed in post-sell state
  (a pending-insert bypassed the later query.update — cash/holdings would have drifted).
- **Env landmine:** Windows Smart App Control (enforcing) blocked the newest SQLAlchemy wheel's
  compiled extension; the reputable 2.0.36 build passes. Pinned in pyproject. EC2/Linux is immune.
- **Orders vertical pulled forward (same evening):** user hit "can't buy" — that was Tuesday's
  scope, so the board moved up a day: order engine (guardrail gate stubbed, contract final),
  portfolio w/ live P&L, history, ticket + 3 pages. 15/15 pytest — fills, rejects, round trip,
  books invariants. Kane flows #2-4 committed. Wednesday now starts at the real rules.
- **Reload gotcha:** uvicorn's StatReload (Windows) announced a reload but never restarted —
  the old process kept serving, so new routes 404'd after edits. Symptom to remember: if a
  change doesn't show up, restart the server before debugging the code.
