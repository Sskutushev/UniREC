from __future__ import annotations

import logging
from typing import cast

from redis.asyncio import Redis

from app.core.config import Settings

logger = logging.getLogger(__name__)

_KEY_PREFIX = "idempotency:v1:"


class IdempotencyService:
    """Tracks client-supplied X-Idempotency-Key → run_id mapping in Redis.

    When a client retries a POST /decode with the same key, the original
    run_id is returned instead of triggering a duplicate decode.
    """

    def __init__(self, redis_client: Redis, settings: Settings) -> None:
        self._redis = redis_client
        self._ttl = settings.idempotency_ttl_seconds

    async def get_run_id(self, key: str) -> str | None:
        try:
            raw = await self._redis.get(f"{_KEY_PREFIX}{key}")
            return cast("str | None", raw)
        except Exception:  # pragma: no cover - depends on external service
            logger.warning("Idempotency Redis read failed; treating as cache miss", exc_info=True)
            return None

    async def store_run_id(self, key: str, run_id: str) -> None:
        try:
            await self._redis.set(f"{_KEY_PREFIX}{key}", run_id, ex=self._ttl)
        except Exception:  # pragma: no cover - depends on external service
            logger.warning(
                "Idempotency Redis write failed; key will not be persisted", exc_info=True
            )
