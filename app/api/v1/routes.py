from fastapi import APIRouter, Depends

from app.api.deps import get_api_key
from app.api.v1 import organizations, activities

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


@router.get("/health", tags=["health"])
def healthcheck(_: str = Depends(get_api_key)) -> dict[str, str]:
    return {"status": "ok"}
