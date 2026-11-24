---
mode: testing
tags: [smoke]
url: http://localhost:5173
max_steps: 45
---

# Signup credits the account (FR1 / AC-1.1)

## Open the app and make sure we are logged out
Open http://localhost:5173.
If shares are visible on a dashboard, click the "Profile" tab in the top right corner, then click "Log out", and wait for the login form.

## Sign up with a fresh email and verify the starting cash
Click "Need an account? Sign up", create an account with the email {{smart.random_email}} and the password DemoPass123.
Then click the "Profile" tab in the corner, open "User Profile Details", and verify it shows the same email and the text "Cash: $100,000.00".
