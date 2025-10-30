"""Database utilities."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ..config import get_settings
from ..logging import get_logger
from .models import Base

logger = get_logger(__name__)


def _build_async_dsn(dsn: str) -> str:
    if dsn.startswith("postgresql+") and "psycopg" in dsn and "asyncpg" not in dsn:
        return dsn.replace("psycopg", "asyncpg")
    if dsn.startswith("postgresql://"):
        return dsn.replace("postgresql://", "postgresql+asyncpg://")
    return dsn


_settings = get_settings()
_engine = create_async_engine(_build_async_dsn(_settings.postgres_dsn), echo=False, future=True)
_session_factory = async_sessionmaker(_engine, expire_on_commit=False)


@asynccontextmanager
async def session_scope() -> AsyncIterator[AsyncSession]:
    session = _session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def init_db() -> None:
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("database_initialized")


__all__ = ["session_scope", "init_db", "_session_factory", "_engine"]
