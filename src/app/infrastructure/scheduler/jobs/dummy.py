import logging
from typing import Any


async def dummy_job(ctx: Any) -> None:
    logging.info("Run dummy job")
