"""FastAPI app: mounts routers, creates tables, boots the price tick loop."""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .auth.api import me_router, router as auth_router
from .core.db import Base, SessionLocal, engine
from .engines.ledger.api import router as portfolio_router
from .engines.orders.api import router as orders_router
from .engines.prices.api import router as stocks_router
from .engines.prices.engine import price_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        price_engine.load_from_db(db)
    tick_task = asyncio.create_task(price_engine.tick_loop())
    yield
    tick_task.cancel()


app = FastAPI(title="PaperBroker API", version="0.1.0", lifespan=lifespan)

app.include_router(auth_router, prefix="/api")
app.include_router(me_router, prefix="/api")
app.include_router(stocks_router, prefix="/api")
app.include_router(orders_router, prefix="/api")
app.include_router(portfolio_router, prefix="/api")
