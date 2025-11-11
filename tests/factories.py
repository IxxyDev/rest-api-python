from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class SeedDataset:
    primary_building_id: int
    secondary_building_id: int
    meat_org_id: int
    auto_org_id: int
    dairy_org_id: int
    food_activity_id: int
    meat_activity_id: int
    dairy_activity_id: int
    auto_activity_id: int


async def seed_reference_data(session: AsyncSession) -> SeedDataset:
    buildings = [
        {
            "id": 100,
            "city": "Москва",
            "address": "Ленинский проспект, 10",
            "latitude": 55.751244,
            "longitude": 37.618423,
        },
        {
            "id": 200,
            "city": "Москва",
            "address": "Тверская улица, 15",
            "latitude": 55.765140,
            "longitude": 37.605020,
        },
    ]
    for row in buildings:
        await session.execute(
            text(
                """
                INSERT INTO buildings (id, city, address, latitude, longitude)
                VALUES (:id, :city, :address, :latitude, :longitude)
                """
            ),
            row,
        )

    activities = [
        {"id": 10, "name": "Продукты питания", "parent_id": None, "level": 1},
        {"id": 11, "name": "Мясная продукция", "parent_id": 10, "level": 2},
        {"id": 12, "name": "Молочная продукция", "parent_id": 10, "level": 2},
        {"id": 13, "name": "Автомобили", "parent_id": None, "level": 1},
    ]
    for row in activities:
        await session.execute(
            text(
                """
                INSERT INTO activities (id, name, parent_id, level)
                VALUES (:id, :name, :parent_id, :level)
                """
            ),
            row,
        )

    organizations = [
        {"id": 1000, "name": "ООО Рога и Копыта", "building_id": 100},
        {"id": 1001, "name": "ООО АвтоМир", "building_id": 100},
        {"id": 1002, "name": "ООО Молочная ферма", "building_id": 200},
    ]
    for row in organizations:
        await session.execute(
            text(
                """
                INSERT INTO organizations (id, name, building_id)
                VALUES (:id, :name, :building_id)
                """
            ),
            row,
        )

    phones = [
        {"organization_id": 1000, "phone": "+7-495-111-2233"},
        {"organization_id": 1000, "phone": "+7-495-111-4455"},
        {"organization_id": 1001, "phone": "+7-495-222-0001"},
        {"organization_id": 1002, "phone": "+7-495-333-8888"},
    ]
    for row in phones:
        await session.execute(
            text(
                """
                INSERT INTO organization_phones (organization_id, phone)
                VALUES (:organization_id, :phone)
                """
            ),
            row,
        )

    organization_activities = [
        {"organization_id": 1000, "activity_id": 11},
        {"organization_id": 1001, "activity_id": 13},
        {"organization_id": 1002, "activity_id": 12},
    ]
    for row in organization_activities:
        await session.execute(
            text(
                """
                INSERT INTO organization_activities (organization_id, activity_id)
                VALUES (:organization_id, :activity_id)
                """
            ),
            row,
        )

    await session.commit()
    return SeedDataset(
        primary_building_id=100,
        secondary_building_id=200,
        meat_org_id=1000,
        auto_org_id=1001,
        dairy_org_id=1002,
        food_activity_id=10,
        meat_activity_id=11,
        dairy_activity_id=12,
        auto_activity_id=13,
    )
