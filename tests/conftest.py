import os

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import get_settings
from app.db.session import reset_engine
from app.main import app

TEST_API_KEY = "test-api-key"
TEST_DB_URL = "sqlite+aiosqlite:///./test.db"


@pytest.fixture(autouse=True, scope="session")
def configure_settings():
    os.environ["API_KEY"] = TEST_API_KEY
    os.environ["DATABASE_URL"] = TEST_DB_URL
    get_settings.cache_clear()
    reset_engine()
    yield
    get_settings.cache_clear()
    reset_engine()


@pytest.fixture
async def async_client(configure_settings):
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
            headers={"X-API-Key": TEST_API_KEY},
        ) as client:
            yield client
