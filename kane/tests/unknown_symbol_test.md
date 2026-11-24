---
mode: testing
tags: [trade]
url: http://localhost:5173
max_steps: 30
---

# Unknown symbol says so, in the UI (FR2 / AC-2.3)

## Log in
Open http://localhost:5173.
If shares are visible on a dashboard, click the "Profile" tab in the corner, then "Log out".
Log in with fresh@demo and password demo1234, and verify the All Shares page loads.

## Visit a symbol that does not exist
Open http://localhost:5173/stocks/NOPE directly.
Verify the page shows the text "unknown symbol".
