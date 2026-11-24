---
test: ../signup_credit_test.md
status: passed
started: 2026-11-24T20:04:54.262Z
duration_s: 102
session_id: fdc04dcd-557a-4553-845e-e6f30f704639
---

# Signup credits the account (FR1 / AC-1.1) — Result

## Open the app and make sure we are logged out ✓ passed (27.2s)
md5: ebf3ba552b87b482d505d41e87ca440f
Open http://localhost:5173.
If shares are visible on a dashboard, click the "Profile" tab in the top right corner, then click "Log out", and wait for the login form.

## Sign up with a fresh email and verify the starting cash ✓ passed (68.2s)
md5: 152b6277d5b7d39fe42f697d12a59cfc
Click "Need an account? Sign up", create an account with the email {{smart.random_email}} and the password DemoPass123.
Then click the "Profile" tab in the corner, open "User Profile Details", and verify it shows the same email and the text "Cash: $100,000.00".
