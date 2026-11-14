from typing import Any

from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from .providers.api import APICommandProvider


def get_async_container() -> AsyncContainer:
    providers: list[Any] = [FastapiProvider(), APICommandProvider()]
    container = make_async_container(*providers)
    return container
