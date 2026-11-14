import asyncio
import logging

import asyncclick as click
import uvicorn
from dishka.integrations.fastapi import setup_dishka

from ..api import fast_app
from ..api.exceptions import include_exception_handlers
from ..api.v1.routes import include_routers as include_v1_routes
from ..core.config import settings
from ..core.logging import setup_logger
from ..infrastructure.di.container import get_async_container


@click.group()
async def cli() -> None:
    debug = settings.get("core.debug")
    if debug:
        setup_logger(loglevel=logging.DEBUG)
    else:
        setup_logger(loglevel=logging.INFO)


@cli.group()
async def run() -> None:
    pass


@run.command()
async def api() -> None:
    try:
        _container = get_async_container()
        setup_dishka(container=_container, app=fast_app)

        include_exception_handlers(fast_app)
        include_v1_routes(fast_app)

        config = uvicorn.Config(
            app=fast_app,
            host=settings.get("api.bind"),
            port=settings.get("api.port"),
            access_log=settings.get("api.enable_access_log"),
            log_config=None,
        )

        server = uvicorn.Server(config=config)
        await server.serve()
    except KeyboardInterrupt:
        pass
    except asyncio.CancelledError:
        pass
