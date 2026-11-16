import uuid
from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import orm

from ....core.models import dto
from .base import Base
from .mixin import CreatedAtMixin

if TYPE_CHECKING:
    from .user import User


class RefreshToken(Base, CreatedAtMixin):
    __tablename__ = "refresh_tokens"

    id: orm.Mapped[uuid.UUID] = orm.mapped_column(
        sa.Uuid(),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: orm.Mapped[uuid.UUID] = orm.mapped_column(
        sa.Uuid(),
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    token_hash: orm.Mapped[str] = orm.mapped_column(
        sa.String(),
        unique=True,
        index=True,
        nullable=False,
    )

    expires_at: orm.Mapped[datetime] = orm.mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    revoked_at: orm.Mapped[datetime | None] = orm.mapped_column(
        sa.DateTime(timezone=True),
        nullable=True,
    )

    user: orm.Mapped["User"] = orm.relationship(
        "User",
        back_populates="refresh_tokens",
    )

    def to_dto(self) -> dto.RefreshTokenResponse:
        return dto.RefreshTokenResponse(
            id=self.id,
            user_id=self.user_id,
            token_hash=self.token_hash,
            expires_at=self.expires_at,
            created_at=self.created_at,
            revoked_at=self.revoked_at,
        )
