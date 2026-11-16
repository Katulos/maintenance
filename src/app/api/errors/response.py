from dataclasses import dataclass
from typing import Any, ClassVar

import orjson

from ...core.errors.base import ApplicationError, application_error


@dataclass
class ErrorResponse:
    code: str
    message: str
    meta: dict[str, Any] | None

    def to_json(self):
        data = {
            "code": self.code,
            "message": self.message,
            "meta": self.meta,
        }
        dump = orjson.dumps(data)
        return orjson.loads(dump)


@application_error
class InternalServerError(ApplicationError):
    code: ClassVar[str] = "INTERNAL_SERVER_ERROR"
    message: str = "Internal Server Error"
    orig_error: Exception
