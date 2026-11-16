from sqlalchemy.ext.asyncio import AsyncSession

from .refresh_token import RefreshToken
from .token import Token
from .user import User


class DAO:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

        self.refresh_token = RefreshToken(self.session)

        self.token = Token(self.session)

        self.user = User(self.session)

    async def commit(self) -> None:
        await self.session.commit()
