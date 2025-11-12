from httpx import AsyncClient

from tests.factories import SeedDataset


async def test_list_buildings(async_client: AsyncClient, seed_dataset: SeedDataset) -> None:
    response = await async_client.get("/api/v1/buildings")
    assert response.status_code == 200
    payload = response.json()

    assert payload["total"] == 3
    names = [item["address"] for item in payload["items"]]
    assert names == [
        "Ленинский проспект, 10",
        "Тверская улица, 15",
        "Невский проспект, 25",
    ]

    first_building = payload["items"][0]
    assert first_building["city"] == "Москва"
    assert first_building["location"]["lat"] == 55.751244
    assert first_building["location"]["lon"] == 37.618423


async def test_buildings_pagination(async_client: AsyncClient, seed_dataset: SeedDataset) -> None:
    response = await async_client.get(
        "/api/v1/buildings",
        params={"limit": 1, "offset": 1},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["address"] == "Тверская улица, 15"
