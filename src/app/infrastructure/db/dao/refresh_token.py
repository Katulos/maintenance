import uuid
from datetime import UTC, datetime

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.models import dto
from .. import models
from .base import BaseDao


class RefreshToken(BaseDao[models.RefreshToken]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(models.RefreshToken, session)

    async def create(
        self,
        token: dto.RefreshTokenCreate,
    ) -> dto.RefreshTokenResponse:
        kwargs = {
            "user_id": token.user_id,
            "token_hash": token.token_hash,
            "expires_at": token.expires_at,
        }
        stmt = (
            sa.insert(models.RefreshToken)
            .values(**kwargs)
            .returning(models.RefreshToken)
        )

        result = await self.session.execute(stmt)
        await self.commit()

        return result.scalar_one().to_dto()

    async def get_by_hash(
        self,
        token_hash: str,
    ) -> dto.RefreshTokenResponse | None:
        result = await self.session.execute(
            sa.select(models.RefreshToken).where(
                models.RefreshToken.token_hash == token_hash,
            ),
        )
        token_obj = result.scalar_one_or_none()
        if token_obj:
            return token_obj.to_dto()
        return None

    async def revoke(self, token_id: uuid.UUID) -> None:
        await self.session.execute(
            sa.update(models.RefreshToken)
            .where(
                models.RefreshToken.id == token_id,
                models.RefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(UTC)),
        )
        await self.commit()

    async def revoke_if_active(self, token_id: uuid.UUID) -> bool:
        result = await self.session.execute(
            sa.update(models.RefreshToken)
            .where(
                models.RefreshToken.id == token_id,
                models.RefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(UTC))
            .returning(models.RefreshToken.id),
        )
        await self.commit()
        return result.scalar_one_or_none() is not None

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        await self.session.execute(
            sa.update(models.RefreshToken)
            .where(
                models.RefreshToken.user_id == user_id,
                models.RefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(UTC)),
        )
        await self.commit()
