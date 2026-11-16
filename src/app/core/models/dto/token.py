import uuid
from dataclasses import dataclass
from datetime import datetime

from .user import UserResponse


@dataclass
class TokenCreate:
    access_token: str
    user_id: uuid.UUID


@dataclass
class TokenRequest:
    access_token: str


@dataclass
class TokenResponse:
    access_token: str
    created_at: datetime
    user: UserResponse


@dataclass
class TokenApiResponse:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
