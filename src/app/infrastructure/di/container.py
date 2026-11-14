from typing import Any

from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider


def get_async_container() -> AsyncContainer:
    providers: list[Any] = [FastapiProvider()]
    container = make_async_container(*providers)
    return container
