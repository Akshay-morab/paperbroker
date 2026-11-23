"""Ledger reads. The books: cash comes from the last cash_transaction.balance_after —
an audit trail that replays to the current balance (DESIGN.md §3.5).
Portfolio/P&L endpoints arrive with the order engine (Tue).
"""

from sqlalchemy.orm import Session

from ...models import CashTransaction


def cash_balance(db: Session, user_id: int) -> float:
    last = (
        db.query(CashTransaction)
        .filter(CashTransaction.user_id == user_id)
        .order_by(CashTransaction.id.desc())
        .first()
    )
    return last.balance_after if last else 0.0
