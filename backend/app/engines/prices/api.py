"""Market data routes: the watchlist and the full per-symbol detail
(quote + candles + 5y history + fundamentals + similar stocks)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...auth.api import get_current_user
from ...core.db import get_db
from ...core.constants import UNKNOWN_SYMBOL
from ...models import StockFinancial, StockProfile
from .engine import price_engine

router = APIRouter(prefix="/stocks", tags=["market"])


@router.get("")
def list_stocks(_user=Depends(get_current_user)):
    return price_engine.list_quotes()


@router.get("/{symbol}")
def stock_detail(symbol: str, _user=Depends(get_current_user), db: Session = Depends(get_db)):
    detail = price_engine.detail(symbol)
    if not detail:
        raise HTTPException(status_code=404, detail=UNKNOWN_SYMBOL)
    symbol = symbol.upper()

    # Fundamentals: profile row + live-derived P/E and market cap (DESIGN.md §3.2b).
    profile = db.get(StockProfile, symbol)
    pe = round(detail["price"] / profile.eps, 2) if profile and profile.eps > 0 else None
    market_cap = profile.shares_outstanding * detail["price"] if profile else None

    financials = (
        db.query(StockFinancial)
        .filter(StockFinancial.symbol == symbol)
        .order_by(StockFinancial.year)
        .all()
        if profile
        else []
    )

    # Similar stocks: same-sector peers with live quotes (the "competitors" row).
    similar = []
    if profile:
        peers = (
            db.query(StockProfile)
            .filter(StockProfile.sector == profile.sector, StockProfile.symbol != symbol)
            .limit(4)
            .all()
        )
        for peer in peers:
            q = price_engine.quote(peer.symbol)
            if q:
                similar.append(q)

    return {
        **detail,
        "profile": (
            {
                "symbol": profile.symbol,
                "description": profile.description,
                "sector": profile.sector,
                "eps": profile.eps,
                "shares_outstanding": profile.shares_outstanding,
                "dividend_yield": profile.dividend_yield,
                "fifty_two_week_high": profile.fifty_two_week_high,
                "fifty_two_week_low": profile.fifty_two_week_low,
                "founded_year": profile.founded_year,
            }
            if profile
            else None
        ),
        "pe": pe,
        "market_cap": market_cap,
        "financials": [
            {"year": f.year, "revenue": f.revenue, "net_profit": f.net_profit} for f in financials
        ],
        "similar": similar,
    }
