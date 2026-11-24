---
test: ../kill_switch_test.md
status: passed
started: 2026-11-24T20:31:12.303Z
duration_s: 273
session_id: de92764b-e831-4d0a-971f-1872a7529305
---

# The kill switch trips and locks trading (FR5 / AC-5.1) — Result

## Log in as the tilted persona ✓ passed (21.38s)
md5: bd71d336851ba79a8c177667594e714f
Open http://localhost:5173.
If shares are visible on a dashboard, click the "Profile" tab in the corner, then "Log out", and wait for the login form.
Log in with tilted@demo and password demo1234, and verify the All Shares page loads.

## The trip: sell the remaining TSLA at a loss ✓ passed (112.97s)
md5: 195fbdfe0c79ed89116c704e57b245e0
On the All Shares page, click the TSLA stock card. In the Sell card, enter quantity 10 and click the Sell button.

## Verify the lock ✓ passed (133s)
md5: a392d6b6fa138b070b56e68f4fcdf7b4
Open http://localhost:5173/discipline and verify the text "Trading locked until tomorrow." is visible.
Then go back to All Shares, open the AAPL stock card, and in the Buy card enter quantity 1 and click the Buy button.
Open http://localhost:5173/orders and verify the newest entry shows status "blocked" and a reason containing "daily loss limit reached".
