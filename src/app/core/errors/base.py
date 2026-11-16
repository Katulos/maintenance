from dataclasses import dataclass
from typing import Any, ClassVar, TypeVar, dataclass_transform

_T = TypeVar("_T")


@dataclass_transform(kw_only_default=True)
def application_error(cls: type[_T]) -> type[_T]:
    return dataclass(slots=True, kw_only=True)(cls)


@application_error
class ApplicationError(Exception):
    message: str

    code: ClassVar[str]
    status_code: ClassVar[int] = 500

    @property
    def meta(self) -> dict[str, Any] | None:
        return None

    def __str__(self) -> str:
        newline = "\n"
        return f"{self.code}: {self.message}{newline:<6}meta={self.meta}"


@application_error
class AccessDeniedError(ApplicationError):
    code: ClassVar[str] = "ACCESS_DENIED"
    status_code: ClassVar[int] = 403

    message: str = "Access denied"
