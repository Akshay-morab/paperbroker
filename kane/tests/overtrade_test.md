---
mode: testing
tags: [guardrail]
url: http://localhost:5173
max_steps: 45
---

# Ten trades a day, the eleventh is refused (FR5 / AC-5.3)

NOTE: uses the tilted persona (9/10 trades already used). Reset personas before re-running.

## Log in as the tilted persona
Open http://localhost:5173.
If shares are visible on a dashboard, click the "Profile" tab in the corner, then "Log out".
Log in with tilted@demo and password demo1234, and verify the All Shares page loads.

## The 10th trade goes through
On the All Shares page, click the AAPL stock card. In the Buy card, enter quantity 1 and click the Buy button, and verify "Order filled" appears.

## The 11th is blocked
Enter quantity 1 again in the Buy card and click the Buy button, and verify the banner shows
"Blocked: daily trade limit reached (10/10)."
Open http://localhost:5173/orders and verify an entry shows status "blocked".
