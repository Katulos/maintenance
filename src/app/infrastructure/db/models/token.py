import uuid
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import orm

from ....core.models import dto
from .base import Base
from .mixin import CreatedAtMixin

if TYPE_CHECKING:
    from .user import User


class Token(Base, CreatedAtMixin):
    __tablename__ = "tokens"

    id: orm.Mapped[uuid.UUID] = orm.mapped_column(
        sa.Uuid(),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: orm.Mapped[uuid.UUID] = orm.mapped_column(
        sa.Uuid(),
        sa.ForeignKey("users.id"),
        nullable=False,
    )

    access_token: orm.Mapped[str] = orm.mapped_column(
        sa.String(),
        unique=True,
        nullable=False,
    )

    user: orm.Mapped["User"] = orm.relationship(
        "User",
        back_populates="tokens",
        lazy="joined",
    )

    def to_dto(self) -> dto.TokenResponse:
        return dto.TokenResponse(
            access_token=self.access_token,
            created_at=self.created_at,
            user=dto.UserResponse(
                id=self.user.id,
                username=self.user.username,
                password=self.user.password,
            ),
        )
