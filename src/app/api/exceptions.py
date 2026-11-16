from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from ..core.errors import AccessDeniedError, ApplicationError
from .errors import ErrorResponse, InternalServerError, UnauthorizedError

error_to_http_status: dict[type[ApplicationError], int] = {
    UnauthorizedError: 401,
    # AuthUserAlreadyExistsError: 409,
    # UserNotFoundError: 404,
    AccessDeniedError: 403,
    # MissingTraceIdError: 422,
}


async def get_app_error_response(
    err: ApplicationError,
) -> JSONResponse:
    try:
        http_status = error_to_http_status[type(err)]
    except KeyError:
        http_status = 500

    error_response = ErrorResponse(
        code=err.code,
        message=err.message,
        meta=err.meta,
    ).to_json()

    return JSONResponse(
        status_code=http_status,
        content=error_response,
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
    app.add_exception_handler(Exception, app_error_handler)
