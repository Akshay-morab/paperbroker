---
mode: testing
tags: [guardrail]
url: http://localhost:5173
max_steps: 45
---

# No single order can take more than 20% of equity (FR5 / AC-5.4)

## Sign up fresh
Open http://localhost:5173.
If shares are visible on a dashboard, click the "Profile" tab in the corner, then "Log out".
Click "Need an account? Sign up", create an account with the email {{smart.random_email}} and password DemoPass123.

## Oversize the order
On the All Shares page, click the AAPL stock card. In the Buy card, enter quantity 200 and click the Buy button.
Verify the banner shows "Blocked: order exceeds position size cap (20% of equity)."
Then open http://localhost:5173/discipline and verify the "Position size cap" card shows 20%.
