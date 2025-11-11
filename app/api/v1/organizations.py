from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_api_key, get_db_session
from app.services.organizations import (
    list_organizations_for_building,
    search_organizations,
    serialize_organization,
    get_organization_detail,
)

router = APIRouter()


@router.get(
    "",
    summary="Список организаций арендаторов здания",
)
async def list_organizations(
    building_id: int = Query(..., gt=0),
    activity_id: int | None = Query(default=None, gt=0),
    _: str = Depends(get_api_key),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    organizations = await list_organizations_for_building(session, building_id, activity_id)
    items = [serialize_organization(org) for org in organizations]
    return {"total": len(items), "items": items}


@router.get(
    "/search",
    summary="Геопоиск организаций по радиусу или прямоугольнику",
)
async def search_organizations_endpoint(
    lat: float | None = Query(default=None),
    lon: float | None = Query(default=None),
    radius_km: float | None = Query(default=None, gt=0),
    min_lat: float | None = Query(default=None),
    max_lat: float | None = Query(default=None),
    min_lon: float | None = Query(default=None),
    max_lon: float | None = Query(default=None),
    _: str = Depends(get_api_key),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    organizations = await search_organizations(
        session,
        lat=lat,
        lon=lon,
        radius_km=radius_km,
        min_lat=min_lat,
        max_lat=max_lat,
        min_lon=min_lon,
        max_lon=max_lon,
    )
    items = [serialize_organization(org) for org in organizations]
    return {"total": len(items), "items": items}


@router.get(
    "/{organization_id}",
    summary="Карточка организации",
)
async def get_organization(
    organization_id: int,
    _: str = Depends(get_api_key),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    organization = await get_organization_detail(session, organization_id)
    return serialize_organization(organization)
