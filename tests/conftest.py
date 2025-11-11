import os
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import AsyncSessionFactory, engine, reset_engine
from app.main import app
from tests.factories import SeedDataset, seed_reference_data

TEST_API_KEY = "test-api-key"
TEST_DB_URL = "sqlite+aiosqlite:///./test.db"


@pytest.fixture(autouse=True, scope="session")
def configure_settings() -> None:
    os.environ["API_KEY"] = TEST_API_KEY
    os.environ["DATABASE_URL"] = TEST_DB_URL
    get_settings.cache_clear()
    reset_engine()
    yield
    get_settings.cache_clear()
    reset_engine()
    db_path = Path("test.db")
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
async def clean_database(configure_settings: None) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.fixture
async def db_session(clean_database: None) -> AsyncSession:
    async with AsyncSessionFactory() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def seed_dataset(db_session: AsyncSession) -> SeedDataset:
    return await seed_reference_data(db_session)


@pytest.fixture
async def async_client(configure_settings: None) -> AsyncClient:
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
            headers={"X-API-Key": TEST_API_KEY},
        ) as client:
            yield client
