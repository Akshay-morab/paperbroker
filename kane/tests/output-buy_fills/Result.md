---
test: ../buy_fills_test.md
status: passed
started: 2026-11-24T20:08:45.209Z
duration_s: 183
session_id: e73c2396-3c48-4fb0-88cf-1763bec93586
---

# Buy order fills and hits the books (FR3 / AC-3.1) — Result

## Open the app and sign up fresh ✓ passed (82.8s)
md5: d2790768c049100b757f65bdd8c295dd
Open http://localhost:5173.
If shares are visible on a dashboard, click the "Profile" tab in the corner, then "Log out", and wait for the login form.
Click "Need an account? Sign up", create an account with the email {{smart.random_email}} and password DemoPass123.

## Buy 10 AAPL from All Shares ✓ passed (95.9s)
md5: a2916d9e1535461e9ef03dd5aa70d02e
On the All Shares page, click the AAPL stock card.
On the AAPL page, enter quantity 10 in the Buy card and click the Buy button.
Then open the Portfolio and verify a row for AAPL shows 10 shares, with Cash lower than $100,000.00.
