"""Dividends: holdings earn their stock's yield on the demo clock, credited as
real ledger rows, surfaced as dividends_earned in the portfolio."""

import uuid

import pytest
from fastapi.testclient import TestClient

from app.core.db import Base, SessionLocal, engine
from app.engines.ledger.dividends import credit_quarterly_dividends
from app.engines.ledger.service import portfolio
from app.engines.prices.engine import price_engine
from app.main import app
from app.models import CashTransaction, Holding, StockProfile, User
from app.seed import seed_instruments, seed_profiles


@pytest.fixture(autouse=True)
def _tables():
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        seed_instruments(db)
        seed_profiles(db)
        price_engine.load_from_db(db)  # the credit loop reads live prices
    finally:
        db.close()
    yield


def test_dividends_credit_for_holdings():
    email = f"div-{uuid.uuid4().hex[:8]}@test.dev"
    db = SessionLocal()
    try:
        user = User(email=email, password_hash="x")
        db.add(user)
        db.flush()
        db.add(CashTransaction(user_id=user.id, amount=100000.0, kind="signup_credit", balance_after=100000.0))

        # MSFT (not AAPL — the seed test asserts on AAPL's yield range).
        profile = db.get(StockProfile, "MSFT")
        profile.dividend_yield = 4.0  # deterministic for the assert below
        db.add(Holding(user_id=user.id, symbol="MSFT", quantity=100, avg_cost=420.0))
        db.commit()
        user_id = user.id
    finally:
        db.close()

    db = SessionLocal()
    try:
        credit_quarterly_dividends(db)
    finally:
        db.close()

    db = SessionLocal()
    try:
        p = portfolio(db, user_id)
        # 100 shares x ~$420 price x 4%/yr / 4 quarters ~= $420 per quarter.
        assert p["dividends_earned"] > 100
        assert p["cash"] > 100000
        assert p["pnl"] > 0
        assert p["starting_cash"] == 100000.0
    finally:
        db.close()


def test_dividends_zero_without_holdings():
    with TestClient(app) as client:
        email = f"nodiv-{uuid.uuid4().hex[:8]}@test.dev"
        client.post("/api/auth/signup", json={"email": email, "password": "DemoPass123"})

        p = client.get("/api/portfolio").json()
        assert p["dividends_earned"] == 0.0
        assert p["pnl"] == 0.0
        assert p["pnl_pct"] == 0.0
        assert p["starting_cash"] == 100000.0
