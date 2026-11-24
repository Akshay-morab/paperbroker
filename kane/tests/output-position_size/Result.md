---
test: ../position_size_test.md
status: passed
started: 2026-11-24T20:40:30.119Z
duration_s: 296
session_id: cda1338b-2932-4a98-9ad7-3f65408d74cb
---

# No single order can take more than 20% of equity (FR5 / AC-5.4) — Result

## Sign up fresh ✓ passed (73.8s)
md5: 6bd37369ba221956ef65e8cd1fec6236
Open http://localhost:5173.
If shares are visible on a dashboard, click the "Profile" tab in the corner, then "Log out".
Click "Need an account? Sign up", create an account with the email {{smart.random_email}} and password DemoPass123.

## Oversize the order ✓ passed (217.2s)
md5: bf936ace327935c9723436ef3510b98f
On the All Shares page, click the AAPL stock card. In the Buy card, enter quantity 200 and click the Buy button.
Open http://localhost:5173/orders and verify the newest entry shows status "blocked" and a reason containing "position size cap".
Then open http://localhost:5173/discipline and verify the "Position size cap" card shows 20%.
