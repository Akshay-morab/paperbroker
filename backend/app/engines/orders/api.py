"""Order routes: place + history.

Contract (DESIGN.md §5):
  201 filled  -> {order}
  400 rejected -> {"status": "rejected", "reason": "<exact string>"}
  403 blocked  -> {"status": "blocked",  "reason": "<exact string>"}   (rules land Wed)
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ...auth.api import get_current_user
from ...core.db import get_db
from ...models import User
from . import service

router = APIRouter(prefix="/orders", tags=["orders"])


def _order_out(order) -> dict:
    return {
        "id": order.id,
        "symbol": order.symbol,
        "side": order.side,
        "quantity": order.quantity,
        "order_type": order.order_type,
        "status": order.status,
        "reason": order.reason,
        "filled_price": order.filled_price,
        "realized_pnl": order.realized_pnl,
        "created_at": order.created_at.isoformat(),
    }


@router.post("", status_code=201)
def place_order(payload: dict, user: User = Depends(get_current_user),
               db: Session = Depends(get_db)):
    quantity = (payload or {}).get("quantity")
    if isinstance(quantity, float) and quantity.is_integer():
        quantity = int(quantity)  # treat 10.0 as 10 — Kane and forms both send this
    order = service.place_order(
        db, user, (payload or {}).get("symbol", ""), (payload or {}).get("side", ""), quantity
    )

    if order.status == "rejected":
        return JSONResponse(
            status_code=400, content={"status": "rejected", "reason": order.reason}
        )
    if order.status == "blocked":
        return JSONResponse(
            status_code=403, content={"status": "blocked", "reason": order.reason}
        )
    return _order_out(order)


@router.get("")
def order_history(limit: int = 50, user: User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    return [_order_out(o) for o in service.order_history(db, user.id, limit=min(limit, 200))]
