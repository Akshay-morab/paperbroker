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
- **Tue Nov 24 — guardrails complete (pulled forward from Wed):** the five real rules live in
  the gate, discipline status endpoint + Discipline page, admin persona reset. 32/32 pytest.
  Two design discoveries worth the log:
  1. The old tilted persona (9 straight losses) would ALREADY be in cooldown — the kill-switch
     demo could never fire. Reseeded as 6 panic dumps + 3 small winners (same net −$9,700,
     same cash) so the trailing winners break the streak. Richer story, too.
  2. Validation now runs BEFORE the guardrail gate (DESIGN §3.3 flipped): otherwise a fresh
     account can never see "insufficient cash" — any oversize order trips the position-size
     cap first, since cash starts at 100% of equity.
  Bug wall additions: `{mm:ss}` is format-spec syntax, not a placeholder (KeyError at render);
  persona re-seed deleted orders before the cash rows referencing them (FK violation) — delete
  order fixed. Kane flows #5-8 written; deploy runbook scripted (scripts/deploy-ec2.sh).
- **Tue Nov 24 — UI restyle (Mantine v7):** the hand-rolled CSS was too plain; swapped to
  Mantine's AppShell (persistent header: nav + signed-in identity + cash + logout), striped
  tables, card-based order ticket with a segmented Buy/Sell control, status badges on orders,
  grid of discipline cards. Every Kane-asserted string preserved byte-exact; backend untouched
  (32/32 still stands). TS clean; 101 kB gzip.
- **Wed Nov 25 — UI overhaul round 2 (user feedback):** watchlist is now a grid of large
  clickable stock cards (whole card = the link), real candlestick charts (lightweight-charts),
  direct Buy/Sell buttons replacing the toggle, a 4-second "Order filled" toast with fill
  details, a net-worth hero on Portfolio, a split branding login page, and 22 instruments
  (up from 8). Flow texts updated to match the new interactions — old-UI recordings are
  invalidated by design; the suite re-authors and that IS the loop story for the video.
