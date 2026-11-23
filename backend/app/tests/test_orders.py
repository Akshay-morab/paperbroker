"""Order engine tests — the app's heart (DESIGN.md §3.3, PRD FR3/FR4/FR6).

Key technique: the price engine ticks on a live timer, so every assertion uses
the order's OWN filled_price from the response, never a re-read of the quote.
"""

import uuid

import pytest
from fastapi.testclient import TestClient

from app.core.db import Base, SessionLocal, engine
from app.main import app
from app.models import Stock


def _ensure_instrument():
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if not db.query(Stock).filter(Stock.symbol == "TEST").first():
            db.add(Stock(symbol="TEST", name="Test Inc", base_price=100.0, volatility=0.02, seed=42))
            db.commit()


@pytest.fixture(autouse=True)
def _instrument():
    _ensure_instrument()
    yield


def _cash(client):
    return client.get("/api/me").json()["cash"]


def test_buy_fills_and_moves_the_books():
    with TestClient(app) as client:
        email = f"buy-{uuid.uuid4().hex[:8]}@test.dev"
        client.post("/api/auth/signup", json={"email": email, "password": "DemoPass123"})

        r = client.post("/api/orders", json={"symbol": "TEST", "side": "buy", "quantity": 10})
        assert r.status_code == 201
        order = r.json()
        assert order["status"] == "filled"
        price = order["filled_price"]
        assert price > 0

        # Books moved together: cash dropped by exactly qty*price.
        assert _cash(client) == round(100000.0 - 10 * price, 2)

        portfolio = client.get("/api/portfolio").json()
        assert portfolio["positions"][0]["symbol"] == "TEST"
        assert portfolio["positions"][0]["quantity"] == 10
        assert portfolio["equity"] == 100000.0  # buy at market: equity unchanged


def test_second_buy_reweights_average_cost():
    with TestClient(app) as client:
        email = f"avg-{uuid.uuid4().hex[:8]}@test.dev"
        client.post("/api/auth/signup", json={"email": email, "password": "DemoPass123"})

        first = client.post("/api/orders", json={"symbol": "TEST", "side": "buy", "quantity": 10}).json()
        second = client.post("/api/orders", json={"symbol": "TEST", "side": "buy", "quantity": 10}).json()
        p1, p2 = first["filled_price"], second["filled_price"]

        position = client.get("/api/portfolio").json()["positions"][0]
        assert position["quantity"] == 20
        assert position["avg_cost"] == round((10 * p1 + 10 * p2) / 20, 4)


def test_insufficient_cash_rejected_without_touching_books():
    with TestClient(app) as client:
        email = f"cash-{uuid.uuid4().hex[:8]}@test.dev"
        client.post("/api/auth/signup", json={"email": email, "password": "DemoPass123"})

        r = client.post("/api/orders", json={"symbol": "TEST", "side": "buy", "quantity": 1_000_000})
        assert r.status_code == 400
        body = r.json()
        assert body["status"] == "rejected"
        assert body["reason"] == "Rejected: insufficient cash"

        # Atomicity: cash untouched, no position — but the attempt IS recorded (AC-6.1).
        assert _cash(client) == 100000.0
        assert client.get("/api/portfolio").json()["positions"] == []
        history = client.get("/api/orders").json()
        assert history[0]["status"] == "rejected"
        assert history[0]["reason"] == "Rejected: insufficient cash"


def test_sell_requires_holdings():
    with TestClient(app) as client:
        email = f"sell-{uuid.uuid4().hex[:8]}@test.dev"
        client.post("/api/auth/signup", json={"email": email, "password": "DemoPass123"})

        r = client.post("/api/orders", json={"symbol": "TEST", "side": "sell", "quantity": 5})
        assert r.status_code == 400
        assert r.json()["reason"] == "Rejected: insufficient shares"

        # Buy 5, then try to sell 10 — still refused.
        client.post("/api/orders", json={"symbol": "TEST", "side": "buy", "quantity": 5})
        r = client.post("/api/orders", json={"symbol": "TEST", "side": "sell", "quantity": 10})
        assert r.status_code == 400
        assert r.json()["reason"] == "Rejected: insufficient shares"


def test_invalid_quantity_rejected():
    with TestClient(app) as client:
        email = f"qty-{uuid.uuid4().hex[:8]}@test.dev"
        client.post("/api/auth/signup", json={"email": email, "password": "DemoPass123"})

        for qty in (0, -5, 2.5):
            r = client.post("/api/orders", json={"symbol": "TEST", "side": "buy", "quantity": qty})
            assert r.status_code == 400, qty
            assert r.json()["reason"] == "Rejected: invalid quantity", qty

        assert _cash(client) == 100000.0
        assert client.get("/api/portfolio").json()["positions"] == []


def test_sell_roundtrip_closes_the_position():
    with TestClient(app) as client:
        email = f"round-{uuid.uuid4().hex[:8]}@test.dev"
        client.post("/api/auth/signup", json={"email": email, "password": "DemoPass123"})

        buy = client.post("/api/orders", json={"symbol": "TEST", "side": "buy", "quantity": 10})
        assert buy.status_code == 201
        buy_price = buy.json()["filled_price"]

        sell = client.post("/api/orders", json={"symbol": "TEST", "side": "sell", "quantity": 10})
        assert sell.status_code == 201
        sell_order = sell.json()
        sell_price = sell_order["filled_price"]

        # Realized P&L booked on the sell, against the actual buy price paid.
        assert sell_order["realized_pnl"] == round(10 * (sell_price - buy_price), 2)

        # Position closed: row gone, cash back (plus/minus the round-trip delta).
        assert client.get("/api/portfolio").json()["positions"] == []
        assert _cash(client) == round(100000.0 + 10 * (sell_price - buy_price), 2)

        # History shows both fills, newest first.
        history = client.get("/api/orders").json()
        assert [h["side"] for h in history[:2]] == ["sell", "buy"]
        assert all(h["status"] == "filled" for h in history[:2])


def test_unknown_symbol_is_404():
    with TestClient(app) as client:
        email = f"sym-{uuid.uuid4().hex[:8]}@test.dev"
        client.post("/api/auth/signup", json={"email": email, "password": "DemoPass123"})

        r = client.post("/api/orders", json={"symbol": "NOPE", "side": "buy", "quantity": 1})
        assert r.status_code == 404
        assert r.json()["detail"] == "unknown symbol"
