from __future__ import annotations

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
