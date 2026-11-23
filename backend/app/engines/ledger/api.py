"""Ledger routes: the portfolio view — cash, positions with live P&L, equity."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...auth.api import get_current_user
from ...core.db import get_db
from ...models import User
from . import service

router = APIRouter(prefix="/portfolio", tags=["ledger"])


@router.get("")
def get_portfolio(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return service.portfolio(db, user.id)
