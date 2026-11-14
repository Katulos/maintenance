from typing import Any

from dishka import AsyncContainer, make_async_container


def get_async_container() -> AsyncContainer:
    providers: list[Any] = []
    container = make_async_container(*providers)
    return container
