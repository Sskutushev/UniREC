from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.briefs import router as briefs_router
from app.api.v1.health import router as health_router
from app.core.config import get_settings
from app.core.errors import AppError
from app.core.logging import configure_logging
from app.domain.enums import ErrorCode
from app.domain.schemas import ErrorResponse

_CHROME_EXT_ORIGIN_PREFIX = "chrome-extension://"

_APP_ERROR_STATUS_CODES: dict[str, int] = {
    ErrorCode.PROVIDER_FAILURE: 502,
    ErrorCode.VALIDATION_ERROR: 502,
    ErrorCode.RUN_NOT_FOUND: 404,
}


def _build_cors_middleware(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=rf"({_CHROME_EXT_ORIGIN_PREFIX}[a-z]{{32}}|http://localhost(:\d+)?)",
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type"],
        max_age=600,
    )


def _register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        status_code = _APP_ERROR_STATUS_CODES.get(exc.error_code, 500)
        payload = ErrorResponse(error_code=exc.error_code, message=exc.message)
        return JSONResponse(status_code=status_code, content=payload.model_dump(mode="json"))

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, __: Exception) -> JSONResponse:
        payload = ErrorResponse(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Unexpected internal error",
        )
        return JSONResponse(status_code=500, content=payload.model_dump(mode="json"))


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging()
    app = FastAPI(title=settings.app_name)

    _build_cors_middleware(app)
    app.include_router(health_router)
    app.include_router(briefs_router)
    _register_exception_handlers(app)

    return app


app = create_app()
