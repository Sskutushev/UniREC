from collections.abc import AsyncIterator
from typing import Any, cast

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.dependencies import get_db, get_provider, get_redis_client
from app.db.base import Base
from app.main import app
from app.providers.base import LLMProvider
from app.providers.fake import FakeProvider


class FakeRedis:
    """In-process Redis replacement for tests.

    Implements the subset of commands used by CacheService, IdempotencyService,
    and the rate_limit_decode dependency.
    """

    def __init__(self) -> None:
        self._storage: dict[str, str] = {}
        self._counters: dict[str, int] = {}

    async def ping(self) -> bool:
        return True

    async def get(self, key: str) -> str | None:
        return self._storage.get(key)

    async def set(self, key: str, value: str, ex: int | None = None) -> bool:
        del ex
        self._storage[key] = value
        return True

    async def incr(self, key: str) -> int:
        self._counters[key] = self._counters.get(key, 0) + 1
        return self._counters[key]

    async def expire(self, key: str, seconds: int) -> bool:
        del key, seconds
        return True


@pytest.fixture
def fake_redis() -> FakeRedis:
    return FakeRedis()


@pytest.fixture
def provider() -> LLMProvider:
    return FakeProvider()


@pytest.fixture
async def session() -> AsyncIterator[AsyncSession]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db_session:
        yield db_session

    await engine.dispose()


@pytest.fixture
async def client(
    session: AsyncSession,
    fake_redis: FakeRedis,
    provider: LLMProvider,
) -> AsyncIterator[AsyncClient]:
    async def override_db() -> AsyncIterator[AsyncSession]:
        yield session

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_redis_client] = lambda: fake_redis
    app.dependency_overrides[get_provider] = lambda: provider
    transport = ASGITransport(app=cast(Any, app))
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client
    app.dependency_overrides.clear()
