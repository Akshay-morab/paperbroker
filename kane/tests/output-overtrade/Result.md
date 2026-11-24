---
test: ../overtrade_test.md
status: passed
started: 2026-11-24T20:36:38.879Z
duration_s: 195
session_id: 96c4e694-46a6-4b59-be83-a4318601b24c
---

# Ten trades a day, the eleventh is refused (FR5 / AC-5.3) — Result

## Log in as the tilted persona ✓ passed (62.8s)
md5: 0b63b1a309c4f4907a5ceccdf9cf45af
Open http://localhost:5173.
If shares are visible on a dashboard, click the "Profile" tab in the corner, then "Log out".
Log in with tilted@demo and password demo1234, and verify the All Shares page loads.

## The 10th trade goes through ✓ passed (55.8s)
md5: 9241314c8383a4da967d4dcd0b8dc056
On the All Shares page, click the AAPL stock card. In the Buy card, enter quantity 1 and click the Buy button.

## The 11th is blocked ✓ passed (71.4s)
md5: c019a5fe599c84f1a20f002bb8926355
Enter quantity 1 again in the Buy card and click the Buy button.
Open http://localhost:5173/orders and verify the newest entry shows status "blocked" and a reason containing "daily trade limit reached (10/10)".
