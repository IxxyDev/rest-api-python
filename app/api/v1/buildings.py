from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_api_key, get_db_session
from app.services.buildings import list_buildings, serialize_building

router = APIRouter()


@router.get("", summary="Список зданий справочника")
async def get_buildings(
    _: str = Depends(get_api_key),
    session: AsyncSession = Depends(get_db_session),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> dict:
    buildings = await list_buildings(session, limit=limit, offset=offset)
    items = [serialize_building(building) for building in buildings]
    return {"total": len(items), "items": items, "limit": limit, "offset": offset}
