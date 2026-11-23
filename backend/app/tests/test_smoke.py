"""End-to-end smoke over the FastAPI TestClient: signup credit, cookies,
quotes, candles, unknown-symbol 404, duplicate email (DESIGN.md flows #1-adjacent)."""

import uuid

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


def test_signup_quotes_flow():
    _ensure_instrument()
    email = f"smoke-{uuid.uuid4().hex[:8]}@test.dev"

    with TestClient(app) as client:
        r = client.post("/api/auth/signup", json={"email": email, "password": "DemoPass123"})
        assert r.status_code == 201
        body = r.json()
        assert body["email"] == email
        assert body["cash"] == 100000.0
        assert body["rules"]["max_trades_per_day"] == 10

        short = client.post("/api/auth/signup", json={"email": "short-pw@x.dev", "password": "short"})
        assert short.status_code == 422

        dup = client.post("/api/auth/signup", json={"email": email, "password": "DemoPass123"})
        assert dup.status_code == 409
        assert dup.json()["detail"] == "email already registered"

        stocks = client.get("/api/stocks")
        assert stocks.status_code == 200
        assert "TEST" in [s["symbol"] for s in stocks.json()]

        detail = client.get("/api/stocks/TEST")
        assert detail.status_code == 200
        assert len(detail.json()["candles"]) == 120

        missing = client.get("/api/stocks/NOPE")
        assert missing.status_code == 404
        assert missing.json()["detail"] == "unknown symbol"

        me = client.get("/api/me")
        assert me.status_code == 200
        assert me.json()["email"] == email

        assert client.post("/api/auth/logout").status_code == 200
        assert client.get("/api/me").status_code == 401


def test_login_roundtrip():
    _ensure_instrument()
    email = f"login-{uuid.uuid4().hex[:8]}@test.dev"

    with TestClient(app) as client:
        client.post("/api/auth/signup", json={"email": email, "password": "DemoPass123"})
        client.post("/api/auth/logout")

        bad = client.post("/api/auth/login", json={"email": email, "password": "wrong"})
        assert bad.status_code == 401

        good = client.post("/api/auth/login", json={"email": email, "password": "DemoPass123"})
        assert good.status_code == 200
        assert good.json()["email"] == email
