---
mode: testing
tags: [guardrail]
url: http://localhost:5173
max_steps: 45
---

# The kill switch trips and locks trading (FR5 / AC-5.1)

NOTE: this flow consumes the tilted persona. Before re-running, reset personas:
`python -m app.seed --personas-only` (backend dir) — or the admin endpoint.

## Log in as the tilted persona
Open http://localhost:5173.
If a dashboard with "Cash:" is visible, click "Log out" and wait for the login form.
Log in with tilted@demo and password demo1234, and verify "Signed in as tilted@demo" appears.

## The trip: sell the remaining TSLA at a loss
Click the TSLA stock card on the watchlist, enter quantity 10, and click the Sell button.
Verify "Order filled" appears.

## Verify the lock
Open http://localhost:5173/discipline and verify the text "Trading locked until tomorrow." is visible.
Then go back to the watchlist, open the AAPL stock card, enter quantity 1, and click the Buy button.
Verify the banner shows "Blocked: daily loss limit reached. Trading locked until tomorrow."
