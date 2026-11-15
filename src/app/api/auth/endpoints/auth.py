from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

router = APIRouter(tags=["auth"], route_class=DishkaRoute)
