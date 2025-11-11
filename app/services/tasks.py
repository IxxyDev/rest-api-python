from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.entities import Building, Task


async def list_tasks_for_building(
    session: AsyncSession,
    building_id: int,
) -> list[Task]:
    exists_stmt = select(Building.id).where(Building.id == building_id)
    exists = await session.scalar(exists_stmt)
    if exists is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Building not found")

    stmt = (
        select(Task)
        .options(selectinload(Task.building))
        .where(Task.building_id == building_id)
        .order_by(Task.title.asc())
    )
    tasks = await session.scalars(stmt)
    return list(tasks)


def serialize_task(task: Task) -> dict:
    building = task.building
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "building": {
            "id": building.id,
            "city": building.city,
            "address": building.address,
            "location": {"lat": building.latitude, "lon": building.longitude},
        },
    }
