"""Single source of truth for every user-visible decision string.

The backend returns these verbatim, the frontend renders them as-is,
pytest asserts equality, and Kane asserts substrings (DESIGN.md §3.4).
Do not reword from anywhere else.
"""

# --- guardrail blocks -------------------------------------------------------
BLOCKED_DAILY_LOSS = "Blocked: daily loss limit reached. Trading locked until tomorrow."
BLOCKED_COOLDOWN = "Blocked: cooldown active after 3 consecutive losses. Try again in {mmss}."
BLOCKED_TRADE_LIMIT = "Blocked: daily trade limit reached (10/10)."
BLOCKED_POSITION_SIZE = "Blocked: order exceeds position size cap (20% of equity)."
BLOCKED_OPEN_POSITIONS = "Blocked: max open positions reached (5)."

# --- order validation rejects -------------------------------------------------
REJECTED_INSUFFICIENT_CASH = "Rejected: insufficient cash"
REJECTED_INSUFFICIENT_SHARES = "Rejected: insufficient shares"
REJECTED_INVALID_QUANTITY = "Rejected: invalid quantity"

# --- misc ---------------------------------------------------------------------
UNKNOWN_SYMBOL = "unknown symbol"
EMAIL_ALREADY_REGISTERED = "email already registered"
INVALID_CREDENTIALS = "invalid email or password"

# --- guardrail defaults (mirrored in rules_config) -----------------------------
DAILY_LOSS_LIMIT = 10_000.0
MAX_TRADES_PER_DAY = 10
COOLDOWN_MINUTES = 30
LOSS_STREAK_TRIGGER = 3
MAX_POSITION_PCT = 0.20
MAX_OPEN_POSITIONS = 5
