from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Activity


async def fetch_activity_tree(
    session: AsyncSession,
    *,
    max_level: int | None = None,
) -> list[dict]:
    stmt = select(Activity).order_by(Activity.level.asc(), Activity.name.asc())
    if max_level is not None:
        stmt = stmt.where(Activity.level <= max_level)

    rows = (await session.scalars(stmt)).all()
    by_id: dict[int, dict] = {}
    roots: list[dict] = []

    for activity in rows:
        node = {
            "id": activity.id,
            "name": activity.name,
            "level": activity.level,
            "parent_id": activity.parent_id,
            "children": [],
        }
        by_id[activity.id] = node

    for activity in rows:
        node = by_id[activity.id]
        if activity.parent_id is None:
            roots.append(node)
            continue
        parent = by_id.get(activity.parent_id)
        if parent is not None:
            parent["children"].append(node)

    for node in by_id.values():
        node["children"].sort(key=lambda child: child["name"])

    roots.sort(key=lambda item: item["name"])
    return roots
