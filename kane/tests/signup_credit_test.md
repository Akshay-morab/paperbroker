---
mode: testing
tags: [smoke]
url: http://localhost:5173
max_steps: 35
---

# Signup credits the account (FR1 / AC-1.1)

## Open the app and make sure we are logged out
Open http://localhost:5173.
If the page shows "Cash:" with a logged-in dashboard, click the "Log out" button and wait for the login form.

## Sign up with a fresh email
On the login form, click the sign-up toggle ("Need an account? Sign up").
Create an account using the email {{smart.random_email}} and the password DemoPass123.
Verify the dashboard shows "Cash: $100,000.00" and the text "Signed in as" containing the same email.
