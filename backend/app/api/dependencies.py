from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from functools import lru_cache

from fastapi import Depends, HTTPException, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_db_session
from app.providers.base import LLMProvider
from app.providers.factory import build_provider
from app.services.brief_decoder import BriefDecoderService
from app.services.cache import CacheService
from app.services.idempotency import IdempotencyService

logger = logging.getLogger(__name__)


async def get_db() -> AsyncIterator[AsyncSession]:
    async for session in get_db_session():
        yield session


@lru_cache
def get_provider() -> LLMProvider:
    return build_provider(get_settings())


@lru_cache
def get_redis_client() -> Redis:
    settings = get_settings()
    return Redis.from_url(settings.redis_url, decode_responses=True)


def get_cache_service(redis_client: Redis = Depends(get_redis_client)) -> CacheService:
    return CacheService(redis_client, get_settings())


def get_idempotency_service(
    redis_client: Redis = Depends(get_redis_client),
) -> IdempotencyService:
    return IdempotencyService(redis_client, get_settings())


def get_decoder_service(
    session: AsyncSession = Depends(get_db),
    provider: LLMProvider = Depends(get_provider),
    cache_service: CacheService = Depends(get_cache_service),
) -> BriefDecoderService:
    return BriefDecoderService(
        session=session,
        provider=provider,
        cache_service=cache_service,
    )


def get_runtime_settings() -> Settings:
    return get_settings()


async def rate_limit_decode(
    request: Request,
    redis_client: Redis = Depends(get_redis_client),
    settings: Settings = Depends(get_runtime_settings),
) -> None:
    """Per-IP sliding window rate limiter for the decode endpoint.

    Uses Redis INCR + EXPIRE. Falls back gracefully when Redis is unavailable.
    """
    client_ip = request.client.host if request.client else "unknown"
    key = f"rate:decode:{client_ip}"
    try:
        count: int = await redis_client.incr(key)
        if count == 1:
            await redis_client.expire(key, 60)
        if count > settings.rate_limit_per_minute:
            raise HTTPException(
                status_code=429,
                detail={
                    "error_code": "rate_limit_exceeded",
                    "message": "Too many decode requests. Try again in a minute.",
                },
            )
    except HTTPException:
        raise
    except Exception:
        logger.warning("Rate limit Redis unavailable; allowing request through", exc_info=True)
