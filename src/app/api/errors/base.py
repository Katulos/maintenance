from enum import Enum
from typing import Any, ClassVar

from ...core.errors.base import ApplicationError, application_error


class UnauthorizedReason(Enum):
    MISSING_USER_ID = "MISSING_USER_ID"
    INVALID_AUTH_USER_ID = "INVALID_AUTH_USER_ID"
    MISSING_ACCESS_TOKEN = "MISSING_ACCESS_TOKEN"
    CORRUPTED_ACCESS_TOKEN = "CORRUPTED_ACCESS_TOKEN"
    EMAIL_IS_NOT_VERIFIED = "EMAIL_IS_NOT_VERIFIED"


@application_error
class UnauthorizedError(ApplicationError):
    code: ClassVar[str] = "UNAUTHORIZED"
    reason: UnauthorizedReason
    header: str | None = None
    message: str = "Unauthorized"

    @property
    def meta(self) -> dict[str, Any] | None:
        return {
            "reason": self.reason,
            "header": self.header,
        }
