"""Order engine — the heart of the app (DESIGN.md §3.3).

place_order: instrument check -> guardrail gate (block wins) -> validation ->
fill at the current simulated price -> atomic ledger update, ONE commit.

Books invariant (§3.5): every filled order moves cash, holdings and its own row
in a single transaction; rejected/blocked attempts are still recorded (AC-6.1)
but never touch the books.
"""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ...core.constants import (
    REJECTED_INSUFFICIENT_CASH,
    REJECTED_INSUFFICIENT_SHARES,
    REJECTED_INVALID_QUANTITY,
    UNKNOWN_SYMBOL,
)
from ...models import CashTransaction, Holding, Order, RulesConfig, User
from ..guardrails.rules import evaluate
from ..ledger.service import cash_balance
from ..prices.engine import price_engine


def place_order(db: Session, user: User, symbol: str, side: str, quantity) -> Order:
    symbol = (symbol or "").upper()
    quote = price_engine.quote(symbol)
    if not quote:
        raise HTTPException(status_code=404, detail=UNKNOWN_SYMBOL)

    if side not in ("buy", "sell"):
        raise HTTPException(status_code=422, detail="side must be 'buy' or 'sell'")

    # Whole, positive quantities only (bool is an int subclass — exclude it).
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 1:
        return _record_attempt(db, user.id, symbol, side, 0, "rejected", REJECTED_INVALID_QUANTITY)

    price = quote["price"]

    # Guardrail gate — block wins, nothing else runs (real rules: Wed, §3.4).
    rules = db.query(RulesConfig).filter(RulesConfig.user_id == user.id).first()
    decision = evaluate(
        {"user_id": user.id, "symbol": symbol, "side": side, "quantity": quantity},
        None,  # gstate lands with Wednesday's state.py
        rules,
    )
    if not decision.allowed:
        return _record_attempt(db, user.id, symbol, side, quantity, "blocked", decision.reason)

    cash = cash_balance(db, user.id)
    holding = db.query(Holding).filter(Holding.user_id == user.id, Holding.symbol == symbol).first()

    if side == "buy":
        cost = round(price * quantity, 2)
        if cash + 1e-9 < cost:
            return _record_attempt(db, user.id, symbol, side, quantity, "rejected", REJECTED_INSUFFICIENT_CASH)
    else:
        if not holding or holding.quantity < quantity:
            return _record_attempt(db, user.id, symbol, side, quantity, "rejected", REJECTED_INSUFFICIENT_SHARES)

    # -- the fill: one transaction, books move together --------------------------------
    if side == "buy":
        realized = None
    else:
        realized = round(quantity * (price - holding.avg_cost), 2)

    order = Order(
        user_id=user.id,
        symbol=symbol,
        side=side,
        quantity=quantity,
        order_type="market",
        status="filled",
        filled_price=price,
        realized_pnl=realized,
    )
    db.add(order)
    db.flush()  # order.id exists for the cash txn reference

    if side == "buy":
        cost = round(price * quantity, 2)
        new_cash = round(cash - cost, 2)
        if holding:
            total = holding.quantity + quantity
            holding.avg_cost = round(
                (holding.quantity * holding.avg_cost + quantity * price) / total, 4
            )
            holding.quantity = total
        else:
            db.add(Holding(user_id=user.id, symbol=symbol, quantity=quantity, avg_cost=price))
        db.add(
            CashTransaction(
                user_id=user.id, amount=-cost, kind="buy", order_id=order.id,
                balance_after=new_cash,
            )
        )
    else:
        proceeds = round(price * quantity, 2)
        new_cash = round(cash + proceeds, 2)
        holding.quantity -= quantity
        if holding.quantity == 0:
            db.delete(holding)
        db.add(
            CashTransaction(
                user_id=user.id, amount=proceeds, kind="sell", order_id=order.id,
                balance_after=new_cash,
            )
        )

    db.commit()
    db.refresh(order)
    return order


def order_history(db: Session, user_id: int, limit: int = 50) -> list[Order]:
    return (
        db.query(Order)
        .filter(Order.user_id == user_id)
        .order_by(Order.id.desc())
        .limit(limit)
        .all()
    )


def _record_attempt(db: Session, user_id: int, symbol: str, side: str, quantity: int,
                    status: str, reason: str) -> Order:
    """AC-6.1: every attempt lands in history with its exact reason string —
    but rejected/blocked orders never touch cash or holdings."""
    order = Order(
        user_id=user_id,
        symbol=symbol,
        side=side,
        quantity=quantity,
        order_type="market",
        status=status,
        reason=reason,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order
