---
test: ../insufficient_cash_test.md
status: passed
started: 2026-11-24T20:12:28.077Z
duration_s: 227
session_id: 2c380ae8-bbc2-41cc-964d-de721435845b
---

# Oversized buy is rejected (FR3 / AC-3.2) — Result

## Open the app and sign up fresh ✓ passed (78.5s)
md5: d2790768c049100b757f65bdd8c295dd
Open http://localhost:5173.
If shares are visible on a dashboard, click the "Profile" tab in the corner, then "Log out", and wait for the login form.
Click "Need an account? Sign up", create an account with the email {{smart.random_email}} and password DemoPass123.

## Try to buy far more than the cash balance ✓ passed (143.8s)
md5: 56a7a824df4a749352670d8339b98543
On the All Shares page, click the AAPL stock card.
Enter quantity 100000 in the Buy card and click the Buy button.
Open the Orders page and verify the newest entry shows status "rejected" and the reason "Rejected: insufficient cash".
Then click the "Profile" tab in the corner, open "User Profile Details", and verify the text "Cash: $100,000.00".
