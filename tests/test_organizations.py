from httpx import AsyncClient
import pytest

from tests.factories import SeedDataset


async def test_list_organizations_in_building(
    async_client: AsyncClient,
    seed_dataset: SeedDataset,
) -> None:
    response = await async_client.get(
        "/api/v1/organizations",
        params={"building_id": seed_dataset.primary_building_id},
    )
    assert response.status_code == 200
    payload = response.json()

    assert payload["total"] == 2
    names = [item["name"] for item in payload["items"]]
    assert names == ["ООО АвтоМир", "ООО Рога и Копыта"]

    first_item = payload["items"][0]
    assert first_item["building"]["id"] == seed_dataset.primary_building_id
    assert first_item["building"]["city"] == "Москва"
    assert first_item["building"]["address"] == "Ленинский проспект, 10"
    assert first_item["building"]["location"]["lat"] == pytest.approx(55.751244)
    assert first_item["building"]["location"]["lon"] == pytest.approx(37.618423)

    assert first_item["phones"] == ["+7-495-222-0001"]
    assert first_item["activities"] == [
        {"id": seed_dataset.auto_activity_id, "name": "Автомобили", "level": 1, "parent_id": None}
    ]
