"""Dividends: every holding earns its stock's dividend yield, on a demo-speed
clock — 1 real minute = 1 simulated quarter. Real quarters take three months;
nobody would ever see a payout in a demo. Credits are real cash transactions
(kind='dividend') so the ledger stays honest."""

import asyncio

from ...core.db import SessionLocal
from ...models import CashTransaction, Holding, StockProfile
from ..prices.engine import price_engine
from .service import cash_balance

DIVIDEND_INTERVAL_SECONDS = 60  # 1 real minute = 1 simulated quarter


def credit_quarterly_dividends(db) -> None:
    for holding in db.query(Holding).all():
        profile = db.get(StockProfile, holding.symbol)
        if not profile or profile.dividend_yield <= 0:
            continue
        quote = price_engine.quote(holding.symbol)
        if not quote:
            continue
        # Quarterly payout: position value x annual yield / 4.
        amount = round(holding.quantity * quote["price"] * (profile.dividend_yield / 100) / 4, 2)
        if amount < 0.01:
            continue
        balance = round(cash_balance(db, holding.user_id) + amount, 2)
        db.add(
            CashTransaction(
                user_id=holding.user_id,
                amount=amount,
                kind="dividend",
                balance_after=balance,
            )
        )
        db.commit()


async def dividends_loop() -> None:
    while True:
        await asyncio.sleep(DIVIDEND_INTERVAL_SECONDS)
        db = SessionLocal()
        try:
            credit_quarterly_dividends(db)
        except Exception:
            # A background payout must never take the app down; next tick retries.
            pass
        finally:
            db.close()
