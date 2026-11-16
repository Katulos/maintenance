from typing import Any

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.models import dto
from .. import models
from .base import BaseDao


class User(BaseDao[models.User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(models.User, session)

    async def create(self, user: dto.UserCreate) -> dto.UserResponse:
        kwargs = {"username": user.username, "password": user.password}
        stmt = sa.insert(models.User).values(**kwargs).returning(models.User)

        result = await self.session.execute(stmt)
        await self.commit()

        user_obj = result.scalar_one()

        await self.session.refresh(user_obj, ["tokens"])

        return user_obj.to_dto()

    async def get(self, user: dto.UserRequest) -> dto.UserResponse | None:
        stmt = await self.session.execute(
            sa.select(models.User).filter(
                models.User.username == user.username,
            ),
        )
        result = stmt.scalar_one_or_none()
        if result:
            return result.to_dto()
        else:
            return result

    async def get_by_id(self, id: Any) -> dto.UserResponse | None:
        stmt = await self.session.execute(
            sa.select(models.User).filter(
                models.User.id == id,
            ),
        )
        result = stmt.scalar_one_or_none()
        if result:
            return result.to_dto()
        else:
            return result

    async def delete(self, user: dto.UserRequest) -> None:
        await self.session.execute(
            sa.delete(models.User).where(
                models.User.username == user.username,
            ),
        )

    async def upsert(self, user: dto.UserCreate) -> dto.UserResponse:
        kwargs = {"username": user.username, "password": user.password}

        stmt = await self.session.execute(
            pg.insert(models.User)
            .values(**kwargs)
            .on_conflict_do_update(
                index_elements=[models.User.username],
                set_=kwargs,
                where=models.User.username == user.username,
            )
            .returning(models.User),
        )
        await self.commit()
        return stmt.scalar_one().to_dto()
