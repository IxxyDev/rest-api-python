from __future__ import annotations

import math

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.models.entities import Activity, Building, Organization


async def list_organizations_for_building(
    session: AsyncSession,
    building_id: int,
    activity_id: int | None,
) -> list[Organization]:
    await _ensure_building_exists(session, building_id)
    stmt: Select[Organization] = (
        select(Organization)
        .options(
            selectinload(Organization.building),
            selectinload(Organization.phones),
            selectinload(Organization.activities),
        )
        .where(Organization.building_id == building_id)
        .order_by(Organization.name.asc())
    )

    if activity_id is not None:
        descendant_ids = await _collect_activity_branch(session, activity_id)
        stmt = stmt.where(
            Organization.activities.any(Activity.id.in_(descendant_ids))
        )

    result = await session.scalars(stmt)
    return list(result)


async def search_organizations(
    session: AsyncSession,
    *,
    lat: float | None = None,
    lon: float | None = None,
    radius_km: float | None = None,
    min_lat: float | None = None,
    max_lat: float | None = None,
    min_lon: float | None = None,
    max_lon: float | None = None,
    query: str | None = None,
    activity_id: int | None = None,
) -> list[Organization]:
    stmt: Select[Organization] = select(Organization).options(
        selectinload(Organization.building),
        selectinload(Organization.phones),
        selectinload(Organization.activities),
    )

    filters = []
    if activity_id is not None:
        descendant_ids = await _collect_activity_branch(session, activity_id)
        filters.append(Organization.activities.any(Activity.id.in_(descendant_ids)))
    if query:
        filters.append(Organization.name.ilike(f"%{query}%"))

    if filters:
        stmt = stmt.where(*filters)

    result = await session.scalars(stmt)
    organizations = list(result)

    filtered = [
        org
        for org in organizations
        if _match_geo_filters(org, lat, lon, radius_km, min_lat, max_lat, min_lon, max_lon)
    ]
    filtered.sort(key=lambda o: o.name)
    return filtered


async def _ensure_building_exists(session: AsyncSession, building_id: int) -> None:
    exists_stmt = select(Building.id).where(Building.id == building_id)
    exists = await session.scalar(exists_stmt)
    if exists is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Building not found")


async def _collect_activity_branch(session: AsyncSession, activity_id: int) -> set[int]:
    exists_stmt = select(Activity.id).where(Activity.id == activity_id)
    base_activity = await session.scalar(exists_stmt)
    if base_activity is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Activity not found")

    collected: set[int] = {activity_id}
    frontier: set[int] = {activity_id}

    while frontier:
        children_stmt = select(Activity.id).where(Activity.parent_id.in_(frontier))
        rows = await session.scalars(children_stmt)
        child_ids = set(rows.all())
        new_ids = child_ids.difference(collected)
        if not new_ids:
            break
        collected.update(new_ids)
        frontier = new_ids

    return collected


def serialize_organization(org: Organization) -> dict:
    building = org.building
    phones = [phone.phone for phone in sorted(org.phones, key=lambda p: p.phone)]
    activities = [
        {
            "id": activity.id,
            "name": activity.name,
            "level": activity.level,
            "parent_id": activity.parent_id,
        }
        for activity in sorted(
            org.activities,
            key=lambda a: (a.level, a.name),
        )
    ]
    return {
        "id": org.id,
        "name": org.name,
        "phones": phones,
        "building": {
            "id": building.id,
            "city": building.city,
            "address": building.address,
            "location": {"lat": building.latitude, "lon": building.longitude},
        },
        "activities": activities,
    }


async def get_organization_detail(
    session: AsyncSession,
    organization_id: int,
) -> Organization:
    stmt = (
        select(Organization)
        .options(
            selectinload(Organization.building),
            selectinload(Organization.phones),
            selectinload(Organization.activities),
        )
        .where(Organization.id == organization_id)
    )
    organization = await session.scalar(stmt)
    if organization is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Organization not found")
    return organization


def _match_geo_filters(
    org: Organization,
    lat: float | None,
    lon: float | None,
    radius_km: float | None,
    min_lat: float | None,
    max_lat: float | None,
    min_lon: float | None,
    max_lon: float | None,
) -> bool:
    building = org.building
    if min_lat is not None and building.latitude < min_lat:
        return False
    if max_lat is not None and building.latitude > max_lat:
        return False
    if min_lon is not None and building.longitude < min_lon:
        return False
    if max_lon is not None and building.longitude > max_lon:
        return False

    if lat is not None and lon is not None and radius_km is not None:
        distance = _haversine_km(lat, lon, building.latitude, building.longitude)
        if distance > radius_km:
            return False

    return True


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c
