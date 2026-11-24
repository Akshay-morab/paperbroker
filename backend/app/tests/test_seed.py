"""Seed invariants — the personas' books must balance (DESIGN.md §3.5) and their
guardrail-relevant state must match PRD.md exactly. These tests make the seed math
impossible to break silently."""

from datetime import datetime

import pytest

from app.core.db import Base, SessionLocal, engine
from app.models import CashTransaction, Holding, Order, StockFinancial, StockProfile, User
from app.seed import seed_cooldown, seed_instruments, seed_profiles, seed_tilted


@pytest.fixture(autouse=True)
def _tables():
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        seed_instruments(db)  # personas hold TSLA/AAPL — FKs need the instrument master
        seed_profiles(db)
    finally:
        db.close()
    yield


def test_profiles_and_financials_seeded():
    db = SessionLocal()
    try:
        profile = db.get(StockProfile, "AAPL")
        assert profile is not None
        assert profile.sector == "Technology"
        assert profile.eps > 0 and profile.shares_outstanding > 0

        rows = (
            db.query(StockFinancial)
            .filter(StockFinancial.symbol == "AAPL")
            .order_by(StockFinancial.year)
            .all()
        )
        assert len(rows) == 5
        assert rows[0].year < rows[-1].year
        assert all(r.revenue > 0 for r in rows)
    finally:
        db.close()


def _user(db, email):
    return db.query(User).filter(User.email == email).one()


def _sells(db, user_id):
    return (
        db.query(Order)
        .filter(Order.user_id == user_id, Order.side == "sell")
        .order_by(Order.id)
        .all()
    )


def _last_cash(db, user_id):
    return (
        db.query(CashTransaction)
        .filter(CashTransaction.user_id == user_id)
        .order_by(CashTransaction.id.desc())
        .first()
    )


def test_tilted_persona_is_one_bad_sell_from_the_kill_switch():
    db = SessionLocal()
    try:
        seed_tilted(db)
        user = _user(db, "tilted@demo")

        sells = _sells(db, user.id)
        assert len(sells) == 9
        assert len([o for o in sells if o.realized_pnl is not None and o.realized_pnl < 0]) == 6
        assert len([o for o in sells if (o.realized_pnl or 0) > 0]) == 3  # trailing winners break the streak
        assert round(sum(o.realized_pnl for o in sells), 2) == -9700.0  # $300 from the $10,000 limit

        # The trip lever: remaining position guaranteed to realize a loss at any plausible sim price.
        holding = db.query(Holding).filter(Holding.user_id == user.id).one()
        assert (holding.symbol, holding.quantity, holding.avg_cost) == ("TSLA", 10, 420.0)

        # Books balance: audit trail replays to the expected cash figure.
        # 100,000 − (100×420) + 8×(10×312) + (10×314) = 86,100
        assert _last_cash(db, user.id).balance_after == 86100.0
    finally:
        db.close()


def test_cooldown_persona_mid_cooldown():
    db = SessionLocal()
    try:
        seed_cooldown(db)
        user = _user(db, "cooldown@demo")

        sells = _sells(db, user.id)
        assert len(sells) == 3
        assert all(o.realized_pnl < 0 for o in sells)  # three straight losses
        assert round(sum(o.realized_pnl for o in sells), 2) == -1440.0

        # The 3rd loss was 5 minutes ago: cooldown_until ≈ now + 25 min (asserted loosely).
        third = sells[-1]
        age_minutes = (datetime.now() - third.created_at).total_seconds() / 60
        assert 0 <= age_minutes <= 10

        holding = db.query(Holding).filter(Holding.user_id == user.id).one()
        assert (holding.symbol, holding.quantity, holding.avg_cost) == ("AAPL", 20, 300.0)

        assert _last_cash(db, user.id).balance_after == 92560.0
    finally:
        db.close()
