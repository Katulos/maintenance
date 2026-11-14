import logging

import asyncclick as click

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
async def hello() -> None:
    logging.info("Hello World!")
