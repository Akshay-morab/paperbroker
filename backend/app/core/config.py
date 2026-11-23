"""Environment-driven config. Every var is PB_-prefixed and documented in .env.example."""

import os


def db_path() -> str:
    return os.environ.get("PB_DB_PATH", "data/paperbroker.db")


def session_secret() -> str:
    return os.environ.get("PB_SESSION_SECRET", "dev-secret-change-me")


def starting_cash() -> float:
    return float(os.environ.get("PB_STARTING_CASH", "100000"))


def admin_emails() -> list[str]:
    return [e.strip() for e in os.environ.get("PB_ADMIN_EMAILS", "").split(",") if e.strip()]


def admin_password() -> str:
    return os.environ.get("PB_ADMIN_PASSWORD", "")
