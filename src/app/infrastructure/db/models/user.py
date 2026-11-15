import uuid
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import orm

from ....core.models import dto
from .base import Base
from .mixin import CreatedUpdatedAtMixin

if TYPE_CHECKING:
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

    tokens: orm.Mapped["Token"] = orm.relationship(
        "Token",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def to_dto(self) -> dto.User:
        return dto.User(username=self.username, password=self.password)
