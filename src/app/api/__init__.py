import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(fast_app: FastAPI) -> AsyncGenerator[None]:
    yield
    await fast_app.state.dishka_container.close()


fast_app = FastAPI(
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
