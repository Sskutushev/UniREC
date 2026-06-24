from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1.briefs import router as briefs_router
from app.api.v1.health import router as health_router
from app.core.config import get_settings
from app.core.errors import AppError
from app.core.logging import configure_logging
from app.domain.enums import ErrorCode
from app.domain.schemas import ErrorResponse


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging()
    app = FastAPI(title=settings.app_name)

    app.include_router(health_router)
    app.include_router(briefs_router)

    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        status_code_map = {
            ErrorCode.PROVIDER_FAILURE.value: 502,
            ErrorCode.VALIDATION_ERROR.value: 502,
            ErrorCode.RUN_NOT_FOUND.value: 404,
        }
        error_payload = ErrorResponse(error_code=exc.error_code, message=exc.message)
        return JSONResponse(
            status_code=status_code_map.get(exc.error_code, 500),
            content=error_payload.model_dump(mode="json"),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, __: Exception) -> JSONResponse:
        error_payload = ErrorResponse(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Unexpected internal error",
        )
        return JSONResponse(status_code=500, content=error_payload.model_dump(mode="json"))

    return app


app = create_app()
