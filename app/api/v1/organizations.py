from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
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
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    _: str = Depends(get_api_key),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    organizations = await list_organizations_for_building(
        session,
        building_id,
        activity_id,
        limit=limit,
        offset=offset,
    )
    items = [serialize_organization(org) for org in organizations]
    return {"total": len(items), "items": items, "limit": limit, "offset": offset}


@router.get(
    "/search",
    summary="Геопоиск, глобальный поиск по активности или названию",
)
async def search_organizations_endpoint(
    lat: float | None = Query(default=None),
    lon: float | None = Query(default=None),
    radius_km: float | None = Query(default=None, gt=0),
    min_lat: float | None = Query(default=None),
    max_lat: float | None = Query(default=None),
    min_lon: float | None = Query(default=None),
    max_lon: float | None = Query(default=None),
    query: str | None = Query(default=None, min_length=1),
    activity_id: int | None = Query(default=None, gt=0),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    _: str = Depends(get_api_key),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    _validate_geo_filters(lat, lon, radius_km, min_lat, max_lat, min_lon, max_lon)
    organizations = await search_organizations(
        session,
        lat=lat,
        lon=lon,
        radius_km=radius_km,
        min_lat=min_lat,
        max_lat=max_lat,
        min_lon=min_lon,
        max_lon=max_lon,
        query=query,
        activity_id=activity_id,
        limit=limit,
        offset=offset,
    )
    items = [serialize_organization(org) for org in organizations]
    return {"total": len(items), "items": items, "limit": limit, "offset": offset}


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


def _validate_geo_filters(
    lat: float | None,
    lon: float | None,
    radius_km: float | None,
    min_lat: float | None,
    max_lat: float | None,
    min_lon: float | None,
    max_lon: float | None,
) -> None:
    circle_params = (lat, lon, radius_km)
    provided_circle = [param is not None for param in circle_params]
    if any(provided_circle) and not all(provided_circle):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Для кругового поиска необходимо указать широту, долготу и радиус.",
        )

    bbox_params = (min_lat, max_lat, min_lon, max_lon)
    provided_bbox = [param is not None for param in bbox_params]
    if any(provided_bbox) and not all(provided_bbox):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Для поиска по прямоугольнику нужно передать все четыре координаты.",
        )

    if all(provided_bbox):
        if min_lat > max_lat or min_lon > max_lon:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Минимальные координаты должны быть меньше максимальных.",
            )
