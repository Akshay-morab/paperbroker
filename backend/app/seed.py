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
import random
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from .auth import service as auth_service
from .core.config import admin_emails, admin_password, starting_cash
from .models import CashTransaction, Holding, Order, RulesConfig, Session as SessionRow, Stock, User
from .models import StockFinancial, StockProfile, WatchlistItem
from .core.db import Base, SessionLocal, engine
from .core.db import ensure_schema

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
    {"symbol": "AMD", "name": "Advanced Micro Devices", "base_price": 165.0, "volatility": 0.032, "seed": 909},
    {"symbol": "INTC", "name": "Intel Corp.", "base_price": 42.0, "volatility": 0.028, "seed": 1010},
    {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "base_price": 240.0, "volatility": 0.018, "seed": 1111},
    {"symbol": "V", "name": "Visa Inc.", "base_price": 310.0, "volatility": 0.015, "seed": 1212},
    {"symbol": "WMT", "name": "Walmart Inc.", "base_price": 92.0, "volatility": 0.015, "seed": 1313},
    {"symbol": "DIS", "name": "The Walt Disney Co.", "base_price": 110.0, "volatility": 0.022, "seed": 1414},
    {"symbol": "BA", "name": "The Boeing Co.", "base_price": 155.0, "volatility": 0.026, "seed": 1515},
    {"symbol": "NKE", "name": "Nike Inc.", "base_price": 78.0, "volatility": 0.02, "seed": 1616},
    {"symbol": "KO", "name": "The Coca-Cola Co.", "base_price": 63.0, "volatility": 0.012, "seed": 1717},
    {"symbol": "PEP", "name": "PepsiCo Inc.", "base_price": 70.0, "volatility": 0.012, "seed": 1818},
    {"symbol": "XOM", "name": "Exxon Mobil Corp.", "base_price": 118.0, "volatility": 0.02, "seed": 1919},
    {"symbol": "ORCL", "name": "Oracle Corp.", "base_price": 185.0, "volatility": 0.02, "seed": 2020},
    {"symbol": "CRM", "name": "Salesforce Inc.", "base_price": 330.0, "volatility": 0.024, "seed": 2121},
    {"symbol": "UBER", "name": "Uber Technologies", "base_price": 72.0, "volatility": 0.03, "seed": 2222},
]

# Sector + a one-line blurb per instrument. Powers the fundamentals panel and
# the "similar stocks" suggestions (same-sector peers).
SECTOR_MAP = {
    "AAPL": ("Technology", "Consumer electronics, software and services — the iPhone company."),
    "MSFT": ("Technology", "Cloud, enterprise software and the Windows/Office franchise."),
    "NVDA": ("Technology", "GPUs, AI accelerators and datacenter compute."),
    "AMD": ("Technology", "CPUs, GPUs and adaptive silicon for computing."),
    "INTC": ("Technology", "Semiconductor manufacturing and x86 processors."),
    "ORCL": ("Technology", "Enterprise databases and cloud infrastructure."),
    "CRM": ("Technology", "Customer relationship management software."),
    "TSLA": ("Automotive", "Electric vehicles, energy storage and autonomy software."),
    "AMZN": ("Consumer", "E-commerce, cloud (AWS), logistics and devices."),
    "WMT": ("Consumer", "Global retail and grocery at scale."),
    "DIS": ("Consumer", "Media, streaming, parks and franchises."),
    "NKE": ("Consumer", "Athletic footwear and apparel."),
    "KO": ("Consumer", "The world's largest non-alcoholic beverage system."),
    "PEP": ("Consumer", "Snacks, food and beverages."),
    "UBER": ("Consumer", "Ride-hailing, delivery and mobility platforms."),
    "GOOG": ("Communication", "Search, advertising, YouTube and Android."),
    "META": ("Communication", "Social platforms — Facebook, Instagram, WhatsApp."),
    "NFLX": ("Communication", "Streaming entertainment and original content."),
    "JPM": ("Finance", "Global investment and consumer banking."),
    "V": ("Finance", "Payments network connecting merchants and issuers."),
    "BA": ("Industrials", "Commercial aerospace and defense."),
    "XOM": ("Energy", "Integrated oil, gas and petrochemicals."),
}


def seed_instruments(db: Session) -> None:
    for row in INSTRUMENTS:
        if not db.query(Stock).filter(Stock.symbol == row["symbol"]).first():
            db.add(Stock(**row))
    db.commit()


