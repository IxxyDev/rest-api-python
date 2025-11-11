from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings


class Base(DeclarativeBase):
    pass
def _make_engine() -> AsyncEngine:
    settings = get_settings()
    return create_async_engine(settings.database_url, echo=settings.debug)


engine = _make_engine()
AsyncSessionFactory = async_sessionmaker(engine, expire_on_commit=False)


def reset_engine() -> None:
    global engine, AsyncSessionFactory
    engine = _make_engine()
    AsyncSessionFactory = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionFactory() as session:
        yield session
