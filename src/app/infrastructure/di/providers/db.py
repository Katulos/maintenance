from collections.abc import AsyncIterable

import sqlalchemy as sa
from dishka import AnyOf, Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from ....core.config import settings
from ....core.interfaces.dal import Committer


class DbProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_async_sessionmaker(
        self,
        engine: AsyncEngine,
    ) -> async_sessionmaker[AsyncSession]:

        session_factory = async_sessionmaker(
            bind=engine,
            expire_on_commit=False,
            autoflush=False,
            class_=AsyncSession,
        )
        return session_factory

    @provide(scope=Scope.APP)
    async def provide_engine(
        self,
    ) -> AsyncIterable[AsyncEngine]:
        engine = create_async_engine(
            url=sa.make_url(settings.get("db.database_url")),
            future=True,
            echo=settings.get("db.echo"),
        )
        yield engine
        await engine.dispose(close=True)

    @provide(scope=Scope.REQUEST)
    async def provide_session(
        self,
        engine: AsyncEngine,
    ) -> AsyncIterable[AnyOf[AsyncSession, Committer]]:
        async with AsyncSession(
            bind=engine,
            autoflush=False,
            expire_on_commit=False,
        ) as session:
            yield session
