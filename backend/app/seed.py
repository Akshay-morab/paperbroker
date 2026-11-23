"""Seed the instrument master + demo personas (DESIGN.md §4).

Run:  python -m app.seed                (full seed; idempotent)
      python -m app.seed --personas-only (re-tilt personas — run before demos/judging)

Personas (password demo1234 for all):
  fresh@demo     — clean account, $100,000, no trades
  tilted@demo    — down $9,700 realized TODAY over 9 trades: one bad sell away from the
                   kill switch (§6.6 daily-reset gotcha: re-run this the day you demo)
  cooldown@demo — 3 straight losses, the last 5 minutes ago → ~25 min of cooldown left

Bookkeeping note: every persona's rows are constructed so the books balance —
each cash txn carries a correct balance_after, holdings match the buy/sell history.
Run the seed on the same day you demo: 'today' comparisons are calendar-based.
"""

import argparse
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from .auth import service as auth_service
from .core.config import admin_emails, admin_password, starting_cash
from .models import CashTransaction, Holding, Order, RulesConfig, Session as SessionRow, Stock, User
from .core.db import Base, SessionLocal, engine

PERSONA_PASSWORD = "demo1234"

INSTRUMENTS = [
    {"symbol": "AAPL", "name": "Apple Inc.", "base_price": 230.0, "volatility": 0.02, "seed": 101},
    {"symbol": "MSFT", "name": "Microsoft Corp.", "base_price": 420.0, "volatility": 0.02, "seed": 202},
    {"symbol": "NVDA", "name": "NVIDIA Corp.", "base_price": 135.0, "volatility": 0.035, "seed": 303},
    {"symbol": "AMZN", "name": "Amazon.com Inc.", "base_price": 205.0, "volatility": 0.025, "seed": 404},
    {"symbol": "GOOG", "name": "Alphabet Inc.", "base_price": 175.0, "volatility": 0.02, "seed": 505},
    {"symbol": "META", "name": "Meta Platforms", "base_price": 585.0, "volatility": 0.028, "seed": 606},
    {"symbol": "NFLX", "name": "Netflix Inc.", "base_price": 900.0, "volatility": 0.03, "seed": 707},
    {"symbol": "TSLA", "name": "Tesla Inc.", "base_price": 340.0, "volatility": 0.03, "seed": 808},
]


def seed_instruments(db: Session) -> None:
    for row in INSTRUMENTS:
        if not db.query(Stock).filter(Stock.symbol == row["symbol"]).first():
            db.add(Stock(**row))
    db.commit()


def _reset_user_rows(db: Session, email: str) -> None:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return
    db.query(Order).filter(Order.user_id == user.id).delete()
    db.query(CashTransaction).filter(CashTransaction.user_id == user.id).delete()
    db.query(Holding).filter(Holding.user_id == user.id).delete()
    db.query(RulesConfig).filter(RulesConfig.user_id == user.id).delete()
    db.query(SessionRow).filter(SessionRow.user_id == user.id).delete()
    db.query(User).filter(User.id == user.id).delete()
    db.commit()


def _create_persona(db: Session, email: str) -> User:
    user = User(email=email, password_hash=auth_service.hash_password(PERSONA_PASSWORD))
    db.add(user)
    db.flush()
    db.add(RulesConfig(user_id=user.id))
    return user


def _credit(db: Session, user_id: int, cash: float) -> None:
    db.add(
        CashTransaction(
            user_id=user_id, amount=round(cash, 2), kind="signup_credit", balance_after=round(cash, 2)
        )
    )


def _filled_order(db: Session, user_id: int, symbol: str, side: str, qty: int,
                  price: float, realized_pnl: float | None, created_at: datetime) -> None:
    db.add(
        Order(
            user_id=user_id,
            symbol=symbol,
            side=side,
            quantity=qty,
            order_type="market",
            status="filled",
            filled_price=round(price, 2),
            realized_pnl=None if realized_pnl is None else round(realized_pnl, 2),
            created_at=created_at,
        )
    )


def _cash_move(db: Session, user_id: int, amount: float, kind: str, balance_after: float,
               created_at: datetime) -> None:
    db.add(
        CashTransaction(
            user_id=user_id,
            amount=round(amount, 2),
            kind=kind,
            balance_after=round(balance_after, 2),
            created_at=created_at,
        )
    )


