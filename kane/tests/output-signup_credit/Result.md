---
test: ../signup_credit_test.md
status: passed
started: 2026-11-24T17:58:55.796Z
duration_s: 116
session_id: 29a06e68-aaca-4bd0-97bd-2dc609d36db3
---

# Signup credits the account (FR1 / AC-1.1) — Result

## Open the app and make sure we are logged out ✓ passed (33s)
md5: 50f5e5fdeac67088dc73eeee28467dd4
Open http://localhost:5173.
If the page shows "Cash:" with a logged-in dashboard, click the "Log out" button and wait for the login form.

## Sign up with a fresh email ✓ passed (68.8s)
md5: bb4ea7457160c4848342d0e53f02f8d0
On the login form, click the sign-up toggle ("Need an account? Sign up").
Create an account using the email {{smart.random_email}} and the password DemoPass123.
Verify the dashboard shows "Cash: $100,000.00" and the text "Signed in as" containing the same email.
