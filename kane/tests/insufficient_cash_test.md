---
mode: testing
tags: [trade]
url: http://localhost:5173
max_steps: 40
---

# Oversized buy is rejected (FR3 / AC-3.2)

## Open the app and sign up fresh
Open http://localhost:5173.
If the page shows "Cash:" on a dashboard, click "Log out" and wait for the login form.
Click "Need an account? Sign up", create an account with the email {{smart.random_email}} and password DemoPass123, and verify "Cash: $100,000.00" appears.

## Try to buy far more than the cash balance
Click the AAPL stock card on the watchlist.
Enter quantity 100000 and click the Buy button.
Verify the banner shows "Rejected: insufficient cash" and Cash still reads $100,000.00.
