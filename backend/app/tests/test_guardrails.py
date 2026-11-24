"""Guardrail integration — the persona-driven flows the judges will see (PRD FR5).

The tilted persona is the star: one bad sell from the kill switch. The cooldown
persona is already locked. These tests mirror kane/tests/kill_switch and
overtrade step for step."""

import uuid

import pytest
from fastapi.testclient import TestClient

from app.core.db import Base, SessionLocal, engine
from app.main import app
from app.models import User
from app.seed import seed_cooldown, seed_fresh, seed_instruments, seed_tilted


@pytest.fixture(autouse=True)
def _seeded():
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        seed_instruments(db)
        seed_fresh(db)
        seed_tilted(db)
        seed_cooldown(db)
    finally:
        db.close()
    yield


def _login(client, email):
    r = client.post("/api/auth/login", json={"email": email, "password": "demo1234"})
    assert r.status_code == 200
    return r


def _reset(db):
    seed_tilted(db)  # persona state is consumed by these tests — restore per test


def test_tilted_is_one_bad_sell_from_the_kill_switch():
    with TestClient(app) as client:
        db = SessionLocal()
        try:
            _reset(db)
        finally:
            db.close()

        _login(client, "tilted@demo")
        status = client.get("/api/guardrails/status").json()
        assert status["locked"] is False  # trailing winners broke the streak
        assert status["daily_loss"]["remaining"] == 300.0

        # The trip: sell the remaining 10 TSLA (avg cost 420 >> live price).
        r = client.post("/api/orders", json={"symbol": "TSLA", "side": "sell", "quantity": 10})
        assert r.status_code == 201
        sell = r.json()
        assert sell["realized_pnl"] < 0

        # Status flips to locked, with the exact banner text.
        status2 = client.get("/api/guardrails/status").json()
        assert status2["locked"] is True
        assert status2["lock_reason"] == "Trading locked until tomorrow."

        # Any further trade is blocked with the exact reason string.
        r2 = client.post("/api/orders", json={"symbol": "AAPL", "side": "buy", "quantity": 1})
        assert r2.status_code == 403
        assert r2.json()["reason"] == "Blocked: daily loss limit reached. Trading locked until tomorrow."

        # The blocked attempt is recorded, never counted as a trade.
        history = client.get("/api/orders").json()
        assert history[0]["status"] == "blocked"
        assert history[0]["reason"] == "Blocked: daily loss limit reached. Trading locked until tomorrow."


def test_tilted_10th_trade_allowed_then_overtrade_blocked():
    with TestClient(app) as client:
        db = SessionLocal()
        try:
            _reset(db)
        finally:
            db.close()

        _login(client, "tilted@demo")
        # 9/10 used today: the 10th is allowed (a BUY realizes nothing, kill switch not tripped).
        r = client.post("/api/orders", json={"symbol": "AAPL", "side": "buy", "quantity": 1})
        assert r.status_code == 201

        # The 11th is blocked with the (10/10) message.
        r2 = client.post("/api/orders", json={"symbol": "AAPL", "side": "buy", "quantity": 1})
        assert r2.status_code == 403
        assert r2.json()["reason"] == "Blocked: daily trade limit reached (10/10)."


def test_cooldown_persona_is_locked_now():
    with TestClient(app) as client:
        _login(client, "cooldown@demo")

        status = client.get("/api/guardrails/status").json()
        assert status["locked"] is True
        assert status["lock_reason"].startswith("Cooldown active — try again in")

        r = client.post("/api/orders", json={"symbol": "AAPL", "side": "buy", "quantity": 1})
        assert r.status_code == 403
        reason = r.json()["reason"]
        assert reason.startswith("Blocked: cooldown active after 3 consecutive losses. Try again in")


def test_position_size_cap_blocks_oversized_buy():
    with TestClient(app) as client:
        email = f"size-{uuid.uuid4().hex[:8]}@test.dev"
        client.post("/api/auth/signup", json={"email": email, "password": "DemoPass123"})

        # Affordable but too big: ~$46k passes the cash check (validation runs first)
        # and trips the 20%-of-equity cap ($20k).
        r = client.post("/api/orders", json={"symbol": "AAPL", "side": "buy", "quantity": 200})
        assert r.status_code == 403
        assert r.json()["reason"] == "Blocked: order exceeds position size cap (20% of equity)."

        # A sane-size buy goes through.
        ok = client.post("/api/orders", json={"symbol": "AAPL", "side": "buy", "quantity": 1})
        assert ok.status_code == 201


def test_max_open_positions():
    with TestClient(app) as client:
        email = f"pos-{uuid.uuid4().hex[:8]}@test.dev"
        client.post("/api/auth/signup", json={"email": email, "password": "DemoPass123"})

        for symbol in ["AAPL", "MSFT", "NVDA", "AMZN", "GOOG"]:
            r = client.post("/api/orders", json={"symbol": symbol, "side": "buy", "quantity": 1})
            assert r.status_code == 201, symbol

        r = client.post("/api/orders", json={"symbol": "META", "side": "buy", "quantity": 1})
        assert r.status_code == 403
        assert r.json()["reason"] == "Blocked: max open positions reached (5)."

        # Buying INTO an existing position is still fine.
        ok = client.post("/api/orders", json={"symbol": "AAPL", "side": "buy", "quantity": 1})
        assert ok.status_code == 201


def test_admin_reset_personas_requires_admin():
    with TestClient(app) as client:
        # a trader account gets 403
        _login(client, "fresh@demo")
        r = client.post("/api/admin/reset-personas")
        assert r.status_code == 403

        # an admin (created directly, role=admin) may reset
        db = SessionLocal()
        try:
            email = f"admin-{uuid.uuid4().hex[:6]}@test.dev"
            from app.auth import service as auth_service
            from app.models import CashTransaction, RulesConfig

            user = User(email=email, password_hash=auth_service.hash_password("AdminPass123"), role="admin")
            db.add(user)
            db.flush()
            db.add(RulesConfig(user_id=user.id))
            db.add(CashTransaction(user_id=user.id, amount=100000.0, kind="signup_credit", balance_after=100000.0))
            db.commit()
        finally:
            db.close()

        client.post("/api/auth/login", json={"email": email, "password": "AdminPass123"})
        r2 = client.post("/api/admin/reset-personas")
        assert r2.status_code == 200
        assert r2.json()["ok"] is True
