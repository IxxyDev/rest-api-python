from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_api_key, get_db_session
from app.services.tasks import list_tasks_for_building, serialize_task

router = APIRouter()


@router.get(
    "",
    summary="Задачи, запланированные для здания",
)
async def list_tasks(
    building_id: int = Query(..., gt=0),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    _: str = Depends(get_api_key),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    tasks = await list_tasks_for_building(session, building_id, limit=limit, offset=offset)
    items = [serialize_task(task) for task in tasks]
    return {"total": len(items), "items": items, "limit": limit, "offset": offset}
