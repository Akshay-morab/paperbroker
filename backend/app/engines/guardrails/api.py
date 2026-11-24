"""Discipline status for the Discipline page + admin persona reset."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...auth.api import get_current_user
from ...core.db import get_db
from ...models import User
from ...seed import seed_cooldown, seed_fresh, seed_tilted
from . import state

router = APIRouter(prefix="/guardrails", tags=["guardrails"])
admin_router = APIRouter(prefix="/admin", tags=["admin"])


def status_view(db: Session, user: User) -> dict:
    rules = state.rules_for(db, user.id)
    gstate = state.derive(db, user.id, rules)
    now = gstate["now"]

    kill_switch_locked = gstate["realized_today"] <= -rules.daily_loss_limit
    cooldown_until = gstate["cooldown_until"]
    cooldown_active = bool(cooldown_until and now < cooldown_until)
    locked = kill_switch_locked or cooldown_active

    lock_reason = None
    if kill_switch_locked:
        lock_reason = "Trading locked until tomorrow."
    elif cooldown_active:
        seconds = int((cooldown_until - now).total_seconds()) + 1
        mm, ss = divmod(seconds, 60)
        lock_reason = f"Cooldown active — try again in {mm}:{ss:02d}."

    return {
        "locked": locked,
        "lock_reason": lock_reason,
        "state": {
            "realized_today": gstate["realized_today"],
            "trades_used": gstate["trades_used"],
            "open_positions": gstate["open_positions"],
            "equity": gstate["equity"],
        },
        "daily_loss": {
            "used": gstate["realized_today"],
            "limit": rules.daily_loss_limit,
            "remaining": round(rules.daily_loss_limit + gstate["realized_today"], 2),
        },
        "trade_cap": {"used": gstate["trades_used"], "limit": rules.max_trades_per_day},
        "cooldown": {
            "active": cooldown_active,
            "until": cooldown_until.isoformat() if cooldown_until else None,
        },
        "position_size_pct": int(rules.max_position_pct * 100),
        "open_positions_limit": rules.max_open_positions,
    }


@router.get("/status")
def guardrail_status(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return status_view(db, user)


@admin_router.post("/reset-personas")
def reset_personas(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="admin only")
    seed_fresh(db)
    seed_tilted(db)
    seed_cooldown(db)
    return {"ok": True, "personas": ["fresh@demo", "tilted@demo", "cooldown@demo"]}
