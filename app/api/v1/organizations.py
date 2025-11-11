from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_api_key, get_db_session
from app.services.organizations import list_organizations_for_building, serialize_organization

router = APIRouter()


@router.get("")
async def list_organizations(
    building_id: int = Query(..., gt=0),
    activity_id: int | None = Query(default=None, gt=0),
    _: str = Depends(get_api_key),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    organizations = await list_organizations_for_building(session, building_id, activity_id)
    items = [serialize_organization(org) for org in organizations]
    return {"total": len(items), "items": items}
