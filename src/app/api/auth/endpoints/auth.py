from datetime import timedelta
from typing import Annotated

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ....core.config import settings
from ....core.models import dto
from ....infrastructure.db.dao import DAO
from ...dependencies.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)

router = APIRouter(tags=["auth"], route_class=DishkaRoute)


@router.post("/register")
async def register(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    dao: FromDishka[DAO],
) -> dto.UserResponse:
    exists = await dao.user.get(dto.UserRequest(username=username))
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already registered",
        )
    password = get_password_hash(password)
    user = await dao.user.upsert(
        dto.UserCreate(username=username, password=password),
    )
    return user


@router.post("/refresh")
async def refresh(
    refresh_token: str,
    dao: FromDishka[DAO],
) -> dto.TokenApiResponse:
    payload = decode_token(refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    user = await dao.user.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    new_access_token = create_access_token(data={"sub": str(user.id)})
    token = await dao.token.upsert(
        dto.TokenCreate(access_token=new_access_token, user_id=user.id),
    )
    return dto.TokenApiResponse(
        access_token=token.access_token,
        refresh_token=refresh_token,
    )


@router.post("/token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    dao: FromDishka[DAO],
) -> dto.TokenApiResponse:

    user = await dao.user.get(dto.UserRequest(username=form_data.username))
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=settings.get("security.access_token_expire_minutes"),
    )
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )
    token = await dao.token.upsert(
        dto.TokenCreate(access_token=access_token, user_id=user.id),
    )
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    return dto.TokenApiResponse(
        access_token=token.access_token,
        refresh_token=refresh_token,
    )
