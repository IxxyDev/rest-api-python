from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Building


async def list_buildings(session: AsyncSession, *, limit: int, offset: int) -> list[Building]:
    stmt = (
        select(Building)
        .order_by(Building.city.asc(), Building.address.asc())
        .offset(offset)
        .limit(limit)
    )
    result = await session.scalars(stmt)
    return list(result)


def serialize_building(building: Building) -> dict:
    return {
        "id": building.id,
        "city": building.city,
        "address": building.address,
        "location": {
            "lat": building.latitude,
            "lon": building.longitude,
        },
    }
