---
mode: testing
tags: [smoke]
url: http://localhost:5173
max_steps: 50
---

# Sell round trip closes the position (FR4 / AC-4.2)

## Open the app and sign up fresh
Open http://localhost:5173.
If shares are visible on a dashboard, click the "Profile" tab in the corner, then "Log out", and wait for the login form.
Click "Need an account? Sign up", create an account with the email {{smart.random_email}} and password DemoPass123.

## Buy then sell AAPL
On the All Shares page, click the AAPL stock card. Enter quantity 10 in the Buy card and click the Buy button, and verify "Order filled" appears.
Then enter quantity 10 in the Sell card and click the Sell button, and verify "Order filled" appears again.
Open the Portfolio and verify it shows "No positions yet." with a Net worth near the starting cash.
Open the Orders page and verify two entries show "filled".
