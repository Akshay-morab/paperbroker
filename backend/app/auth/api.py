"""Auth + /me routes. Sessions ride an httpOnly cookie (Kane's browser is just a user)."""

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..engines.ledger.service import cash_balance
from ..models import RulesConfig, User
from . import service

COOKIE_NAME = "pb_session"
COOKIE_MAX_AGE = 24 * 60 * 60

router = APIRouter(prefix="/auth", tags=["auth"])
me_router = APIRouter(tags=["me"])


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    user = service.user_from_token(db, request.cookies.get(COOKIE_NAME))
    if not user:
        raise HTTPException(status_code=401, detail="not signed in")
    return user


def _profile(db: Session, user: User) -> dict:
    rules = db.query(RulesConfig).filter(RulesConfig.user_id == user.id).first()
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "cash": round(cash_balance(db, user.id), 2),
        "rules": {
            "daily_loss_limit": rules.daily_loss_limit,
            "max_trades_per_day": rules.max_trades_per_day,
            "cooldown_minutes": rules.cooldown_minutes,
            "loss_streak_trigger": rules.loss_streak_trigger,
            "max_position_pct": rules.max_position_pct,
            "max_open_positions": rules.max_open_positions,
        },
    }


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=COOKIE_MAX_AGE,
    )


@router.post("/signup", status_code=201)
def signup(payload: dict, response: Response, db: Session = Depends(get_db)):
    email = (payload or {}).get("email", "")
    password = (payload or {}).get("password", "")
    user = service.signup(db, email, password)
    token = service.create_session(db, user)
    _set_session_cookie(response, token)
    return _profile(db, user)


@router.post("/login")
def login(payload: dict, response: Response, db: Session = Depends(get_db)):
    user = service.login(db, (payload or {}).get("email", ""), (payload or {}).get("password", ""))
    token = service.create_session(db, user)
    _set_session_cookie(response, token)
    return _profile(db, user)


@router.post("/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    service.destroy_session(db, request.cookies.get(COOKIE_NAME))
    response.delete_cookie(COOKIE_NAME)
    return {"ok": True}


@me_router.get("/me")
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _profile(db, user)
