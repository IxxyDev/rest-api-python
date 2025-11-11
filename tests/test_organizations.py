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


async def test_filter_organizations_by_activity(
    async_client: AsyncClient,
    seed_dataset: SeedDataset,
) -> None:
    response = await async_client.get(
        "/api/v1/organizations",
        params={
            "building_id": seed_dataset.primary_building_id,
            "activity_id": seed_dataset.food_activity_id,
        },
    )
    assert response.status_code == 200
    payload = response.json()

    assert payload["total"] == 1
    assert payload["items"][0]["name"] == "ООО Рога и Копыта"
    assert payload["items"][0]["activities"][0]["id"] == seed_dataset.meat_activity_id


async def test_search_organizations_within_radius(
    async_client: AsyncClient,
    seed_dataset: SeedDataset,
) -> None:
    response = await async_client.get(
        "/api/v1/organizations/search",
        params={
            "lat": 55.751,
            "lon": 37.618,
            "radius_km": 3,
        },
    )
    assert response.status_code == 200
    payload = response.json()

    assert payload["total"] == 3
    names = [item["name"] for item in payload["items"]]
    assert "ООО Северный Ветер" not in names
    assert "ООО Рога и Копыта" in names
    assert "ООО АвтоМир" in names


async def test_search_organizations_in_bbox(
    async_client: AsyncClient,
    seed_dataset: SeedDataset,
) -> None:
    response = await async_client.get(
        "/api/v1/organizations/search",
        params={
            "min_lat": 55.70,
            "max_lat": 55.77,
            "min_lon": 37.59,
            "max_lon": 37.63,
        },
    )
    assert response.status_code == 200
    payload = response.json()

    assert payload["total"] == 2
    names = [item["name"] for item in payload["items"]]
    assert names == ["ООО АвтоМир", "ООО Рога и Копыта"]


async def test_get_organization_detail(
    async_client: AsyncClient,
    seed_dataset: SeedDataset,
) -> None:
    response = await async_client.get(f"/api/v1/organizations/{seed_dataset.meat_org_id}")
    assert response.status_code == 200
    payload = response.json()

    assert payload["name"] == "ООО Рога и Копыта"
    assert payload["building"]["address"] == "Ленинский проспект, 10"
    assert payload["phones"] == ["+7-495-111-2233", "+7-495-111-4455"]
    assert payload["activities"][0]["name"] == "Мясная продукция"


async def test_get_organization_detail_not_found(
    async_client: AsyncClient,
) -> None:
    response = await async_client.get("/api/v1/organizations/999999")
    assert response.status_code == 404


async def test_search_organizations_by_name(
    async_client: AsyncClient,
) -> None:
    response = await async_client.get(
        "/api/v1/organizations/search",
        params={"query": "Рога"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["name"] == "ООО Рога и Копыта"


async def test_global_activity_search_returns_descendants(
    async_client: AsyncClient,
    seed_dataset: SeedDataset,
) -> None:
    response = await async_client.get(
        "/api/v1/organizations/search",
        params={"activity_id": seed_dataset.food_activity_id},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 2
    names = [item["name"] for item in payload["items"]]
    assert "ООО Рога и Копыта" in names
    assert "ООО Молочная ферма" in names
