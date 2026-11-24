---
mode: testing
tags: [smoke]
url: http://localhost:5173
max_steps: 45
---

# Buy order fills and hits the books (FR3 / AC-3.1)

## Open the app and sign up fresh
Open http://localhost:5173.
If shares are visible on a dashboard, click the "Profile" tab in the corner, then "Log out", and wait for the login form.
Click "Need an account? Sign up", create an account with the email {{smart.random_email}} and password DemoPass123.

## Buy 10 AAPL from All Shares
On the All Shares page, click the AAPL stock card.
On the AAPL page, enter quantity 10 in the Buy card and click the Buy button.
Verify the text "Order filled" appears.
Then open the Portfolio and verify a row for AAPL shows 10 shares, with Cash lower than $100,000.00.
