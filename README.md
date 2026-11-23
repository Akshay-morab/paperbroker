# PaperBroker *(working title)*

> A paper-trading broker with a **discipline engine** — other brokers let you trade; this one
> decides when you're done for the day.

*(Name note: this repo runs under a working title until the demo video records on Thu Nov 26 —
GitHub renames are free and redirect, so the final brand can land any time this week.)*

## What it is

- **Paper trading:** simulated, deterministic market prices; real bookkeeping underneath — cash,
  holdings, average cost, realized/unrealized P&L on SQLite
- **A discipline engine** between you and your worst impulses:
  - **Daily loss kill switch** — hit the limit, trading locks until tomorrow
  - **Overtrade cap** — 10 trades a day; the 11th is refused, with a reason
  - **Tilt cooldown** — three straight losses buys you a forced break
  - **Position-size cap & max open positions** — no single idea can sink the account

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

On the EC2 box, nginx serves the built frontend and proxies `/api` — see [DESIGN.md §6](./DESIGN.md).

## Demo logins (for judges)

_Seeded personas arrive with the seed script:_

| Persona | Demonstrates |
|---|---|
| `fresh@demo` | clean account, happy-path trading |
| `tilted@demo` | one click from the kill switch firing |
| `cooldown@demo` | mid-cooldown, trading locked with countdown |

All personas use password `demo1234`.
