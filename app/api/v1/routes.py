from fastapi import APIRouter, Depends

from app.api.deps import get_api_key

router = APIRouter()


@router.get("/health", tags=["health"])
def healthcheck(_: str = Depends(get_api_key)) -> dict[str, str]:
    return {"status": "ok"}