def seed_profiles(db: Session) -> None:
    """Profiles + 5-year financials + dividend yield, derived deterministically
    from each symbol's seed (same spirit as the price walk). Idempotent: existing
    rows are kept, and rows missing a dividend yield (pre-Nov-25 schema) get one."""
    from .models import StockFinancial, StockProfile

    for row in INSTRUMENTS:
        symbol = row["symbol"]

        # Dedicated RNG so the yield is identical whether creating or patching.
        yield_rng = random.Random(row["seed"] * 13 + 5)
        div_yield = round(yield_rng.uniform(0.5, 3.5), 2)

        existing = db.get(StockProfile, symbol)
        if existing:
            if existing.dividend_yield == 0.0:
                existing.dividend_yield = div_yield
                db.commit()
            continue

        sector, blurb = SECTOR_MAP[symbol]
        rng = random.Random(row["seed"] * 7 + 1)

        eps = round(row["base_price"] / rng.uniform(16, 30), 2)
        shares = rng.randint(1_500_000_000, 12_000_000_000)
        high = round(row["base_price"] * rng.uniform(1.15, 1.60), 2)
        low = round(row["base_price"] * rng.uniform(0.55, 0.85), 2)
        founded = rng.randint(1900, 2015)

        db.add(
            StockProfile(
                symbol=symbol, description=blurb, sector=sector, eps=eps,
                shares_outstanding=shares, dividend_yield=div_yield,
                fifty_two_week_high=high,
                fifty_two_week_low=low, founded_year=founded,
            )
        )
        for year in range(2021, 2026):
            frng = random.Random(row["seed"] * 100 + year)
            revenue = round(frng.uniform(20, 90) * (1.09 ** (year - 2021)), 2)
            net_profit = round(revenue * frng.uniform(0.08, 0.30), 2)
            db.add(StockFinancial(symbol=symbol, year=year, revenue=revenue, net_profit=net_profit))
    db.commit()


def _reset_user_rows(db: Session, email: str) -> None:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return
    # FK-safe order: cash txns reference orders (order_id), so they go first.
    db.query(CashTransaction).filter(CashTransaction.user_id == user.id).delete()
    db.query(Order).filter(Order.user_id == user.id).delete()
    db.query(Holding).filter(Holding.user_id == user.id).delete()
    db.query(RulesConfig).filter(RulesConfig.user_id == user.id).delete()
    db.query(SessionRow).filter(SessionRow.user_id == user.id).delete()
    db.query(WatchlistItem).filter(WatchlistItem.user_id == user.id).delete()
    db.query(User).filter(User.id == user.id).delete()
    db.commit()


def _same_day(at: datetime, day_floor: datetime) -> datetime:
    """Clamp a timestamp so it never falls before today's start.

    The midnight gotcha (DESIGN.md §6.6): seeding 'N minutes ago' just after
    00:00 puts those events on yesterday. Clamping keeps every persona's
    narrative inside the current day, so 'today's trades' is always what the
    guardrails expect. Re-seeding before demos remains good practice."""
    return max(at, day_floor)


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

    # 9 sells today, net -9,700: six panic dumps @ 254.50 (-1,655 each = -9,930),
    # then three small winners @ 425/430/428 (+230). The trailing winners matter:
    # they break the 3-straight-losses streak, so the cooldown is NOT active and
    # the 10th trade reaches the kill switch (DESIGN §3.4 check order).
    # Cash check: 58,000 + 6x2,545 + 4,250 + 4,300 + 4,280 = 86,100.
    day_floor = datetime.combine(now.date(), datetime.min.time()) + timedelta(minutes=1)
    sell_prices = [254.50] * 6 + [425.00, 430.00, 428.00]
    for i, price in enumerate(sell_prices):
        pnl = 10 * (price - 420.0)
        qty_delta = 10 * price
        cash += qty_delta
        at = _same_day(now - timedelta(minutes=[95, 88, 80, 70, 60, 45, 30, 20, 10][i]), day_floor)
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

    day_floor = datetime.combine(now.date(), datetime.min.time()) + timedelta(minutes=1)
    for i, minutes_ago in enumerate([20, 12, 5]):
        price = 252.0  # 10 x (252 - 300) = -480 per sell
        pnl = 10 * (price - 300.0)
        cash += 10 * price
        at = _same_day(now - timedelta(minutes=minutes_ago), day_floor)
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
    ensure_schema(engine)              # patch any columns added after this DB shipped

    db = SessionLocal()
    try:
        if not args.personas_only:
            seed_instruments(db)
            seed_profiles(db)
            seed_admins(db)
        seed_fresh(db)
        seed_tilted(db)
        seed_cooldown(db)
        print("Seed complete. Personas: fresh@demo / tilted@demo / cooldown@demo (password: demo1234)")
    finally:
        db.close()


if __name__ == "__main__":
    main()
