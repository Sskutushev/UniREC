import pytest

from app.core.config import get_settings
from app.domain.schemas import BriefResult
from app.services.cache import CacheService
from tests.conftest import FakeRedis


class BrokenRedis(FakeRedis):
    async def get(self, key: str) -> str | None:
        del key
        raise RuntimeError("redis unavailable")

    async def set(self, key: str, value: str, ex: int | None = None) -> bool:
        del key, value, ex
        raise RuntimeError("redis unavailable")


def build_result() -> BriefResult:
    return BriefResult.model_validate(
        {
            "summary": "Normalized brief summary",
            "goals": ["Explain the offer"],
            "deliverables": ["Landing page plan"],
            "constraints": ["Limited budget"],
            "risks": [
                {
                    "risk": "Timeline pressure",
                    "severity": "medium",
                    "reason": "Two weeks for copy and launch prep is tight.",
                }
            ],
            "clarifying_questions": ["Who approves the launch copy?"],
            "recommended_next_action": "Confirm scope priorities.",
        }
    )


@pytest.mark.asyncio
async def test_cache_set_and_get_roundtrip() -> None:
    service = CacheService(FakeRedis(), get_settings())
    result = build_result()

    await service.set("Example brief text", result)
    cached = await service.get("Example brief text")

    assert cached == result


@pytest.mark.asyncio
async def test_cache_gracefully_handles_redis_failures() -> None:
    service = CacheService(BrokenRedis(), get_settings())

    await service.set("Example brief text", build_result())
    cached = await service.get("Example brief text")

    assert cached is None
