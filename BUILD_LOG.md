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
- **Wed Nov 25 (late) — fundamentals + UX round 3 (user feedback):** the Phase-2 tables
  landed for real — profiles (sector/eps/shares/52w) + 5-year financials per instrument,
  5 years of daily price history for chart ranges (1D/1M/2M/4M/6M/1Y/5Y), similar-stocks
  suggestions by sector, fully separated Buy/Sell cards with live totals, a 2s purchase
  popup, boxed nav pills with hover tooltips, portfolio position cards, orders as an
  activity feed. The midnight gotcha bit FOR REAL just after 00:00 — the tilted persona's
  panic dumps landed on yesterday, caught instantly by the guardrail tests; fixed with
  same-day clamping in the seed (33/33 green). Scope frozen after this pass: suite, EC2,
  video.
- **Wed Nov 25 (final round) — watchlist + profile + tabs:** per-user watchlist
  (watchlist_items + star toggles on every card; All Shares vs Watchlist pages), corner
  Profile menu (User Profile Details modal w/ email/cash/net worth; Log out), "Signed in as"
  + cash removed from the header per feedback, clickable brand → About popup, research
  sections collapsed into tabs (Fundamentals/Financials/News/Similar — page is short again),
  simulated headlines: 18 templates, company name swapped, 4 random per visit. 34/34 pytest
  (new watchlist round-trip test). All 8 Kane flows reworded for the Profile-menu logout and
  profile-modal assertions. THIS IS THE FEATURE FREEZE.
- **Wed Nov 25 (truly final) — orders modal, sticky trade bar, hover chip, avatars, P&L,
  dividends:** order rows open a details modal (shares/price/total/status/success line);
  a floating Buy/Sell bar follows the stock page and smooth-scrolls to the trade cards;
  the chart shows an OHLC hover chip; deterministic letter avatars per symbol; the hero
  gains P&L % vs starting cash and Dividends earned — backed by a real dividends loop
  (1 real minute = 1 simulated quarter, credited as genuine ledger rows; yields seeded
  per stock). ensure_schema() added because SQLite create_all never ALTERs — the
  dividend_yield column landed on the shipped DB without data loss. 36/36 pytest.
- **Thu Nov 26 (~4 AM) — popups, not banners (user feedback):** blocked/rejected reasons
  now pop up as a closable modal (~2s) with a warning icon, matching the success popup;
  the inline alerts are retired. Because 2-second popups are racy for Kane's ~6s
  click-to-assert latency, all flow assertions were moved to the persistent records —
  order-history entries, the discipline lock, portfolio rows. Ephemeral UI for humans,
  permanent records for verification. Also fixed a live crash: dividend_yield missing
  from the profile API payload → blank stock page (caught by the human, fixed in minutes).
- **Thu Nov 26 (~5 AM) — the blank-page arc (the loop's best story):** user reported
  blank stock pages again. Source read clean, build clean — dead end. Ran the same
  Kane probe twice around the fix: RED ("empty root after waits and refresh",
  confirmed_product_bug, evidence pack) → restarted the two-day-old Vite dev server
  (its log showed a poisoned module graph from ~50 hot-reloads + mid-session dep
  re-optimizations) → same probe GREEN (AAPL page, price + Buy card verified).
  Lesson, now a rule: long-lived watchers lie — uvicorn's StatReload already proved it,
  Vite confirmed it. Restart the servers before debugging the code. Ctrl+Shift+R for
  the human after a wedged dev session.
- **Thu Nov 26 (~6 AM) — SUITE GREEN: 8/8, and flow 5 earned its bug-wall plaque:**
  the full re-run on the frozen UI finished with every flow passed and every recording
  committed (kane/tests/output-*). Flow 5 (kill switch) went RED first — and the failure
  was a real product bug no human had noticed: ~20h of live uptime had let the seeded
  random walk drift TSLA +265% above base, so the tilted persona's "panic" sells would
  fill at GAINS, never cross the −$10k line, and the kill-switch demo was silently
  disarmed. Kane caught it because it asserted on the persistent record, not the
  visual. Fix: mean reversion in the price walk (0.002 pull toward base_price each
  tick; 36/36 pytest re-run), backend restarted so prices re-anchor at base. Same
  flow then went GREEN: tilted sells 10 TSLA → "Trading locked until tomorrow." on
  /discipline → attempted buy blocked with the byte-exact reason. Flows 6–8 followed:
  overtrade (10 filled, the 11th blocked "daily trade limit reached (10/10)"),
  position size (200-share AAPL buy blocked at the 20% cap), unknown symbol
  (/stocks/NOPE shows "unknown symbol"). Second plaque lesson: stateful sims drift —
  an agent that never sleeps catches the bugs an evening of eyeballing can't.
  Remaining: EC2 deploy, 3-min video, submission form.
