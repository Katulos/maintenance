from dataclasses import dataclass


@dataclass
class Token:
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
