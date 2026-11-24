"""Guardrails — the five discipline rules (DESIGN.md §3.4). THE differentiator.

Pure: no DB, no clock — state is derived by state.py and passed in.
Check order is product design and fixed:
  kill switch -> cooldown -> trade cap -> position size -> open positions.
Reason strings match core/constants.py exactly for the defaults; the numbers
inside are generated from the user's own config.
"""

from dataclasses import dataclass

from ...core.constants import BLOCKED_COOLDOWN, BLOCKED_DAILY_LOSS


@dataclass
class Decision:
    allowed: bool
    rule: str | None
    reason: str | None


def evaluate(order: dict, gstate: dict | None, rules) -> Decision:
    """order: {"user_id", "symbol", "side", "quantity", "price", "opens_new_position"}
    gstate: from state.derive() — includes "now" (the clock, passed in for purity).
    rules: the caller's RulesConfig row."""
    if not gstate or not rules:
        return Decision(allowed=True, rule=None, reason=None)

    # ① Kill switch — realized losses today at/over the limit lock everything.
    if gstate["realized_today"] <= -rules.daily_loss_limit:
        return Decision(allowed=False, rule="daily_loss_limit", reason=BLOCKED_DAILY_LOSS)

    # ② Tilt cooldown — last 3 sells all losses, still inside the window.
    cooldown_until = gstate.get("cooldown_until")
    if cooldown_until and gstate["now"] < cooldown_until:
        seconds_left = int((cooldown_until - gstate["now"]).total_seconds()) + 1
        mm, ss = divmod(seconds_left, 60)
        return Decision(
            allowed=False,
            rule="cooldown",
            reason=BLOCKED_COOLDOWN.format(mmss=f"{mm}:{ss:02d}"),
        )

    # ③ Overtrade cap — filled trades today; blocked attempts never count.
    if gstate["trades_used"] >= rules.max_trades_per_day:
        return Decision(
            allowed=False,
            rule="trade_limit",
            reason=f"Blocked: daily trade limit reached "
                   f"({gstate['trades_used']}/{rules.max_trades_per_day}).",
        )

    # ④ Position size cap — buys only, strictly over the cap.
    if order["side"] == "buy":
        cost = round(order["quantity"] * order["price"], 2)
        if cost > rules.max_position_pct * gstate["equity"]:
            pct = int(rules.max_position_pct * 100)
            return Decision(
                allowed=False,
                rule="position_size",
                reason=f"Blocked: order exceeds position size cap ({pct}% of equity).",
            )

        # ⑤ Max open positions — only a buy that opens a NEW position.
        if order.get("opens_new_position") and gstate["open_positions"] >= rules.max_open_positions:
            return Decision(
                allowed=False,
                rule="open_positions",
                reason=f"Blocked: max open positions reached ({rules.max_open_positions}).",
            )

    return Decision(allowed=True, rule=None, reason=None)
