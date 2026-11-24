---
mode: testing
tags: [trade]
url: http://localhost:5173
max_steps: 45
---

# Oversized buy is rejected (FR3 / AC-3.2)

## Open the app and sign up fresh
Open http://localhost:5173.
If shares are visible on a dashboard, click the "Profile" tab in the corner, then "Log out", and wait for the login form.
Click "Need an account? Sign up", create an account with the email {{smart.random_email}} and password DemoPass123.

## Try to buy far more than the cash balance
On the All Shares page, click the AAPL stock card.
Enter quantity 100000 in the Buy card and click the Buy button.
Open the Orders page and verify the newest entry shows status "rejected" and the reason "Rejected: insufficient cash".
Then click the "Profile" tab in the corner, open "User Profile Details", and verify the text "Cash: $100,000.00".
