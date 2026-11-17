import asyncio
import logging
import sys
from collections.abc import Callable
from typing import Any

import asyncclick as click
import uvicorn
from alembic import command
from alembic.config import Config
from arq import Worker
from dishka.integrations.fastapi import setup_dishka

from ..api import fast_app
from ..api.auth.routes import include_routers as include_auth_routes
from ..api.exceptions import include_exception_handlers
from ..api.v1.routes import include_routers as include_v1_routes
from ..core.config import settings
from ..core.logging import setup_logger
from ..infrastructure.db.alembic.config import get_alembic_config_path
from ..infrastructure.di.container import get_async_container


async def _with_alembic_config(
    callback: Callable[[Config], Any],
) -> None:
    alembic_path_gen = get_alembic_config_path()
    try:
        alembic_path = next(alembic_path_gen)
    except StopIteration:
        logging.error("Alembic config path not found")
        return

    alembic_cfg = Config(str(alembic_path))
    alembic_cfg.set_main_option(
        "sqlalchemy.url",
        settings.get("db.database_url"),
    )

    await asyncio.to_thread(callback, alembic_cfg)


@click.group()
async def cli() -> None:
    debug = settings.get("core.debug")
    if debug:
        setup_logger(loglevel=logging.DEBUG)
    else:
        setup_logger(loglevel=logging.INFO)


@cli.group()
async def migrations() -> None:
    """Database migrations management."""
    pass


@cli.group()
async def run() -> None:
    """Run application components."""
    ctx = click.get_current_context()
    await ctx.invoke(upgrade)


@run.command()
async def api() -> None:
    _container = get_async_container()
    try:
        setup_dishka(container=_container, app=fast_app)

        include_auth_routes(fast_app)
        include_v1_routes(fast_app)
        include_exception_handlers(fast_app)

        config = uvicorn.Config(
            app=fast_app,
            host=settings.get("api.bind"),
            port=settings.get("api.port"),
            access_log=settings.get("api.enable_access_log"),
            log_config=None,
        )

        server = uvicorn.Server(config=config)
        await server.serve()
    except (KeyboardInterrupt, asyncio.exceptions.CancelledError):
        pass
    except Exception as e:
        logging.error(e)
        sys.exit(1)
    finally:
        await _container.close()


@run.command()
async def scheduler() -> None:
    _container = get_async_container()

    worker = await _container.get(Worker)

    try:
        await worker.async_run()
    except (KeyboardInterrupt, asyncio.exceptions.CancelledError):
        pass
    except Exception as e:
        logging.error(e)
        sys.exit(1)
    finally:
        await _container.close()
        await worker.close()


@migrations.command()
@click.argument("message", required=True)
async def autogenerate(
    message: str,
) -> None:
    """Autogenerate new migration."""
    await _with_alembic_config(
        lambda cfg: command.revision(cfg, autogenerate=True, message=message),
    )


@migrations.command()
@click.argument("revision", default="head")
async def downgrade(
    revision: str,
) -> None:
    """Downgrade database to specified revision."""
    await _with_alembic_config(
        lambda cfg: command.downgrade(cfg, revision),
    )


@migrations.command()
@click.argument("revision", default="head")
async def upgrade(revision: str) -> None:
    """Upgrade database to specified revision."""
    await _with_alembic_config(lambda cfg: command.upgrade(cfg, revision))
