from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import DecodeRun
from app.domain.enums import RunStatus
from app.domain.schemas import DecodeRunCreate
from app.repositories.base import Repository


class DecodeRunRepository(Repository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create(self, data: DecodeRunCreate) -> DecodeRun:
        run = DecodeRun(
            status=data.status,
            input_text=data.input_text,
            input_hash=data.input_hash,
            provider_name=data.provider_name,
        )
        self.session.add(run)
        await self.session.flush()
        await self.session.refresh(run)
        return run

    async def get_by_id(self, run_id: UUID) -> DecodeRun | None:
        return await self.session.get(DecodeRun, run_id)

    async def get_by_input_hash(self, input_hash: str) -> DecodeRun | None:
        statement = (
            select(DecodeRun)
            .where(DecodeRun.input_hash == input_hash)
            .where(DecodeRun.status == RunStatus.COMPLETED)
            .order_by(DecodeRun.created_at.desc())
        )
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def update_status(
        self,
        run: DecodeRun,
        status: RunStatus,
        *,
        result: dict[str, object] | None = None,
        raw_provider_output: str | None = None,
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> DecodeRun:
        run.status = status
        run.result = result
        run.raw_provider_output = raw_provider_output
        run.error_code = error_code
        run.error_message = error_message
        run.completed_at = (
            datetime.now(UTC) if status in {RunStatus.COMPLETED, RunStatus.FAILED} else None
        )
        await self.session.flush()
        await self.session.refresh(run)
        return run
