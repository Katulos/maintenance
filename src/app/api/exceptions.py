from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

error_code = {
    Exception: 500,
}


def get_http_error_response(
    err: Exception,
) -> JSONResponse:
    err_type = type(err)
    err_http_code = error_code[err_type]

    return JSONResponse(
        status_code=err_http_code,
        content={},
    )


async def app_exception_handler(
    _request: Request,
    exc: Exception,
) -> JSONResponse:
    return get_http_error_response(exc)


def include_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(Exception, app_exception_handler)
