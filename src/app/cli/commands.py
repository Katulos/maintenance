import logging

import asyncclick as click

from ..core.logging import setup_logger


@click.group()
async def cli() -> None:
    setup_logger(loglevel=logging.INFO)


@cli.group()
async def run() -> None:
    pass


@run.command()
async def hello() -> None:
    logging.info("Hello World!")
