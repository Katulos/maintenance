import asyncio
import logging

import asyncclick as click
import uvicorn

from ..api.api import fast_app
from ..core.config import settings
from ..core.logging import setup_logger


@click.group()
async def cli() -> None:
    debug = settings.get("core. debug")
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
