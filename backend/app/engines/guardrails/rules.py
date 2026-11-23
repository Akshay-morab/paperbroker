"""Guardrails engine — the discipline gate (DESIGN.md §3.4).

Contract is FINAL from day one: place_order calls evaluate() before any fill,
and a blocked decision wins over everything. The real five rules land Wed
(the pure functions + state derivation); until then the gate passes through.
"""

from dataclasses import dataclass


@dataclass
class Decision:
    allowed: bool
    rule: str | None
    reason: str | None


def evaluate(order: dict, gstate: dict | None, rules) -> Decision:
    """rules: the caller's RulesConfig row (or None = defaults).
    order: {"user_id", "symbol", "side", "quantity", ...}
    gstate: derived guardrail state (None until Wed's state.py lands)."""
    # TODO(Wed Nov 25): kill switch -> cooldown -> trade cap -> size cap -> open positions.
    # Check order and exact reason strings are fixed in core/constants.py (DESIGN.md §3.4).
    return Decision(allowed=True, rule=None, reason=None)
