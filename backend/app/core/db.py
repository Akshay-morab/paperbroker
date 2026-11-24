"""SQLite engine + session factory.

The only SQLite-specific code in the app lives here: WAL mode, foreign keys,
and a busy timeout. Business logic never touches pragmas (DESIGN.md §4).
"""

import pathlib

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import db_path


class Base(DeclarativeBase):
    pass


def make_engine():
    path = db_path()
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    eng = create_engine(
        f"sqlite:///{path}",
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(eng, "connect")
    def _set_sqlite_pragma(dbapi_connection, _record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.close()

    return eng


engine = make_engine()
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_schema(eng) -> None:
    """Lightweight migrations. SQLAlchemy's create_all never ALTERs existing
    tables, so columns added after a DB shipped get patched in here.
    Runs after create_all; idempotent."""
    with eng.connect() as conn:
        cols = [row[1] for row in conn.exec_driver_sql("PRAGMA table_info(stock_profiles)")]
        if cols and "dividend_yield" not in cols:
            conn.exec_driver_sql(
                "ALTER TABLE stock_profiles ADD COLUMN dividend_yield REAL NOT NULL DEFAULT 0"
            )
            conn.commit()
