from typing import Any

from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from .providers.api import APICommandProvider
from .providers.db import DbProvider


def get_async_container() -> AsyncContainer:
    providers: list[Any] = [
        FastapiProvider(),
        APICommandProvider(),
        DbProvider(),
    ]
    container = make_async_container(*providers)
    return container
