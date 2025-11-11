from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_api_key, get_db_session
from app.services.activities import fetch_activity_tree

router = APIRouter()


@router.get(
    "/tree",
    summary="Получить дерево видов деятельности",
)
async def get_activity_tree(
    max_level: int | None = Query(default=None, ge=1),
    _: str = Depends(get_api_key),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    tree = await fetch_activity_tree(session, max_level=max_level)
    return {"max_level": max_level, "items": tree}
