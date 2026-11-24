---
mode: testing
tags: [smoke]
url: http://localhost:5173
max_steps: 40
---

# Buy order fills and hits the books (FR3 / AC-3.1)

## Open the app and sign up fresh
Open http://localhost:5173.
If the page shows "Cash:" on a dashboard, click "Log out" and wait for the login form.
Click "Need an account? Sign up", create an account with the email {{smart.random_email}} and password DemoPass123, and verify "Cash: $100,000.00" appears.

## Buy 10 AAPL from the watchlist
On the watchlist, click the AAPL stock card.
On the AAPL page enter quantity 10 and click the Buy button.
Verify the text "Order filled" appears.
Then open the Portfolio and verify a row for AAPL shows 10 shares, with Cash lower than $100,000.00.
