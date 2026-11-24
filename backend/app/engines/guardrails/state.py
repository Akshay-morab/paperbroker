"""Derive guardrail state from today's orders (DESIGN.md §3.4: derived, never stored).

evaluate() stays pure — every DB and clock access happens HERE, and the result
is a plain dict that gets passed into the rules.
"""

from datetime import datetime, timedelta

from ...models import Holding, Order, RulesConfig
from ..ledger.service import portfolio


def derive(db, user_id: int, rules) -> dict:
    now = datetime.now()
    today = now.date()

    fills = db.query(Order).filter(Order.user_id == user_id, Order.status == "filled").all()
    fills_today = [o for o in fills if o.created_at.date() == today]
    sells_today = [o for o in fills_today if o.side == "sell"]
    realized_today = round(sum((o.realized_pnl or 0.0) for o in sells_today), 2)

    # Loss streak: the most recent 3 filled sells, all losses. A single profitable
    # sell in the window breaks the streak. Cooldown anchors at the LATEST loss.
    recent_sells = (
        db.query(Order)
        .filter(Order.user_id == user_id, Order.side == "sell", Order.status == "filled")
        .order_by(Order.id.desc())
        .limit(3)
        .all()
    )
    streak = len(recent_sells) == 3 and all(
        o.realized_pnl is not None and o.realized_pnl < 0 for o in recent_sells
    )
    cooldown_until = None
    if streak:
        cooldown_minutes = rules.cooldown_minutes if rules else 30
        cooldown_until = recent_sells[0].created_at + timedelta(minutes=cooldown_minutes)

    open_positions = db.query(Holding).filter(Holding.user_id == user_id).count()
    equity = portfolio(db, user_id)["equity"]

    return {
        "now": now,
        "realized_today": realized_today,
        "trades_used": len(fills_today),
        "cooldown_until": cooldown_until,
        "open_positions": open_positions,
        "equity": equity,
    }


def rules_for(db, user_id: int) -> RulesConfig:
    """The user's rules row, or a transient default-backed instance (never None)."""
    return (
        db.query(RulesConfig).filter(RulesConfig.user_id == user_id).first()
        or RulesConfig(user_id=user_id)
    )
