import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.models import dto
from .. import models
from .base import BaseDao


class Token(BaseDao[models.Token]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(models.Token, session)

    async def create(self, token: dto.TokenCreate) -> dto.TokenResponse:
        kwargs = {
            "access_token": token.access_token,
            "user_id": token.user_id,
        }

        stmt = (
            sa.insert(models.Token).values(**kwargs).returning(models.Token)
        )

        result = await self.session.execute(stmt)
        await self.commit()

        token_obj = result.scalar_one()

        await self.session.refresh(token_obj, ["user"])

        return token_obj.to_dto()

    async def get(self, token: dto.TokenRequest) -> dto.TokenResponse:
        stmt = (
            sa.select(models.Token)
            .options(orm.joinedload(models.Token.user))
            .filter(
                models.Token.access_token == token.access_token,
            )
        )
        result = await self.session.execute(stmt)
        token_obj = result.scalar_one()
        return token_obj.to_dto()

    async def delete(self, token: dto.TokenRequest) -> None:
        await self.session.execute(
            sa.delete(models.Token).where(
                models.Token.access_token == token.access_token,
            ),
        )
        await self.commit()

    async def upsert(self, token: dto.TokenCreate) -> dto.TokenResponse:
        kwargs = {
            "access_token": token.access_token,
            "user_id": token.user_id,
        }

        stmt = (
            pg.insert(models.Token)
            .values(**kwargs)
            .on_conflict_do_update(
                index_elements=[models.Token.access_token],
                set_=kwargs,
                where=models.Token.access_token == token.access_token,
            )
            .returning(models.Token)
        )

        result = await self.session.execute(stmt)
        await self.commit()

        token_obj = result.scalar_one()

        await self.session.refresh(token_obj, ["user"])

        return token_obj.to_dto()
