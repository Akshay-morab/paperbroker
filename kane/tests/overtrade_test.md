---
mode: testing
tags: [guardrail]
url: http://localhost:5173
max_steps: 40
---

# Ten trades a day, the eleventh is refused (FR5 / AC-5.3)

NOTE: uses the tilted persona (9/10 trades already used). Reset personas before re-running.

## Log in as the tilted persona
Open http://localhost:5173.
If a dashboard with "Cash:" is visible, click "Log out".
Log in with tilted@demo and password demo1234.

## The 10th trade goes through
Click the AAPL stock card on the watchlist, enter quantity 1, click the Buy button, and verify "Order filled" appears.

## The 11th is blocked
Enter quantity 1 again and click the Buy button, and verify the banner shows
"Blocked: daily trade limit reached (10/10)."
Open http://localhost:5173/orders and verify an entry shows status "blocked".
