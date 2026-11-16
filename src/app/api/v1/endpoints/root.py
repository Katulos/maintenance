from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends

from ....core.models import dto
from ...dependencies.security import get_current_user
from ..commands.ping import Ping

router = APIRouter(
    tags=["root"],
    route_class=DishkaRoute,
)


@router.get("/v1/ping")
async def ping(
    user: Annotated[dto.UserResponse, Depends(get_current_user)],
    command: FromDishka[Ping],
) -> str:
    return await command.execute()
