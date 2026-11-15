import pathlib
from collections.abc import Iterator
from importlib.resources import as_file, files

from .. import alembic


def get_alembic_config_path() -> Iterator[pathlib.Path]:
    source = files(alembic).joinpath("alembic.ini")
    with as_file(source) as path:
        yield path
