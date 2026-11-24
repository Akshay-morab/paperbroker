---
test: ../sell_roundtrip_test.md
status: passed
started: 2026-11-24T20:17:02.697Z
duration_s: 465
session_id: a4b1c794-ebfc-4474-8b82-33eea1e4e2f6
---

# Sell round trip closes the position (FR4 / AC-4.2) — Result

## Open the app and sign up fresh ✓ passed (80.7s)
md5: d2790768c049100b757f65bdd8c295dd
Open http://localhost:5173.
If shares are visible on a dashboard, click the "Profile" tab in the corner, then "Log out", and wait for the login form.
Click "Need an account? Sign up", create an account with the email {{smart.random_email}} and password DemoPass123.

## Buy then sell AAPL ✓ passed (379.2s)
md5: 9f68bc65ce19e3b4342db84366fb471c
On the All Shares page, click the AAPL stock card. Enter quantity 10 in the Buy card and click the Buy button.
Then enter quantity 10 in the Sell card and click the Sell button.
Open the Portfolio and verify it shows "No positions yet." with a Net worth near the starting cash.
Open the Orders page and verify the two newest entries show status "filled".
