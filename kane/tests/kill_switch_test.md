---
mode: testing
tags: [guardrail]
url: http://localhost:5173
max_steps: 50
---

# The kill switch trips and locks trading (FR5 / AC-5.1)

NOTE: this flow consumes the tilted persona. Before re-running, reset personas:
`python -m app.seed --personas-only` (backend dir) — or the admin endpoint.

## Log in as the tilted persona
Open http://localhost:5173.
If shares are visible on a dashboard, click the "Profile" tab in the corner, then "Log out", and wait for the login form.
Log in with tilted@demo and password demo1234, and verify the All Shares page loads.

## The trip: sell the remaining TSLA at a loss
On the All Shares page, click the TSLA stock card. In the Sell card, enter quantity 10 and click the Sell button.

## Verify the lock
Open http://localhost:5173/discipline and verify the text "Trading locked until tomorrow." is visible.
Then go back to All Shares, open the AAPL stock card, and in the Buy card enter quantity 1 and click the Buy button.
Open http://localhost:5173/orders and verify the newest entry shows status "blocked" and a reason containing "daily loss limit reached".
