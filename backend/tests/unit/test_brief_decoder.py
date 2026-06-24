import pytest
from sqlalchemy import select

from app.core.config import get_settings
from app.core.errors import ProviderError, ValidationAppError
from app.db.models import DecodeRun
from app.domain.enums import RunStatus
from app.providers.base import LLMProvider, ProviderResponse
from app.providers.fake import FakeProvider
from app.services.brief_decoder import BriefDecoderService
from app.services.cache import CacheService
from tests.conftest import FakeRedis


class ExplodingProvider(LLMProvider):
    @property
    def name(self) -> str:
        return "exploding"

    async def decode_brief(self, text: str) -> ProviderResponse:
        del text
        raise ProviderError("Provider execution failed", error_code="provider_failure")


BRIEF_TEXT = (
    "We need a landing page for a B2B SaaS analytics product. "
    "The page should explain the product, include pricing teaser, "
    "capture emails, and be ready in 2 weeks. Budget is limited."
)


async def latest_run(session) -> DecodeRun:
    result = await session.execute(select(DecodeRun).order_by(DecodeRun.created_at.desc()))
    run = result.scalars().first()
    assert run is not None
    return run


async def test_service_happy_path(session) -> None:
    service = BriefDecoderService(
        session=session,
        provider=FakeProvider(),
        cache_service=CacheService(FakeRedis(), get_settings()),
    )

    response = await service.decode(BRIEF_TEXT)

    assert response.status == RunStatus.COMPLETED
    assert response.result is not None
    assert response.result.summary


async def test_service_stores_raw_provider_output_for_live_call(session) -> None:
    service = BriefDecoderService(
        session=session,
        provider=FakeProvider(),
        cache_service=CacheService(FakeRedis(), get_settings()),
    )

    await service.decode(BRIEF_TEXT)
    run = await latest_run(session)

    assert run.raw_provider_output is not None


async def test_service_cache_hit_leaves_raw_provider_output_null(session) -> None:
    """Cache-served runs must not pollute raw_provider_output with serialized BriefResult."""
    from app.repositories.decode_run import DecodeRunRepository

    cache = CacheService(FakeRedis(), get_settings())
    provider = FakeProvider()
    first_service = BriefDecoderService(session=session, provider=provider, cache_service=cache)
    await first_service.decode(BRIEF_TEXT)

    second_service = BriefDecoderService(session=session, provider=provider, cache_service=cache)
    second_response = await second_service.decode(BRIEF_TEXT)

    repo = DecodeRunRepository(session)
    run = await repo.get_by_id(second_response.run_id)

    assert run is not None
    assert run.raw_provider_output is None


async def test_service_marks_run_failed_on_provider_error(session) -> None:
    service = BriefDecoderService(
        session=session,
        provider=ExplodingProvider(),
        cache_service=CacheService(FakeRedis(), get_settings()),
    )

    with pytest.raises(ProviderError):
        await service.decode(BRIEF_TEXT)

    run = await latest_run(session)

    assert run.status == RunStatus.FAILED
    assert run.error_code == "provider_failure"


async def test_service_marks_run_failed_on_invalid_provider_payload(session) -> None:
    service = BriefDecoderService(
        session=session,
        provider=FakeProvider(mode="invalid_json"),
        cache_service=CacheService(FakeRedis(), get_settings()),
    )

    with pytest.raises(ValidationAppError):
        await service.decode(BRIEF_TEXT)

    run = await latest_run(session)

    assert run.status == RunStatus.FAILED
    assert run.error_code == "validation_error"


async def test_service_uses_cache_before_provider(session) -> None:
    fake_redis = FakeRedis()
    cache = CacheService(fake_redis, get_settings())
    priming_service = BriefDecoderService(
        session=session,
        provider=FakeProvider(),
        cache_service=cache,
    )
    first_response = await priming_service.decode(BRIEF_TEXT)

    class CountingProvider(FakeProvider):
        def __init__(self) -> None:
            super().__init__()
            self.calls = 0

        async def decode_brief(self, text: str) -> ProviderResponse:
            self.calls += 1
            return await super().decode_brief(text)

    provider = CountingProvider()
    service = BriefDecoderService(session=session, provider=provider, cache_service=cache)
    second_response = await service.decode(BRIEF_TEXT)

    assert provider.calls == 0
    assert first_response.result == second_response.result


async def test_service_sanitizes_control_characters_in_input(session) -> None:
    dirty_text = BRIEF_TEXT + "\x00\x1f"
    service = BriefDecoderService(
        session=session,
        provider=FakeProvider(),
        cache_service=CacheService(FakeRedis(), get_settings()),
    )

    response = await service.decode(dirty_text)
    run = await latest_run(session)

    assert response.status == RunStatus.COMPLETED
    assert "\x00" not in run.input_text
