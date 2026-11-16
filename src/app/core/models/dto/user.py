import uuid
from dataclasses import dataclass


@dataclass
class UserCreate:
    username: str
    password: str


@dataclass
class UserRequest:
    username: str


@dataclass
class UserResponse:
    id: uuid.UUID
    username: str
    password: str
