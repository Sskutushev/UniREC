from __future__ import annotations

import hashlib
import json
from uuid import UUID

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ProviderError, ValidationAppError
from app.db.models import DecodeRun
from app.domain.enums import ErrorCode, RunStatus
from app.domain.schemas import BriefResult, DecodeRunCreate, DecodeRunResponse, DecodeRunStatus
from app.providers.base import LLMProvider
from app.repositories.decode_run import DecodeRunRepository
from app.services.cache import CacheService


def _hash_input(text: str) -> str:
    return hashlib.sha256(text.lower().encode("utf-8")).hexdigest()


class BriefDecoderService:
    def __init__(
        self,
        session: AsyncSession,
        provider: LLMProvider,
        cache_service: CacheService,
    ) -> None:
        self.session = session
        self.provider = provider
        self.cache_service = cache_service
        self.repository = DecodeRunRepository(session)

    async def decode(self, input_text: str) -> DecodeRunResponse:
        normalized = input_text.strip()
        input_hash = _hash_input(normalized)

        cached = await self.cache_service.get(normalized)
        if cached is not None:
            return await self._persist_cache_hit(normalized, input_hash, cached)

        run = await self._create_run(normalized, input_hash)
        return await self._execute_decode(run, normalized)

    async def get_run_status(self, run_id: UUID) -> DecodeRunStatus | None:
        run = await self.repository.get_by_id(run_id)
        if run is None:
            return None
        return self._to_run_status(run)

    # ─── Private helpers ──────────────────────────────────────────────────────

    async def _persist_cache_hit(
        self, normalized: str, input_hash: str, result: BriefResult
    ) -> DecodeRunResponse:
        run = await self.repository.create(
            DecodeRunCreate(
                input_text=normalized,
                input_hash=input_hash,
                provider_name=self.provider.name,
            )
        )
        await self.repository.update_status(
            run,
            RunStatus.COMPLETED,
            result=result.model_dump(mode="json"),
            raw_provider_output=result.model_dump_json(),
        )
        await self.session.commit()
        return self._to_run_response(run)

    async def _create_run(self, normalized: str, input_hash: str) -> DecodeRun:
        run = await self.repository.create(
            DecodeRunCreate(
                input_text=normalized,
                input_hash=input_hash,
                provider_name=self.provider.name,
            )
        )
        await self.repository.update_status(run, RunStatus.RUNNING)
        await self.session.commit()
        return run

    async def _execute_decode(self, run: DecodeRun, normalized: str) -> DecodeRunResponse:
        try:
            result = await self._invoke_provider(normalized)
        except ProviderError as exc:
            await self._mark_failed(run, exc.error_code, exc.message)
            raise
        except (json.JSONDecodeError, ValidationError) as exc:
            msg = "Structured output validation failed"
            await self._mark_failed(run, ErrorCode.VALIDATION_ERROR, msg)
            raise ValidationAppError(
                "Structured output validation failed",
                error_code=ErrorCode.VALIDATION_ERROR,
            ) from exc

        await self._persist_result(run, result, normalized)
        return self._to_run_response(run)

    async def _invoke_provider(self, text: str) -> BriefResult:
        response = await self.provider.decode_brief(text)
        payload = json.loads(response.raw_output)
        return BriefResult.model_validate(payload)

    async def _persist_result(self, run: DecodeRun, result: BriefResult, text: str) -> None:
        await self.repository.update_status(
            run,
            RunStatus.COMPLETED,
            result=result.model_dump(mode="json"),
            raw_provider_output=result.model_dump_json(),
        )
        await self.session.commit()
        await self.cache_service.set(text, result)

    async def _mark_failed(self, run: DecodeRun, error_code: str, error_message: str) -> None:
        await self.repository.update_status(
            run,
            RunStatus.FAILED,
            error_code=error_code,
            error_message=error_message,
        )
        await self.session.commit()

    def _to_run_response(self, run: DecodeRun) -> DecodeRunResponse:
        result = BriefResult.model_validate(run.result) if run.result is not None else None
        return DecodeRunResponse(
            run_id=run.id,
            status=run.status,
            result=result,
            error_code=run.error_code,
            error_message=run.error_message,
            created_at=run.created_at,
            updated_at=run.updated_at,
            completed_at=run.completed_at,
        )

    def _to_run_status(self, run: DecodeRun) -> DecodeRunStatus:
        result = BriefResult.model_validate(run.result) if run.result is not None else None
        return DecodeRunStatus(
            run_id=run.id,
            status=run.status,
            input_text=run.input_text,
            provider_name=run.provider_name,
            result=result,
            error_code=run.error_code,
            error_message=run.error_message,
            created_at=run.created_at,
            updated_at=run.updated_at,
            completed_at=run.completed_at,
        )
