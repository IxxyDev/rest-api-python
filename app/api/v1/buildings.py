from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_api_key, get_db_session
from app.services.buildings import list_buildings, serialize_building

router = APIRouter()


@router.get("", summary="Список зданий справочника")
async def get_buildings(
    _: str = Depends(get_api_key),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    buildings = await list_buildings(session)
    items = [serialize_building(building) for building in buildings]
    return {"total": len(items), "items": items}
