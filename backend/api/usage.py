"""AI-usage accounting that survives restarts, in one small table of the API's own.

Adds a single table (`api_usage_events`) beside the existing ones; the existing tables and
models are untouched. Used for per-account quotas and the daily spending cutoff.
"""

from datetime import datetime, timedelta

from sqlalchemy import Column, DateTime, Integer, String, func

from database.db import Base, engine, get_db


class UsageEvent(Base):
    __tablename__ = "api_usage_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    kind = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


def ensure_table() -> None:
    """Create only this table if it is missing (safe on hosted Postgres too)."""
    UsageEvent.__table__.create(bind=engine, checkfirst=True)


def record(user_id: str, kind: str = "ai") -> None:
    with get_db() as db:
        db.add(UsageEvent(user_id=user_id, kind=kind))


def count_user_since(user_id: str, seconds: int) -> int:
    since = datetime.utcnow() - timedelta(seconds=seconds)
    with get_db() as db:
        return db.query(func.count(UsageEvent.id)).filter(UsageEvent.user_id == user_id, UsageEvent.created_at >= since).scalar() or 0


def count_all_since(seconds: int) -> int:
    since = datetime.utcnow() - timedelta(seconds=seconds)
    with get_db() as db:
        return db.query(func.count(UsageEvent.id)).filter(UsageEvent.created_at >= since).scalar() or 0


def delete_user_events(user_id: str) -> None:
    with get_db() as db:
        db.query(UsageEvent).filter(UsageEvent.user_id == user_id).delete()


def prune_older_than(days: int = 3) -> None:
    cutoff = datetime.utcnow() - timedelta(days=days)
    with get_db() as db:
        db.query(UsageEvent).filter(UsageEvent.created_at < cutoff).delete()
