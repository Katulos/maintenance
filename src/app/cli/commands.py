import logging

import asyncclick as click


@click.group()
async def cli() -> None:
    logging.basicConfig(level=logging.INFO)


@cli.group()
async def run() -> None:
    pass


@run.command()
async def hello() -> None:
    logging.info("Hello World!")
