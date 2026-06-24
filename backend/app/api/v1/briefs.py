from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Header, status

from app.api.dependencies import (
    get_decoder_service,
    get_idempotency_service,
    rate_limit_decode,
)
from app.core.errors import NotFoundError
from app.domain.enums import ErrorCode
from app.domain.schemas import DecodeBriefRequest, DecodeRunResponse, DecodeRunStatus
from app.services.brief_decoder import BriefDecoderService
from app.services.idempotency import IdempotencyService

router = APIRouter(prefix="/v1/briefs", tags=["briefs"])


@router.post(
    "/decode",
    response_model=DecodeRunResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(rate_limit_decode)],
)
async def decode_brief(
    payload: DecodeBriefRequest,
    x_idempotency_key: str | None = Header(default=None, alias="X-Idempotency-Key"),
    service: BriefDecoderService = Depends(get_decoder_service),
    idempotency_service: IdempotencyService = Depends(get_idempotency_service),
) -> DecodeRunResponse:
    if x_idempotency_key:
        existing_run_id = await idempotency_service.get_run_id(x_idempotency_key)
        if existing_run_id:
            run_status = await service.get_run_status(UUID(existing_run_id))
            if run_status is not None:
                return run_status

    response = await service.decode(payload.text)

    if x_idempotency_key:
        await idempotency_service.store_run_id(x_idempotency_key, str(response.run_id))

    return response


@router.get("/runs/{run_id}", response_model=DecodeRunStatus)
async def get_run_status(
    run_id: UUID,
    service: BriefDecoderService = Depends(get_decoder_service),
) -> DecodeRunStatus:
    run = await service.get_run_status(run_id)
    if run is None:
        raise NotFoundError("Decode run not found", error_code=ErrorCode.RUN_NOT_FOUND)
    return run
