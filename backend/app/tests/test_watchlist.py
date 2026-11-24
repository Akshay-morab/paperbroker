"""Watchlist round-trip: star, list, duplicate star, unstar, unknown symbol."""

import uuid

import pytest
from fastapi.testclient import TestClient

from app.core.db import Base, SessionLocal, engine
from app.main import app
from app.models import Stock


@pytest.fixture(autouse=True)
def _tables():
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        if not db.query(Stock).filter(Stock.symbol == "TEST").first():
            db.add(Stock(symbol="TEST", name="Test Inc", base_price=100.0, volatility=0.02, seed=42))
            db.commit()
    finally:
        db.close()
    yield


def test_watchlist_roundtrip():
    with TestClient(app) as client:
        email = f"wl-{uuid.uuid4().hex[:8]}@test.dev"
        client.post("/api/auth/signup", json={"email": email, "password": "DemoPass123"})

        assert client.get("/api/watchlist").json() == []

        r = client.post("/api/watchlist/AAPL")
        assert r.status_code == 201
        assert r.json()["starred"] is True

        symbols = [w["symbol"] for w in client.get("/api/watchlist").json()]
        assert symbols == ["AAPL"]

        # duplicate star is harmless
        assert client.post("/api/watchlist/AAPL").status_code == 201
        assert len(client.get("/api/watchlist").json()) == 1

        assert client.delete("/api/watchlist/AAPL").status_code == 200
        assert client.get("/api/watchlist").json() == []

        missing = client.post("/api/watchlist/NOPE")
        assert missing.status_code == 404
        assert missing.json()["detail"] == "unknown symbol"
