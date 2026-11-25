# PaperBroker *(working title)*

> A paper-trading broker with a **discipline engine** — other brokers let you trade; this one
> decides when you're done for the day.

*(Name note: this repo runs under a working title until the demo video records on Thu Nov 26 —
GitHub renames are free and redirect, so the final brand can land any time this week.)*

## What this is, in plain words

**A practice stock market.** You get $100,000 of fake money, 22 fake companies whose prices
move on their own, and you buy and sell shares like a real broker app. Cash, holdings, and
profit/loss are all tracked honestly, like a real bank ledger.

**The discipline engine — the part that makes this different.** "Tilt" is trader slang for
the moment you stop thinking and start *reacting*: you lose money, get angry, and immediately
trade again to win it back — usually losing even more. Every experienced trader knows tilt.
Most trading apps don't care. This one does: five hard rules that **physically stop you** —

1. Lose $10,000 in a day? Trading is locked until tomorrow. No "one more trade."
2. Already made 10 trades today? The 11th is refused. Done for the day.
3. Three losing trades in a row? A forced 30-minute cooldown. Walk away.
4. Want to put 20%+ of everything you own into one stock? Refused.
5. Already holding 5 different stocks? The 6th is refused.

The message isn't a suggestion — the order simply does not go through. Other brokers let you
trade; **this one decides when you're done for the day.**

**And an AI checked it.** [Kane CLI](https://www.testmuai.com/) is an AI tester: flows are
described in plain English ("log in, buy 10 shares, check the cash dropped"), and Kane opens
a real browser, does it like a human, and reports pass or fail with video proof. This app was
built by an AI coding agent and verified flow-by-flow with Kane — including the moment the
kill switch slams the door.

**One breath:** *a practice trading app that protects you from your worst self — the tilt
locker — tested in a real browser by an AI.*

## What it is

- **Paper trading:** simulated, deterministic market prices; real bookkeeping underneath — cash,
  holdings, average cost, realized/unrealized P&L on SQLite
- **A discipline engine** between you and your worst impulses:
  - **Daily loss kill switch** — hit the limit, trading locks until tomorrow
  - **Overtrade cap** — 10 trades a day; the 11th is refused, with a reason
  - **Tilt cooldown** — three straight losses buys you a forced break
  - **Position-size cap & max open positions** — no single idea can sink the account
- **A Discipline page** — every rule's live status: loss budget, trades used,
  cooldown countdown, position caps

## How it's built & verified

Built for the **Kane CLI Online Hackathon** (TestMu AI) with a closed verification loop:

> the AI coding agent makes the changes → **Kane CLI** drives the app in a real browser →
> the pass/fail verdict with evidence feeds back to the agent → repeat until green.

Every trading and guardrail flow has a committed `_test.md` that Kane replays against the deployed
URL. The full low-level design, deployment runbook (EC2 + nginx + SQLite), and the Phase-2 roadmap
(fundamentals panel, ops console, limit orders) live in [DESIGN.md](./DESIGN.md).

## Status

Building — solo hack week, Nov 21–27, 2026. Daily progress in [BUILD_LOG.md](./BUILD_LOG.md).

## Run it

Two terminals, one origin (Vite proxies `/api` to the backend — no CORS):

```bash
# backend (Python 3.10+)
cd backend
python -m venv .venv
.venv\Scripts\pip install -e ".[dev]"        # macOS/Linux: .venv/bin/pip
.venv\Scripts\python -m app.seed             # instruments + demo personas
.venv\Scripts\uvicorn app.main:app --reload  # API on http://127.0.0.1:8000

# frontend (Node 18+)
cd frontend
npm install
npm run dev                                  # http://localhost:5173
```

On the EC2 box, nginx serves the built frontend and proxies `/api` — one command:
`sudo ./scripts/deploy-ec2.sh <repo-url>` (runbook: DESIGN.md §6).

## Demo logins (for judges)

**Live app: http://15.252.181.255/** — log in with any persona below, or sign up your own
account (new accounts start with $100,000).

_Seeded personas arrive with the seed script:_

| Persona | Demonstrates |
|---|---|
| `fresh@demo` | clean account, happy-path trading |
| `tilted@demo` | one click from the kill switch firing |
| `cooldown@demo` | mid-cooldown, trading locked with countdown |

All personas use password `demo1234`.
