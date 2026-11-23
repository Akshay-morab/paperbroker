"""Engine unit tests: determinism and clamping (the two invariants that make
demos repeatable and Kane replays stable — DESIGN.md §3.2)."""

from app.engines.prices.engine import CANDLE_HISTORY, PriceEngine


class Row:
    """Test double for the Stock model — the engine stays DB-free."""

    def __init__(self, symbol, name, base_price, volatility, seed):
        self.symbol = symbol
        self.name = name
        self.base_price = base_price
        self.volatility = volatility
        self.seed = seed


def test_same_seed_same_series():
    e1, e2 = PriceEngine(), PriceEngine()
    e1.add_symbol(Row("X", "X Inc", 100.0, 0.02, 7))
    e2.add_symbol(Row("X", "X Inc", 100.0, 0.02, 7))
    for _ in range(10):
        e1.tick()
        e2.tick()
    assert e1.quote("X")["price"] == e2.quote("X")["price"]


def test_price_clamped_positive():
    e = PriceEngine()
    e.add_symbol(Row("Y", "Y Inc", 10.0, 5.0, 9))  # absurd volatility on purpose
    for _ in range(50):
        e.tick()
    assert e.quote("Y")["price"] > 0


def test_detail_has_candle_history():
    e = PriceEngine()
    e.add_symbol(Row("Z", "Z Inc", 50.0, 0.02, 5))
    detail = e.detail("Z")
    assert len(detail["candles"]) == CANDLE_HISTORY
    assert detail["price"] > 0


def test_unknown_symbol_returns_none():
    e = PriceEngine()
    e.add_symbol(Row("Z", "Z Inc", 50.0, 0.02, 5))
    assert e.quote("NOPE") is None
    assert e.detail("nope") is None
