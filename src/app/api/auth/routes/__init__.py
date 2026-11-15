from fastapi import FastAPI

from ..endpoints.auth import router


def include_routers(app: FastAPI) -> None:
    app.include_router(router)
