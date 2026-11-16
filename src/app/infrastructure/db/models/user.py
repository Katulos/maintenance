import uuid
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import orm

from ....core.models import dto
from .base import Base
from .mixin import CreatedUpdatedAtMixin

if TYPE_CHECKING:
    from .refresh_token import RefreshToken
    from .token import Token


class User(Base, CreatedUpdatedAtMixin):
    __tablename__ = "users"

    id: orm.Mapped[uuid.UUID] = orm.mapped_column(
        sa.Uuid(),
        primary_key=True,
        default=uuid.uuid4,
    )

    username: orm.Mapped[str] = orm.mapped_column(
        sa.String(),
        unique=True,
        index=True,
        nullable=False,
    )

    password: orm.Mapped[str] = orm.mapped_column(sa.String(), nullable=False)

    tokens: orm.Mapped[list["Token"]] = orm.relationship(
        "Token",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    refresh_tokens: orm.Mapped[list["RefreshToken"]] = orm.relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def to_dto(self) -> dto.UserResponse:
        return dto.UserResponse(
            id=self.id,
            username=self.username,
        )

    def to_auth_dto(self) -> dto.UserWithPassword:
        return dto.UserWithPassword(
            id=self.id,
            username=self.username,
            password=self.password,
        )
