from collections.abc import AsyncIterator
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.domain.enums import RunStatus
from app.domain.schemas import DecodeRunCreate
from app.repositories.decode_run import DecodeRunRepository


@pytest.fixture
async def session() -> AsyncIterator[AsyncSession]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db_session:
        yield db_session

    await engine.dispose()


def make_create_data(suffix: str = "a") -> DecodeRunCreate:
    return DecodeRunCreate(
        input_text=suffix * 60,
        input_hash=suffix * 64,
        provider_name="fake",
    )


async def test_repository_creates_and_reads_run(session: AsyncSession) -> None:
    repo = DecodeRunRepository(session)
    created = await repo.create(make_create_data("a"))
    await session.commit()

    loaded = await repo.get_by_id(created.id)

    assert loaded is not None
    assert loaded.input_hash == "a" * 64
    assert loaded.status == RunStatus.PENDING


async def test_repository_get_by_id_returns_none_for_unknown(session: AsyncSession) -> None:
    repo = DecodeRunRepository(session)

    loaded = await repo.get_by_id(uuid4())

    assert loaded is None


async def test_repository_updates_status_to_completed(session: AsyncSession) -> None:
    repo = DecodeRunRepository(session)
    run = await repo.create(make_create_data("b"))

    await repo.update_status(
        run,
        RunStatus.COMPLETED,
        result={"summary": "done"},
        raw_provider_output="{}",
    )
    await session.commit()

    loaded = await repo.get_by_id(run.id)

    assert loaded is not None
    assert loaded.status == RunStatus.COMPLETED
    assert loaded.result == {"summary": "done"}
    assert loaded.completed_at is not None


async def test_repository_updates_status_to_failed(session: AsyncSession) -> None:
    repo = DecodeRunRepository(session)
    run = await repo.create(make_create_data("c"))

    await repo.update_status(
        run,
        RunStatus.FAILED,
        error_code="provider_failure",
        error_message="Provider timed out",
    )
    await session.commit()

    loaded = await repo.get_by_id(run.id)

    assert loaded is not None
    assert loaded.status == RunStatus.FAILED
    assert loaded.error_code == "provider_failure"
    assert loaded.completed_at is not None


async def test_repository_get_by_input_hash_returns_completed_run(session: AsyncSession) -> None:
    repo = DecodeRunRepository(session)
    run = await repo.create(make_create_data("d"))
    await repo.update_status(run, RunStatus.COMPLETED, result={"summary": "cached"})
    await session.commit()

    cached = await repo.get_by_input_hash("d" * 64)

    assert cached is not None
    assert cached.id == run.id


async def test_repository_get_by_input_hash_ignores_non_completed(session: AsyncSession) -> None:
    repo = DecodeRunRepository(session)
    run = await repo.create(make_create_data("e"))
    # leave as PENDING — should not be returned as a cache hit
    await session.commit()
    del run

    cached = await repo.get_by_input_hash("e" * 64)

    assert cached is None


async def test_repository_get_by_input_hash_returns_none_for_missing(session: AsyncSession) -> None:
    repo = DecodeRunRepository(session)

    cached = await repo.get_by_input_hash("0" * 64)

    assert cached is None
