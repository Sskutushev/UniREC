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
        normalized_text = input_text.strip()
        input_hash = hashlib.sha256(normalized_text.lower().encode("utf-8")).hexdigest()

        cached_result = await self.cache_service.get(normalized_text)
        if cached_result is not None:
            run = await self.repository.create(
                DecodeRunCreate(
                    input_text=normalized_text,
                    input_hash=input_hash,
                    provider_name=self.provider.name,
                )
            )
            await self.repository.update_status(
                run,
                RunStatus.COMPLETED,
                result=cached_result.model_dump(mode="json"),
                raw_provider_output=cached_result.model_dump_json(),
            )
            await self.session.commit()
            return self._to_run_response(run)

        run = await self.repository.create(
            DecodeRunCreate(
                input_text=normalized_text,
                input_hash=input_hash,
                provider_name=self.provider.name,
            )
        )
        await self.repository.update_status(run, RunStatus.RUNNING)
        await self.session.commit()

        try:
            provider_response = await self.provider.decode_brief(normalized_text)
            parsed_payload = json.loads(provider_response.raw_output)
            result = BriefResult.model_validate(parsed_payload)
        except ProviderError as exc:
            await self._mark_failed(run, exc.error_code, exc.message)
            raise
        except (json.JSONDecodeError, ValidationError) as exc:
            await self._mark_failed(
                run,
                ErrorCode.VALIDATION_ERROR,
                "Structured output validation failed",
            )
            raise ValidationAppError(
                "Structured output validation failed",
                error_code=ErrorCode.VALIDATION_ERROR,
            ) from exc

        await self.repository.update_status(
            run,
            RunStatus.COMPLETED,
            result=result.model_dump(mode="json"),
            raw_provider_output=provider_response.raw_output,
        )
        await self.session.commit()
        await self.cache_service.set(normalized_text, result)
        return self._to_run_response(run)

    async def get_run_status(self, run_id: UUID) -> DecodeRunStatus | None:
        run = await self.repository.get_by_id(run_id)
        if run is None:
            return None
        return self._to_run_status(run)

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
