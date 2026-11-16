from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Base

_T = TypeVar("_T", bound=Base, covariant=True, contravariant=False)


class BaseDao(Generic[_T]):
    def __init__(self, model: type[_T], session: AsyncSession) -> None:
        self.model: type[_T] = model
        self.session: AsyncSession = session

    async def commit(self) -> None:
        await self.session.commit()
