from collections.abc import Mapping
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from ..core.errors import ApplicationError
from .errors import ErrorResponse, InternalServerError

_HTTP_ERROR_CODES: dict[int, str] = {
    status.HTTP_400_BAD_REQUEST: "BAD_REQUEST",
    status.HTTP_401_UNAUTHORIZED: "UNAUTHORIZED",
    status.HTTP_403_FORBIDDEN: "FORBIDDEN",
    status.HTTP_404_NOT_FOUND: "NOT_FOUND",
    status.HTTP_405_METHOD_NOT_ALLOWED: "METHOD_NOT_ALLOWED",
    status.HTTP_409_CONFLICT: "CONFLICT",
    status.HTTP_422_UNPROCESSABLE_CONTENT: "VALIDATION_ERROR",
}


def _error_response(
    *,
    code: str,
    message: str,
    meta: dict[str, Any] | None,
    status_code: int,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(
            code=code,
            message=message,
            meta=meta,
        ).to_json(),
        headers=headers,
    )


async def get_app_error_response(
    err: ApplicationError,
) -> JSONResponse:
    return _error_response(
        code=err.code,
        message=err.message,
        meta=err.meta,
        status_code=err.status_code,
    )


def _http_error_details(
    detail: Any,
) -> tuple[str, dict[str, Any] | None]:
    if isinstance(detail, str):
        return detail, None
    if detail is None:
        return "HTTP error", None
    return "HTTP error", {"detail": jsonable_encoder(detail)}


async def http_error_handler(
    _request: Request,
    exc: Exception,
) -> JSONResponse:
    assert isinstance(exc, StarletteHTTPException)
    message, meta = _http_error_details(exc.detail)
    return _error_response(
        code=_HTTP_ERROR_CODES.get(exc.status_code, "HTTP_ERROR"),
        message=message,
        meta=meta,
        status_code=exc.status_code,
        headers=exc.headers,
    )


async def validation_error_handler(
    _request: Request,
    exc: Exception,
) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)
    return _error_response(
        code="VALIDATION_ERROR",
        message="Validation error",
        meta={"errors": jsonable_encoder(exc.errors())},
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )


async def app_error_handler(
    _request: Request,
    exc: Exception,
) -> JSONResponse:
    app_error = exc if isinstance(exc, ApplicationError) else None
    if app_error is None:
        app_error = InternalServerError(orig_error=exc)
    return await get_app_error_response(app_error)


def include_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(StarletteHTTPException, http_error_handler)
    app.add_exception_handler(
        RequestValidationError,
        validation_error_handler,
    )
    app.add_exception_handler(Exception, app_error_handler)