def seed_fresh(db: Session) -> None:
    _reset_user_rows(db, "fresh@demo")
    user = _create_persona(db, "fresh@demo")
    _credit(db, user.id, starting_cash())
    db.commit()


def seed_tilted(db: Session) -> None:
    """-$9,700 realized today across 9 fills: the 10th trade (a sell of the remaining
    TSLA at any plausible price) trips the $10,000 kill switch."""
    _reset_user_rows(db, "tilted@demo")
    user = _create_persona(db, "tilted@demo")
    now = datetime.now()
    yesterday = now - timedelta(days=1)

    cash = starting_cash()
    _credit(db, user.id, cash)

    # Bought 100 TSLA @ 420 yesterday (way above the ~340 sim price: any sell realizes a loss).
    buy_cost = 100 * 420.0
    cash -= buy_cost
    _filled_order(db, user.id, "TSLA", "buy", 100, 420.0, None, yesterday)
    _cash_move(db, user.id, -buy_cost, "buy", cash, yesterday)
    # Holds 10 TSLA @ avg 420 after the sells — the kill-switch trip lever.
    # (Holdings rows are constructed directly in their post-sell state: order rows carry the narrative.)
    db.add(Holding(user_id=user.id, symbol="TSLA", quantity=10, avg_cost=420.0))

    # 9 loss-realizing sells today: 8 x 10 @ 312.00, then 1 x 10 @ 314.00.
    # pnl: 8 x (10 * (312 - 420)) = -8,640 ; + 10 * (314 - 420) = -1,060  =>  -9,700 total.
    sell_prices = [312.00] * 8 + [314.00]
    for i, price in enumerate(sell_prices):
        pnl = 10 * (price - 420.0)
        qty_delta = 10 * price
        cash += qty_delta
        at = now - timedelta(minutes=[95, 88, 80, 70, 60, 45, 30, 18, 8][i])
        _filled_order(db, user.id, "TSLA", "sell", 10, price, pnl, at)
        _cash_move(db, user.id, qty_delta, "sell", cash, at)

    db.commit()


def seed_cooldown(db: Session) -> None:
    """3 straight losing sells, the last 5 minutes ago -> cooldown_until = now + ~25 min."""
    _reset_user_rows(db, "cooldown@demo")
    user = _create_persona(db, "cooldown@demo")
    now = datetime.now()
    yesterday = now - timedelta(days=1)

    cash = starting_cash()
    _credit(db, user.id, cash)

    buy_cost = 50 * 300.0
    cash -= buy_cost
    _filled_order(db, user.id, "AAPL", "buy", 50, 300.0, None, yesterday)
    _cash_move(db, user.id, -buy_cost, "buy", cash, yesterday)
    # Holds 20 AAPL @ avg 300 after the three losing sells.
    db.add(Holding(user_id=user.id, symbol="AAPL", quantity=20, avg_cost=300.0))

    for i, minutes_ago in enumerate([20, 12, 5]):
        price = 252.0  # 10 x (252 - 300) = -480 per sell
        pnl = 10 * (price - 300.0)
        cash += 10 * price
        at = now - timedelta(minutes=minutes_ago)
        _filled_order(db, user.id, "AAPL", "sell", 10, price, pnl, at)
        _cash_move(db, user.id, 10 * price, "sell", cash, at)

    db.commit()


def seed_admins(db: Session) -> None:
    emails = admin_emails()
    if not emails:
        return
    password = admin_password() or "admin-change-me"
    for email in emails:
        if not db.query(User).filter(User.email == email).first():
            user = User(email=email.strip().lower(),
                        password_hash=auth_service.hash_password(password), role="admin")
            db.add(user)
            db.flush()
            db.add(RulesConfig(user_id=user.id))
            _credit(db, user.id, starting_cash())
    db.commit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed PaperBroker")
    parser.add_argument("--personas-only", action="store_true",
                        help="re-tilt the demo personas (run the same day you demo)")
    args = parser.parse_args()

    Base.metadata.create_all(engine)  # standalone script: tables must exist before seeding

    db = SessionLocal()
    try:
        if not args.personas_only:
            seed_instruments(db)
            seed_admins(db)
        seed_fresh(db)
        seed_tilted(db)
        seed_cooldown(db)
        print("Seed complete. Personas: fresh@demo / tilted@demo / cooldown@demo (password: demo1234)")
    finally:
        db.close()


if __name__ == "__main__":
    main()
