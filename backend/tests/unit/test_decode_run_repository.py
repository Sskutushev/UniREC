from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.domain.enums import RunStatus
from app.domain.schemas import DecodeRunCreate
from app.repositories.decode_run import DecodeRunRepository


@pytest.fixture
async def session() -> AsyncSession:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_repository_creates_and_reads_run(session: AsyncSession) -> None:
    repository = DecodeRunRepository(session)
    created = await repository.create(
        DecodeRunCreate(
            input_text="A" * 60,
            input_hash="a" * 64,
            provider_name="fake",
        )
    )
    await session.commit()

    loaded = await repository.get_by_id(created.id)

    assert loaded is not None
    assert loaded.input_hash == "a" * 64


@pytest.mark.asyncio
async def test_repository_updates_status(session: AsyncSession) -> None:
    repository = DecodeRunRepository(session)
    run = await repository.create(
        DecodeRunCreate(
            input_text="B" * 60,
            input_hash="b" * 64,
            provider_name="fake",
        )
    )

    await repository.update_status(
        run,
        RunStatus.COMPLETED,
        result={"summary": "done"},
        raw_provider_output="{}",
    )
    await session.commit()

    loaded = await repository.get_by_id(run.id)

    assert loaded is not None
    assert loaded.status == RunStatus.COMPLETED
    assert loaded.result == {"summary": "done"}
    assert loaded.completed_at is not None


@pytest.mark.asyncio
async def test_repository_gets_by_input_hash(session: AsyncSession) -> None:
    repository = DecodeRunRepository(session)
    run = await repository.create(
        DecodeRunCreate(
            input_text="C" * 60,
            input_hash="c" * 64,
            provider_name="fake",
        )
    )
    await repository.update_status(run, RunStatus.COMPLETED, result={"summary": "cached"})
    await session.commit()

    cached = await repository.get_by_input_hash("c" * 64)

    assert cached is not None
    assert cached.id == run.id
