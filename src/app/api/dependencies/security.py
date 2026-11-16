import base64
import hashlib
import hmac
import os
import uuid
from datetime import UTC, datetime, timedelta
from typing import Annotated, Any

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
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

    encoded_jwt: str = jwt.encode(
        to_encode,
        settings.get("core.secret_key"),
        algorithm=settings.get("security.algorithm"),
    )
    return encoded_jwt


def get_refresh_token_expiry() -> datetime:
    return datetime.now(UTC) + timedelta(
        days=settings.get("security.refresh_token_expire_days"),
    )


def create_refresh_token(
    data: dict[Any, Any],
    expires_at: datetime | None = None,
) -> str:
    to_encode = data.copy()

    if expires_at is None:
        expires_at = get_refresh_token_expiry()

    to_encode.update(
        {
            "exp": expires_at,
            "type": "refresh",
            "jti": str(uuid.uuid4()),
        },
    )

    encoded_jwt: str = jwt.encode(
        to_encode,
        settings.get("core.secret_key"),
        algorithm=settings.get("security.algorithm"),
    )
    return encoded_jwt


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def decode_token(
    token: str,
    *,
    expected_type: str | None = None,
) -> dict[str, Any] | None:
    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            settings.get("core.secret_key"),
            algorithms=[settings.get("security.algorithm")],
        )
    except (JWTError, TypeError, ValueError):
        return None

    if expected_type is not None and payload.get("type") != expected_type:
        return None

    return payload


@inject
async def get_current_user(
    token_value: Annotated[str, Depends(oauth2_scheme)],
    dao: FromDishka[DAO],
) -> dto.UserResponse:
    token = await dao.token.get(dto.TokenRequest(access_token=token_value))
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    expire_minutes = settings.get("security.access_token_expire_minutes")
    if token.created_at < datetime.now(UTC) - timedelta(
        minutes=expire_minutes,
    ):
        await dao.token.delete(
            dto.TokenRequest(access_token=token.access_token),
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if decode_token(token_value, expected_type="access") is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token.user
