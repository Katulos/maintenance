import base64
import hmac
import os
from datetime import UTC, datetime, timedelta
from typing import Annotated, Any

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
)
from jose import JWTError, jwt

from ...core.config import settings
from ...core.models import dto
from ...infrastructure.db.dao import DAO

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

_HASH_ALGORITHM = hashes.SHA256()


def get_password_hash(password: str) -> str:

    salt = os.urandom(settings.get("security.salt_length"))

    kdf = PBKDF2HMAC(
        algorithm=_HASH_ALGORITHM,
        length=settings.get("security.key_length"),
        salt=salt,
        iterations=settings.get("security.iterations"),
    )

    password_bytes = password.encode("utf-8")
    key = kdf.derive(password_bytes)

    salt_b64 = base64.b64encode(salt).decode("utf-8")
    hash_b64 = base64.b64encode(key).decode("utf-8")

    return f"pbkdf2_sha256${settings.get('security.iterations')}${salt_b64}${hash_b64}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not isinstance(plain_password, str) or not isinstance(
        hashed_password,
        str,
    ):
        return False

    try:
        parts = hashed_password.split("$")
        if len(parts) != 4:
            return False

        algorithm_name, iterations_str, salt_b64, hash_b64 = parts

        if algorithm_name != "pbkdf2_sha256":
            return False

        iterations = int(iterations_str)
        salt = base64.b64decode(salt_b64)
        expected_hash = base64.b64decode(hash_b64)

        kdf = PBKDF2HMAC(
            algorithm=_HASH_ALGORITHM,
            length=settings.get("security.key_length"),
            salt=salt,
            iterations=iterations,
        )

        password_bytes = plain_password.encode("utf-8")
        computed_hash = kdf.derive(password_bytes)

        return hmac.compare_digest(computed_hash, expected_hash)

    except (ValueError, TypeError, Exception):
        return False


def create_access_token(
    data: dict[Any, Any],
    expires_delta: timedelta | None = None,
) -> str:

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.get("security.access_token_expire_minutes"),
        )

    to_encode.update({"exp": expire, "type": "access"})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.get("core.secret_key"),
        algorithm=settings.get("security.algorithm"),
    )
    return encoded_jwt


def create_refresh_token(data: dict[Any, Any]) -> str:
    to_encode = data.copy()

    expire = datetime.now(UTC) + timedelta(
        days=settings.get("security.refresh_token_expire_days"),
    )
    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.get("core.secret_key"),
        algorithm=settings.get("security.algorithm"),
    )
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any] | None:
    try:
        payload = jwt.decode(
            token,
            settings.get("core.secret_key"),
            algorithms=[settings.get("security.algorithm")],
        )
        return payload
    except JWTError:
        return None


@inject
async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials,
        Depends(HTTPBearer()),
    ],
    dao: FromDishka[DAO],
) -> dto.UserResponse | None:
    token_value = credentials.credentials
    token = await dao.token.get(dto.TokenRequest(access_token=token_value))
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if token.created_at < datetime.now() - timedelta(
        days=settings.get("security.access_token_expire_minutes"),
    ):
        await dao.token.delete(
            dto.TokenRequest(access_token=token.access_token),
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token.user
