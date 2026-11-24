---
test: ../insufficient_cash_test.md
status: passed
started: 2026-11-24T18:11:36.448Z
duration_s: 129
session_id: ba7ecfc6-cae8-4729-a127-1352af3acd46
---

# Oversized buy is rejected (FR3 / AC-3.2) — Result

## Open the app and sign up fresh ✓ passed (77.5s)
md5: 86f76e29eb9230ae47826207213a9daf
Open http://localhost:5173.
If the page shows "Cash:" on a dashboard, click "Log out" and wait for the login form.
Click "Need an account? Sign up", create an account with the email {{smart.random_email}} and password DemoPass123, and verify "Cash: $100,000.00" appears.

## Try to buy far more than the cash balance ✓ passed (47.1s)
md5: c1b675435fb50cf68fb7f612a3d642d5
Click the AAPL symbol on the watchlist.
Choose Buy, quantity 100000, and place the order.
Verify the banner shows "Rejected: insufficient cash" and Cash still reads $100,000.00.
