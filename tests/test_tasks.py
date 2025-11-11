from httpx import AsyncClient

from tests.factories import SeedDataset


async def test_list_tasks_for_building(
    async_client: AsyncClient,
    seed_dataset: SeedDataset,
) -> None:
    response = await async_client.get(
        "/api/v1/tasks",
        params={"building_id": seed_dataset.primary_building_id},
    )
    assert response.status_code == 200
    payload = response.json()

    assert payload["total"] == 2
    titles = [task["title"] for task in payload["items"]]
    assert titles == [
        "Проверка вентиляции",
        "Проверка пожарной сигнализации",
    ]

    first_task = payload["items"][0]
    assert first_task["building"]["id"] == seed_dataset.primary_building_id
    assert first_task["building"]["city"] == "Москва"
    assert first_task["building"]["address"] == "Ленинский проспект, 10"
    assert first_task["building"]["location"]["lat"] == 55.751244
    assert first_task["building"]["location"]["lon"] == 37.618423
