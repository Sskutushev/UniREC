import pytest

from app.core.config import get_settings
from app.domain.schemas import BriefResult
from app.services.cache import CacheService, sanitize_input
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


async def test_cache_set_and_get_roundtrip() -> None:
    service = CacheService(FakeRedis(), get_settings())
    result = build_result()

    await service.set("Example brief text", "fake", result)
    cached = await service.get("Example brief text", "fake")

    assert cached == result


async def test_cache_miss_returns_none() -> None:
    service = CacheService(FakeRedis(), get_settings())

    cached = await service.get("text that was never cached", "fake")

    assert cached is None


async def test_cache_key_normalizes_case_and_whitespace() -> None:
    service = CacheService(FakeRedis(), get_settings())
    result = build_result()

    await service.set("  Hello World  ", "fake", result)

    assert await service.get("hello world", "fake") == result
    assert await service.get("  HELLO WORLD  ", "fake") == result


async def test_cache_key_is_provider_scoped() -> None:
    """Results cached under one provider must not be returned for a different provider."""
    service = CacheService(FakeRedis(), get_settings())
    result = build_result()

    await service.set("same text", "openai", result)

    assert await service.get("same text", "openai") == result
    assert await service.get("same text", "fake") is None


async def test_cache_gracefully_handles_redis_read_failure() -> None:
    service = CacheService(BrokenRedis(), get_settings())

    cached = await service.get("Example brief text", "fake")

    assert cached is None


async def test_cache_gracefully_handles_redis_write_failure() -> None:
    service = CacheService(BrokenRedis(), get_settings())

    # must not raise
    await service.set("Example brief text", "fake", build_result())


@pytest.mark.parametrize(
    "text",
    [
        "short",
        "A" * 200,
        "  leading and trailing  ",
    ],
)
async def test_cache_build_key_is_deterministic(text: str) -> None:
    service = CacheService(FakeRedis(), get_settings())

    key_a = service.build_key(text, "fake")
    key_b = service.build_key(text, "fake")

    assert key_a == key_b
    assert key_a.startswith("brief:decode:v1:fake:")


# ─── sanitize_input ───────────────────────────────────────────────────────────


def test_sanitize_input_strips_control_characters() -> None:
    dirty = "hello\x00world\x1f"
    assert sanitize_input(dirty) == "helloworld"


def test_sanitize_input_preserves_newlines_and_tabs() -> None:
    text = "line one\nline two\ttabbed"
    assert sanitize_input(text) == text


def test_sanitize_input_strips_surrounding_whitespace() -> None:
    assert sanitize_input("  brief text  ") == "brief text"
