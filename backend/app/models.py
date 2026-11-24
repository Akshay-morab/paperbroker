"""SQLAlchemy models — the single source of truth for the schema (DESIGN.md §4).

Phase-2 tables (stock_profiles, stock_financials, change_requests) are
deliberately absent per the solo re-baseline (§8.1); they are additive later.
"""

from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    PrimaryKeyConstraint,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from .core.constants import (
    COOLDOWN_MINUTES,
    DAILY_LOSS_LIMIT,
    LOSS_STREAK_TRIGGER,
    MAX_OPEN_POSITIONS,
    MAX_POSITION_PCT,
    MAX_TRADES_PER_DAY,
)
from .core.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="trader")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)


class Session(Base):
    __tablename__ = "sessions"

    token: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class Stock(Base):
    __tablename__ = "stocks"

    symbol: Mapped[str] = mapped_column(String(12), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    base_price: Mapped[float] = mapped_column(Float, nullable=False)
    volatility: Mapped[float] = mapped_column(Float, nullable=False, default=0.02)
    seed: Mapped[int] = mapped_column(Integer, nullable=False)


class StockProfile(Base):
    """1:1 content data for the detail page (DESIGN.md §3.2b — landed Nov 25)."""

    __tablename__ = "stock_profiles"

    symbol: Mapped[str] = mapped_column(String(12), ForeignKey("stocks.symbol"), primary_key=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    sector: Mapped[str] = mapped_column(String(60), nullable=False)
    eps: Mapped[float] = mapped_column(Float, nullable=False)  # annual EPS; P/E derived live
    shares_outstanding: Mapped[int] = mapped_column(Integer, nullable=False)
    fifty_two_week_high: Mapped[float] = mapped_column(Float, nullable=False)
    fifty_two_week_low: Mapped[float] = mapped_column(Float, nullable=False)
    founded_year: Mapped[int | None] = mapped_column(Integer, nullable=True)


class StockFinancial(Base):
    """Yearly financials -> the 5-year revenue/profit bars (DESIGN.md §3.2b)."""

    __tablename__ = "stock_financials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(12), ForeignKey("stocks.symbol"), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    revenue: Mapped[float] = mapped_column(Float, nullable=False)
    net_profit: Mapped[float] = mapped_column(Float, nullable=False)


class RulesConfig(Base):
    __tablename__ = "rules_config"

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)
    daily_loss_limit: Mapped[float] = mapped_column(Float, nullable=False, default=DAILY_LOSS_LIMIT)
    max_trades_per_day: Mapped[int] = mapped_column(Integer, nullable=False, default=MAX_TRADES_PER_DAY)
    cooldown_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=COOLDOWN_MINUTES)
    loss_streak_trigger: Mapped[int] = mapped_column(Integer, nullable=False, default=LOSS_STREAK_TRIGGER)
    max_position_pct: Mapped[float] = mapped_column(Float, nullable=False, default=MAX_POSITION_PCT)
    max_open_positions: Mapped[int] = mapped_column(Integer, nullable=False, default=MAX_OPEN_POSITIONS)


class Holding(Base):
    __tablename__ = "holdings"
    __table_args__ = (PrimaryKeyConstraint("user_id", "symbol"),)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    symbol: Mapped[str] = mapped_column(String(12), ForeignKey("stocks.symbol"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_cost: Mapped[float] = mapped_column(Float, nullable=False)


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    symbol: Mapped[str] = mapped_column(String(12), ForeignKey("stocks.symbol"), nullable=False)
    side: Mapped[str] = mapped_column(String(4), nullable=False)  # 'buy' | 'sell'
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    order_type: Mapped[str] = mapped_column(String(10), nullable=False, default="market")
    limit_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(12), nullable=False)  # filled|blocked|rejected|open|cancelled
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    filled_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    realized_pnl: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)


Index("idx_orders_user_day", Order.user_id, Order.created_at)


class CashTransaction(Base):
    __tablename__ = "cash_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)  # signed
    kind: Mapped[str] = mapped_column(String(20), nullable=False)  # signup_credit | buy | sell
    order_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("orders.id"), nullable=True)
    balance_after: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
