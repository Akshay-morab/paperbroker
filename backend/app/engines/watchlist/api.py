"""The per-user watchlist: starred shares with live quotes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...auth.api import get_current_user
from ...core.constants import UNKNOWN_SYMBOL
from ...core.db import get_db
from ...models import User, WatchlistItem
from ..prices.engine import price_engine

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


@router.get("")
def get_watchlist(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.query(WatchlistItem).filter(WatchlistItem.user_id == user.id).all()
    out = []
    for item in items:
        quote = price_engine.quote(item.symbol)
        if quote:
            out.append(quote)
    return out


@router.post("/{symbol}", status_code=201)
def add_to_watchlist(symbol: str, user: User = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    symbol = symbol.upper()
    if not price_engine.quote(symbol):
        raise HTTPException(status_code=404, detail=UNKNOWN_SYMBOL)
    exists = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == user.id, WatchlistItem.symbol == symbol
    ).first()
    if not exists:
        db.add(WatchlistItem(user_id=user.id, symbol=symbol))
        db.commit()
    return {"ok": True, "symbol": symbol, "starred": True}


@router.delete("/{symbol}")
def remove_from_watchlist(symbol: str, user: User = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    symbol = symbol.upper()
    db.query(WatchlistItem).filter(
        WatchlistItem.user_id == user.id, WatchlistItem.symbol == symbol
    ).delete()
    db.commit()
    return {"ok": True, "symbol": symbol, "starred": False}
