# PaperBroker — Product Requirements (v1)

> **Working title** — see DESIGN.md for the naming note. This document is the
> requirement source for `kane-cli context ingest` / `design tests` (Lane 4) and
> maps 1:1 to the committed flows in `kane/tests/`.

## 1. Summary

PaperBroker is a browser-based paper-trading broker with a **discipline engine**.
Users get $100,000 of simulated cash, a simulated but deterministic market, and can
place market orders to buy and sell stocks. The differentiator: five configurable
guardrails stand between the user and their worst impulses, and every trading flow
is verified end-to-end by Kane CLI in a real browser.

- **Not in scope (Phase 2+):** limit/stop orders, real market data, KYC, payment
  rails, margin, options, the ops console UI (see DESIGN.md §8.1 for the cut list).

## 2. Users

| Persona | Purpose | Password |
|---|---|---|
| any new signup | experience the happy path from scratch | chosen at signup |
| `fresh@demo` | clean account: happy-path trading | `demo1234` |
| `tilted@demo` | down $9,700 today over 9 trades — one bad sell from the kill switch | `demo1234` |
| `cooldown@demo` | 3 straight losses, ~25 min of cooldown remaining | `demo1234` |

## 3. Functional requirements & acceptance criteria

### FR1 — Accounts & sessions
- AC-1.1: Signing up with a new email credits the account with **$100,000.00** and lands on a
  dashboard that shows `Cash: $100,000.00` and `Signed in as <email>`.
- AC-1.2: Duplicate signup shows the message `email already registered`.
- AC-1.3: Wrong credentials show `invalid email or password`; logout clears the session.

### FR2 — Market data (simulated, deterministic)
- AC-2.1: The watchlist lists at least 8 symbols with name and a positive price.
- AC-2.2: A symbol's detail returns a quote plus 120 candles for the chart.
- AC-2.3: An unknown symbol returns the message `unknown symbol`.

### FR3 — Market orders
- AC-3.1: A valid **buy** fills instantly at the current simulated price; the UI confirms with
  the text `Order filled`.
- AC-3.2: A buy costing more than the cash balance is rejected with `Rejected: insufficient cash`.
- AC-3.3: Selling more shares than held is rejected with `Rejected: insufficient shares`.
- AC-3.4: Non-positive/non-integer quantity is rejected with `Rejected: invalid quantity`.
- AC-3.5: Books balance after every fill: cash debit/credit, holdings update, order recorded —
  one atomic transaction.

### FR4 — Portfolio & ledger
- AC-4.1: The portfolio shows cash, per-position holdings with live unrealized P&L, and equity.
- AC-4.2: A full sell closes the position (row disappears) and raises cash.

### FR5 — Guardrails (the differentiator)
Checked in order before any fill; block reasons render verbatim in a banner:

- AC-5.1 **Daily loss kill switch**: once realized losses today reach the configured limit
  ($10,000 default), all trading is locked and further attempts show
  `Blocked: daily loss limit reached. Trading locked until tomorrow.`
- AC-5.2 **Tilt cooldown**: after 3 consecutive losing sells, trading locks for 30 minutes;
  attempts during cooldown show the cooldown message with a visible countdown.
- AC-5.3 **Overtrade cap**: the 11th trade of the day is blocked with
  `Blocked: daily trade limit reached (10/10).` (blocked attempts do not count).
- AC-5.4 **Position size cap**: a buy larger than 20% of equity is blocked with
  `Blocked: order exceeds position size cap (20% of equity).`
- AC-5.5 **Max open positions**: opening a 6th position is blocked with
  `Blocked: max open positions reached (5).`

### FR6 — Order history
- AC-6.1: Every attempt (filled, blocked, rejected) appears in history with symbol, side,
  quantity, price, status, and the exact reason string.

## 4. Verification mapping

| ACs | Kane flow (`kane/tests/`) |
|---|---|
| AC-1.1 | `signup_credit_test.md` (smoke) |
| AC-3.1, AC-4.2 | `buy_fills_test.md`, `sell_roundtrip_test.md` (smoke) |
| AC-3.2 | `insufficient_cash_test.md` |
| AC-5.1 | `kill_switch_test.md` (tilted persona: sell trips the switch, then lockout) |
| AC-5.3 | `overtrade_test.md` |
| AC-5.4 | `position_size_test.md` |
| AC-2.3 | `unknown_symbol_test.md` |
| AC-5.2 | cooldown flow — Phase 2 (rule + persona ship; pytest covers the pure logic) |
