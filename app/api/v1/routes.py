from fastapi import APIRouter, Depends

from app.api.deps import get_api_key
from app.api.v1 import organizations, activities, tasks, buildings

router = APIRouter()
router.include_router(
    organizations.router,
    prefix="/organizations",
    tags=["organizations"],
)
router.include_router(
    activities.router,
    prefix="/activities",
    tags=["activities"],
)
router.include_router(
    tasks.router,
    prefix="/tasks",
    tags=["tasks"],
)
router.include_router(
    buildings.router,
    prefix="/buildings",
    tags=["buildings"],
)


@router.get("/health", tags=["health"], summary="Проверить доступность API")
def healthcheck(_: str = Depends(get_api_key)) -> dict[str, str]:
    return {"status": "ok"}
