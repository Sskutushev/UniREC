from __future__ import annotations

import hashlib
import logging
import re

from redis.asyncio import Redis

from app.core.config import Settings
from app.domain.schemas import BriefResult

logger = logging.getLogger(__name__)

_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")


def sanitize_input(text: str) -> str:
    """Strip control characters that carry no semantic value in a brief."""
    return _CONTROL_CHARS.sub("", text).strip()


class CacheService:
    # Bump the version suffix whenever BriefResult schema changes
    # to invalidate all existing cache entries without a manual flush.
    _KEY_VERSION = "v1"

    def __init__(self, redis_client: Redis, settings: Settings) -> None:
        self.redis_client = redis_client
        self.ttl = settings.cache_ttl_seconds

    def build_key(self, text: str, provider_name: str) -> str:
        """Cache key encodes both content and provider so switching providers
        does not silently return stale results from a different model."""
        normalized = text.strip().lower()
        digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        return f"brief:decode:{self._KEY_VERSION}:{provider_name}:{digest}"

    async def get(self, text: str, provider_name: str) -> BriefResult | None:
        try:
            payload = await self.redis_client.get(self.build_key(text, provider_name))
        except Exception:  # pragma: no cover - depends on external service
            logger.warning("Redis read failed; continuing without cache", exc_info=True)
            return None
        if payload is None:
            return None
        return BriefResult.model_validate_json(payload)

    async def set(self, text: str, provider_name: str, result: BriefResult) -> None:
        try:
            await self.redis_client.set(
                self.build_key(text, provider_name),
                result.model_dump_json(),
                ex=self.ttl,
            )
        except Exception:  # pragma: no cover - depends on external service
            logger.warning("Redis write failed; continuing without cache", exc_info=True)
