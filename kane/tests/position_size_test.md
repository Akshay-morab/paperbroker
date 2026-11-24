---
mode: testing
tags: [guardrail]
url: http://localhost:5173
max_steps: 40
---

# No single order can take more than 20% of equity (FR5 / AC-5.4)

## Sign up fresh
Open http://localhost:5173.
If a dashboard with "Cash:" is visible, click "Log out".
Click "Need an account? Sign up", create an account with the email {{smart.random_email}} and password DemoPass123, and verify "Cash: $100,000.00" appears.

## Oversize the order
Click the AAPL stock card, enter quantity 200, and click the Buy button.
Verify the banner shows "Blocked: order exceeds position size cap (20% of equity)."
Then open http://localhost:5173/discipline and verify the "Position size cap" card shows 20%.
