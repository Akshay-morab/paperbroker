---
mode: testing
tags: [trade]
url: http://localhost:5173
max_steps: 25
---

# Unknown symbol says so, in the UI (FR2 / AC-2.3)

## Log in
Open http://localhost:5173.
If a dashboard with "Cash:" is visible, click "Log out".
Log in with fresh@demo and password demo1234, and verify "Signed in as fresh@demo" appears.

## Visit a symbol that does not exist
Open http://localhost:5173/stocks/NOPE directly.
Verify the page shows the text "unknown symbol".
