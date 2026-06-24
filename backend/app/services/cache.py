from __future__ import annotations

import hashlib
import json
import logging

from redis.asyncio import Redis

from app.core.config import Settings
from app.domain.schemas import BriefResult

logger = logging.getLogger(__name__)


class CacheService:
    def __init__(self, redis_client: Redis, settings: Settings) -> None:
        self.redis_client = redis_client
        self.ttl = settings.cache_ttl_seconds

    def build_key(self, text: str) -> str:
        normalized = text.strip().lower()
        digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        return f"brief:decode:v1:{digest}"

    async def get(self, text: str) -> BriefResult | None:
        try:
            payload = await self.redis_client.get(self.build_key(text))
        except Exception:  # pragma: no cover - depends on external service
            logger.warning("Redis read failed; continuing without cache", exc_info=True)
            return None
        if payload is None:
            return None
        return BriefResult.model_validate_json(payload)

    async def set(self, text: str, result: BriefResult) -> None:
        try:
            await self.redis_client.set(self.build_key(text), result.model_dump_json(), ex=self.ttl)
        except Exception:  # pragma: no cover - depends on external service
            logger.warning("Redis write failed; continuing without cache", exc_info=True)
