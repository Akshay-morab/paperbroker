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
    cash, equity = cash + market value of all positions, overall P&L vs the
    starting credit, and dividends earned."""
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

    starting = (
        db.query(CashTransaction)
        .filter(CashTransaction.user_id == user_id, CashTransaction.kind == "signup_credit")
        .first()
    )
    starting_cash = starting.amount if starting else 0.0
    pnl = round(equity - starting_cash, 2)
    pnl_pct = round((pnl / starting_cash) * 100, 2) if starting_cash else 0.0

    dividends = round(
        sum(
            t.amount
            for t in db.query(CashTransaction)
            .filter(CashTransaction.user_id == user_id, CashTransaction.kind == "dividend")
            .all()
        ),
        2,
    )

    return {
        "cash": cash,
        "equity": round(equity, 2),
        "positions": positions,
        "starting_cash": starting_cash,
        "pnl": pnl,
        "pnl_pct": pnl_pct,
        "dividends_earned": dividends,
    }
