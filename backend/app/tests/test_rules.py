"""The five rules as pure functions — every rule x state combination (DESIGN.md §3.4).

Pure means testable without a browser, a DB, or a clock. These tests pin the
check ORDER and the EXACT reason strings Kane asserts on."""

from datetime import datetime, timedelta

from app.core.constants import (
    BLOCKED_COOLDOWN,
    BLOCKED_DAILY_LOSS,
    BLOCKED_OPEN_POSITIONS,
    BLOCKED_POSITION_SIZE,
    BLOCKED_TRADE_LIMIT,
)
from app.engines.guardrails.rules import evaluate


class Rules:
    """Duck-typed stand-in for the RulesConfig row (defaults per DESIGN)."""

    daily_loss_limit = 10_000.0
    max_trades_per_day = 10
    cooldown_minutes = 30
    loss_streak_trigger = 3
    max_position_pct = 0.20
    max_open_positions = 5


def _order(**over):
    base = {
        "user_id": 1,
        "symbol": "TEST",
        "side": "buy",
        "quantity": 10,
        "price": 100.0,
        "opens_new_position": True,
    }
    base.update(over)
    return base


def _state(**over):
    now = datetime.now()
    base = {
        "now": now,
        "realized_today": 0.0,
        "trades_used": 0,
        "cooldown_until": None,
        "open_positions": 0,
        "equity": 100_000.0,
    }
    base.update(over)
    return base


def test_fresh_account_allows_everything():
    d = evaluate(_order(), _state(), Rules())
    assert d.allowed and d.reason is None


def test_missing_state_or_rules_allows():
    assert evaluate(_order(), None, Rules()).allowed
    assert evaluate(_order(), _state(), None).allowed


def test_kill_switch_trips_at_limit():
    d = evaluate(_order(), _state(realized_today=-10_000.0), Rules())
    assert not d.allowed
    assert d.rule == "daily_loss_limit"
    assert d.reason == BLOCKED_DAILY_LOSS


def test_kill_switch_just_under_limit_allows():
    assert evaluate(_order(), _state(realized_today=-9_999.99), Rules()).allowed


def test_cooldown_active_blocks_with_countdown():
    until = _state()["now"] + timedelta(minutes=25, seconds=45)
    d = evaluate(_order(), _state(cooldown_until=until), Rules())
    assert not d.allowed
    assert d.rule == "cooldown"
    assert d.reason.startswith(
        BLOCKED_COOLDOWN.format(mmss="")[: -len(".")]
    )  # "Blocked: cooldown active after 3 consecutive losses. Try again in"
    assert "25:" in d.reason  # the countdown renders


def test_cooldown_expired_allows():
    until = _state()["now"] - timedelta(minutes=1)
    assert evaluate(_order(), _state(cooldown_until=until), Rules()).allowed


def test_trade_cap_blocks_at_limit():
    d = evaluate(_order(), _state(trades_used=10), Rules())
    assert not d.allowed
    assert d.reason == BLOCKED_TRADE_LIMIT
    assert d.rule == "trade_limit"


def test_position_size_cap_blocks_only_buys():
    blocked = evaluate(_order(quantity=300), _state(), Rules())  # 300*100 = 30k > 20% of 100k
    assert not blocked.allowed
    assert blocked.reason == BLOCKED_POSITION_SIZE
    # sells are never size-capped
    ok = evaluate(_order(side="sell", quantity=100_000), _state(), Rules())
    assert ok.allowed


def test_open_positions_cap_blocks_new_positions_only():
    blocked = evaluate(_order(quantity=1), _state(open_positions=5), Rules())
    assert not blocked.allowed
    assert blocked.reason == BLOCKED_OPEN_POSITIONS
    # buying INTO an existing position is fine
    ok = evaluate(_order(quantity=1, opens_new_position=False), _state(open_positions=5), Rules())
    assert ok.allowed


def test_precedence_kill_switch_wins():
    d = evaluate(
        _order(),
        _state(realized_today=-11_000.0, trades_used=10),
        Rules(),
    )
    assert d.rule == "daily_loss_limit"


def test_precedence_cooldown_beats_trade_cap():
    until = _state()["now"] + timedelta(minutes=5)
    d = evaluate(_order(), _state(trades_used=10, cooldown_until=until), Rules())
    assert d.rule == "cooldown"
