---
test: ../unknown_symbol_test.md
status: passed
started: 2026-11-24T20:46:09.291Z
duration_s: 81
session_id: 3bf67358-a1a6-47f9-9f23-a35febabf7e1
---

# Unknown symbol says so, in the UI (FR2 / AC-2.3) — Result

## Log in ✓ passed (55.7s)
md5: ee5ff557efa26fedae24f1b90a02be92
Open http://localhost:5173.
If shares are visible on a dashboard, click the "Profile" tab in the corner, then "Log out".
Log in with fresh@demo and password demo1234, and verify the All Shares page loads.

## Visit a symbol that does not exist ✓ passed (20.4s)
md5: 152a4b2c54e61efd21943c055bb2a784
Open http://localhost:5173/stocks/NOPE directly.
Verify the page shows the text "unknown symbol".
