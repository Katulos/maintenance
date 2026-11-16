import uuid
from datetime import UTC, datetime, timedelta
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
    get_refresh_token_expiry,
    hash_token,
    verify_password,
)

router = APIRouter(tags=["auth"], route_class=DishkaRoute)


def _invalid_refresh_token() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
    )


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
    user = await dao.user.create_if_not_exists(
        dto.UserCreate(username=username, password=password),
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already registered",
        )
    return user


@router.post("/refresh")
async def refresh(
    refresh_token: Annotated[str, Form()],
    dao: FromDishka[DAO],
) -> dto.TokenApiResponse:
    payload = decode_token(refresh_token, expected_type="refresh")
    if payload is None:
        raise _invalid_refresh_token()
    try:
        user_id = uuid.UUID(str(payload.get("sub")))
    except (AttributeError, TypeError, ValueError):
        raise _invalid_refresh_token() from None

    stored_token = await dao.refresh_token.get_by_hash(
        hash_token(refresh_token),
    )
    if stored_token is None:
        raise _invalid_refresh_token()

    if stored_token.revoked_at is not None:
        await dao.refresh_token.revoke_all_for_user(stored_token.user_id)
        raise _invalid_refresh_token()

    if stored_token.expires_at <= datetime.now(UTC):
        await dao.refresh_token.revoke(stored_token.id)
        raise _invalid_refresh_token()

    if stored_token.user_id != user_id:
        await dao.refresh_token.revoke_all_for_user(stored_token.user_id)
        raise _invalid_refresh_token()

    if not await dao.refresh_token.revoke_if_active(stored_token.id):
        await dao.refresh_token.revoke_all_for_user(stored_token.user_id)
        raise _invalid_refresh_token()

    user = await dao.user.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    new_access_token = create_access_token(data={"sub": str(user.id)})
    refresh_expires_at = get_refresh_token_expiry()
    new_refresh_token = create_refresh_token(
        data={"sub": str(user.id)},
        expires_at=refresh_expires_at,
    )
    await dao.refresh_token.create(
        dto.RefreshTokenCreate(
            token_hash=hash_token(new_refresh_token),
            user_id=user.id,
            expires_at=refresh_expires_at,
        ),
    )
    token = await dao.token.upsert(
        dto.TokenCreate(access_token=new_access_token, user_id=user.id),
    )
    return dto.TokenApiResponse(
        access_token=token.access_token,
        refresh_token=new_refresh_token,
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
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
    )

    refresh_expires_at = get_refresh_token_expiry()
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)},
        expires_at=refresh_expires_at,
    )
    await dao.refresh_token.create(
        dto.RefreshTokenCreate(
            token_hash=hash_token(refresh_token),
            user_id=user.id,
            expires_at=refresh_expires_at,
        ),
    )

    token = await dao.token.upsert(
        dto.TokenCreate(access_token=access_token, user_id=user.id),
    )
    return dto.TokenApiResponse(
        access_token=token.access_token,
        refresh_token=refresh_token,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    refresh_token: Annotated[str, Form()],
    dao: FromDishka[DAO],
) -> None:
    stored_token = await dao.refresh_token.get_by_hash(
        hash_token(refresh_token),
    )
    if stored_token is not None:
        await dao.refresh_token.revoke(stored_token.id)
