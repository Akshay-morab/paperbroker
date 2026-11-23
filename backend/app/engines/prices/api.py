"""Market data routes: the watchlist and per-symbol quotes+candles."""

from fastapi import APIRouter, Depends, HTTPException

from ...auth.api import get_current_user
from ...core.constants import UNKNOWN_SYMBOL
from .engine import price_engine

router = APIRouter(prefix="/stocks", tags=["market"])


@router.get("")
def list_stocks(_user=Depends(get_current_user)):
    return price_engine.list_quotes()


@router.get("/{symbol}")
def stock_detail(symbol: str, _user=Depends(get_current_user)):
    detail = price_engine.detail(symbol)
    if not detail:
        raise HTTPException(status_code=404, detail=UNKNOWN_SYMBOL)
    return detail
