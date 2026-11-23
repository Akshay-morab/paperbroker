---
mode: testing
tags: [smoke]
url: http://localhost:5173
max_steps: 45
---

# Sell round trip closes the position (FR4 / AC-4.2)

## Open the app and sign up fresh
Open http://localhost:5173.
If the page shows "Cash:" on a dashboard, click "Log out" and wait for the login form.
Click "Need an account? Sign up", create an account with the email {{smart.random_email}} and password DemoPass123, and verify "Cash: $100,000.00" appears.

## Buy then sell AAPL
Click the AAPL symbol on the watchlist, choose Buy, quantity 10, place the order, and verify "Order filled" appears.
Then choose Sell, quantity 10, place the order, and verify "Order filled" appears again.
Open the Portfolio and verify it shows "No positions yet." with Equity near the starting cash.
Open the Orders page and verify two rows show "filled".
