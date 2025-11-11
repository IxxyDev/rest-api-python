from httpx import AsyncClient

from tests.factories import SeedDataset


async def test_activity_tree_until_level_three(
    async_client: AsyncClient,
    seed_dataset: SeedDataset,
) -> None:
    response = await async_client.get(
        "/api/v1/activities/tree",
        params={"max_level": 3},
    )
    assert response.status_code == 200
    payload = response.json()

    assert payload["max_level"] == 3
    assert len(payload["items"]) == 3

    food_branch = next(item for item in payload["items"] if item["id"] == seed_dataset.food_activity_id)
    assert food_branch["name"] == "Продукты питания"
    assert len(food_branch["children"]) == 2

    meat = next(child for child in food_branch["children"] if child["id"] == seed_dataset.meat_activity_id)
    assert meat["children"] == []

    logistics = next(item for item in payload["items"] if item["id"] == seed_dataset.logistics_activity_id)
    assert len(logistics["children"]) == 1
    assert logistics["children"][0]["children"][0]["name"] == "Холодильные склады"
