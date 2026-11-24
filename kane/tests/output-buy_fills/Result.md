---
test: ../buy_fills_test.md
status: passed
started: 2026-11-24T18:08:05.614Z
duration_s: 162
session_id: de95f0ad-49d8-4eba-b93b-0bc4d12a493f
---

# Buy order fills and hits the books (FR3 / AC-3.1) — Result

## Open the app and sign up fresh ✓ passed (84.5s)
md5: 86f76e29eb9230ae47826207213a9daf
Open http://localhost:5173.
If the page shows "Cash:" on a dashboard, click "Log out" and wait for the login form.
Click "Need an account? Sign up", create an account with the email {{smart.random_email}} and password DemoPass123, and verify "Cash: $100,000.00" appears.

## Buy 10 AAPL from the watchlist ✓ passed (73s)
md5: 6abc2ef3f72520c973d7548874f64a16
On the watchlist, click the AAPL symbol.
On the AAPL page choose Buy, quantity 10, and place the order.
Verify the text "Order filled" appears.
Then open the Portfolio and verify a row for AAPL shows 10 shares, with Cash lower than $100,000.00.
