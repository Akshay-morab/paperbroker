"""Ledger reads. The books: cash comes from the last cash_transaction.balance_after —
an audit trail that replays to the current balance (DESIGN.md §3.5).
"""

from sqlalchemy.orm import Session

from ...models import CashTransaction, Holding
from ..prices.engine import price_engine


def cash_balance(db: Session, user_id: int) -> float:
    last = (
        db.query(CashTransaction)
        .filter(CashTransaction.user_id == user_id)
        .order_by(CashTransaction.id.desc())
        .first()
    )
    return last.balance_after if last else 0.0


def portfolio(db: Session, user_id: int) -> dict:
    """Holdings joined with live sim prices -> per-position unrealized P&L,
    cash, and equity = cash + market value of all positions."""
    cash = round(cash_balance(db, user_id), 2)
    positions = []
    equity = cash

    for holding in (
        db.query(Holding)
        .filter(Holding.user_id == user_id)
        .order_by(Holding.symbol)
        .all()
    ):
        quote = price_engine.quote(holding.symbol)
        price = quote["price"] if quote else holding.avg_cost  # engine always has it; belt+braces
        market_value = round(holding.quantity * price, 2)
        positions.append(
            {
                "symbol": holding.symbol,
                "quantity": holding.quantity,
                "avg_cost": holding.avg_cost,
                "price": price,
                "market_value": market_value,
                "unrealized_pnl": round(holding.quantity * (price - holding.avg_cost), 2),
            }
        )
        equity += market_value

    return {"cash": cash, "equity": round(equity, 2), "positions": positions}
