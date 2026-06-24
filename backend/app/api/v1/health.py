from fastapi import APIRouter, Depends, status
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException

from app.api.dependencies import get_db, get_redis_client

router = APIRouter(tags=["health"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health(
    session: AsyncSession = Depends(get_db),
    redis_client: Redis = Depends(get_redis_client),
) -> dict[str, str]:
    try:
        await session.execute(text("SELECT 1"))
        await redis_client.ping()
    except Exception as exc:  # pragma: no cover - depends on external services
        raise HTTPException(status_code=503, detail="Health check failed") from exc
    return {"status": "ok", "db": "ok", "cache": "ok"}
