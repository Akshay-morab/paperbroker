"""Auth core: bcrypt passwords, server-side sessions, the $100k signup credit."""

import uuid
from datetime import datetime, timedelta

import bcrypt
from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..core.config import starting_cash
from ..core.constants import EMAIL_ALREADY_REGISTERED, INVALID_CREDENTIALS
from ..models import CashTransaction, RulesConfig, Session as SessionRow, User


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except ValueError:
        return False


def signup(db: Session, email: str, password: str) -> User:
    email = (email or "").strip().lower()
    if "@" not in email or len(password or "") < 8:
        raise HTTPException(status_code=422, detail="invalid email or password")
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail=EMAIL_ALREADY_REGISTERED)

    user = User(email=email, password_hash=hash_password(password))
    db.add(user)
    db.flush()  # get user.id without committing

    db.add(RulesConfig(user_id=user.id))

    cash = round(starting_cash(), 2)
    db.add(
        CashTransaction(
            user_id=user.id,
            amount=cash,
            kind="signup_credit",
            balance_after=cash,
        )
    )
    db.commit()
    db.refresh(user)
    return user


def login(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email.strip().lower()).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail=INVALID_CREDENTIALS)
    return user


def create_session(db: Session, user: User) -> str:
    token = uuid.uuid4().hex
    db.add(SessionRow(token=token, user_id=user.id, expires_at=datetime.now() + timedelta(hours=24)))
    db.commit()
    return token


def destroy_session(db: Session, token: str) -> None:
    row = db.query(SessionRow).filter(SessionRow.token == token).first()
    if row:
        db.delete(row)
        db.commit()


def user_from_token(db: Session, token: str | None) -> User | None:
    if not token:
        return None
    row = db.query(SessionRow).filter(SessionRow.token == token).first()
    if not row or row.expires_at < datetime.now():
        return None
    return db.get(User, row.user_id)
