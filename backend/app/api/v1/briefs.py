from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_decoder_service
from app.core.errors import NotFoundError
from app.domain.enums import ErrorCode
from app.domain.schemas import DecodeBriefRequest, DecodeRunResponse, DecodeRunStatus
from app.services.brief_decoder import BriefDecoderService

router = APIRouter(prefix="/v1/briefs", tags=["briefs"])


@router.post("/decode", response_model=DecodeRunResponse, status_code=status.HTTP_200_OK)
async def decode_brief(
    payload: DecodeBriefRequest,
    service: BriefDecoderService = Depends(get_decoder_service),
) -> DecodeRunResponse:
    return await service.decode(payload.text)


@router.get("/runs/{run_id}", response_model=DecodeRunStatus)
async def get_run_status(
    run_id: UUID,
    service: BriefDecoderService = Depends(get_decoder_service),
) -> DecodeRunStatus:
    run = await service.get_run_status(run_id)
    if run is None:
        raise NotFoundError("Decode run not found", error_code=ErrorCode.RUN_NOT_FOUND)
    return run
