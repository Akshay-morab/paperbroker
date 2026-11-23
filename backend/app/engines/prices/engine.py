"""Deterministic simulated market data (DESIGN.md §3.2).

Every symbol gets a seeded random walk: same seed -> same series within a session.
Prices live in memory and NEVER touch the DB — write volume stays human-paced.
The future microservice extraction point: swap this module for an HTTP client.
"""

import asyncio
import random
from dataclasses import dataclass

CANDLE_HISTORY = 120
TICK_SECONDS = 3.0
MIN_PRICE = 0.01


@dataclass
class SymbolState:
    symbol: str
    name: str
    volatility: float
    price: float
    session_open: float
    live_rng: random.Random
    candles: list[dict]


class PriceEngine:
    """In-memory price simulator. One instance per process; ticks on the event loop."""

    def __init__(self) -> None:
        self._state: dict[str, SymbolState] = {}

    # -- loading ---------------------------------------------------------------

    def add_symbol(self, row) -> None:
        """Accepts anything with .symbol .name .base_price .volatility .seed (the Stock model,
        or a test double — keeps the engine DB-free and unit-testable)."""
        hist_rng = random.Random(row.seed * 1000 + 7)
        price = row.base_price
        session_open = price
        candles: list[dict] = []
        for i in range(CANDLE_HISTORY):
            prev = price
            price = max(prev * (1 + row.volatility * hist_rng.gauss(0, 1)), MIN_PRICE)
            hi = max(prev, price) * (1 + abs(hist_rng.gauss(0, 0.003)))
            lo = min(prev, price) * (1 - abs(hist_rng.gauss(0, 0.003)))
            candles.append(
                {
                    "t": i,
                    "o": round(prev, 2),
                    "h": round(hi, 2),
                    "l": round(lo, 2),
                    "c": round(price, 2),
                }
            )
        self._state[row.symbol.upper()] = SymbolState(
            symbol=row.symbol.upper(),
            name=row.name,
            volatility=row.volatility,
            price=round(price, 2),
            session_open=round(session_open, 2),
            live_rng=random.Random(row.seed),
            candles=candles,
        )

    def load_from_db(self, db) -> None:
        from ...models import Stock  # local import keeps the engine DB-optional

        self._state.clear()
        for stock in db.query(Stock).all():
            self.add_symbol(stock)

    # -- ticking ----------------------------------------------------------------

    def tick(self) -> None:
        for state in self._state.values():
            drift = state.live_rng.gauss(0, 1)
            state.price = round(max(state.price * (1 + state.volatility * drift), MIN_PRICE), 2)

    async def tick_loop(self) -> None:
        while True:
            await asyncio.sleep(TICK_SECONDS)
            self.tick()

    # -- reads -------------------------------------------------------------------

    def quote(self, symbol: str) -> dict | None:
        state = self._state.get(symbol.upper())
        if not state:
            return None
        change_pct = round((state.price / state.session_open - 1) * 100, 2)
        return {
            "symbol": state.symbol,
            "name": state.name,
            "price": state.price,
            "session_open": state.session_open,
            "change_pct": change_pct,
        }

    def detail(self, symbol: str) -> dict | None:
        quote = self.quote(symbol)
        if not quote:
            return None
        state = self._state[symbol.upper()]
        return {**quote, "candles": state.candles}

    def list_quotes(self) -> list[dict]:
        return [self.quote(s) for s in sorted(self._state)]


# Single process-wide instance; main.py starts its tick loop in the app lifespan.
price_engine = PriceEngine()
