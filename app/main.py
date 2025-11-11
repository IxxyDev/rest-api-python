from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


settings = get_settings()
tags_metadata = [
    {
        "name": "health",
        "description": "Проверка готовности API ключа и приложения.",
    },
    {
        "name": "organizations",
        "description": "Список, фильтрация, поиск и карточки организаций.",
    },
    {
        "name": "activities",
        "description": "Дерево видов деятельности с вложенностью до требуемого уровня.",
    },
    {
        "name": "tasks",
        "description": "Задачи, привязанные к зданиям справочника.",
    },
]
app = FastAPI(
    title=settings.project_name,
    version=settings.api_version,
    description="REST API для справочника зданий, организаций и видов деятельности.",
    debug=settings.debug,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)
app.include_router(api_router)
