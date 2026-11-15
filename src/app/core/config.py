import logging
import os
import sys

from dynaconf import Dynaconf, ValidationError, Validator

from .logging import setup_logger

_BASE_DIR = os.getcwd()


settings = Dynaconf(
    settings_files=[
        "?/etc/mnt/settings.ini",
        "?/etc/mnt/.secrets.ini",
        "?/etc/mnt/settings.toml",
        "?/etc/mnt/.secrets.toml",
        "?/etc/mnt/settings.yaml",
        "?/etc/mnt/.secrets.yaml",
        "?/etc/mnt/settings.yml",
        "?/etc/mnt/.secrets.yml",
        "?~/.config/mnt/settings.ini",
        "?~/.config/mnt/.secrets.ini",
        "?~/.config/mnt/settings.toml",
        "?~/.config/mnt/.secrets.toml",
        "?~/.config/mnt/settings.yaml",
        "?~/.config/mnt/.secrets.yaml",
        "?~/.config/mnt/settings.yml",
        "?~/.config/mnt/.secrets.yml",
        os.path.join(_BASE_DIR, "settings.ini"),
        os.path.join(_BASE_DIR, ".secrets.ini"),
        os.path.join(_BASE_DIR, "settings.toml"),
        os.path.join(_BASE_DIR, ".secrets.toml"),
        os.path.join(_BASE_DIR, "settings.yaml"),
        os.path.join(_BASE_DIR, ".secrets.yaml"),
        os.path.join(_BASE_DIR, "settings.yml"),
        os.path.join(_BASE_DIR, ".secrets.yml"),
    ],
)
settings.validators.register(
    # core
    Validator(
        "core.debug",
        is_type_of=bool,
        default=False,
    ),
    ###
    # API
    Validator("api.bind", is_type_of=str, default="127.0.0.1"),
    Validator("api.port", is_type_of=int, default=8000),
    Validator("api.enable_access_log", is_type_of=bool, default=True),
    # Database
    Validator(
        "db.database_url",
        is_type_of=str,
        default="postgresql+asyncpg://devel:devel@db:5432/devel",
    ),
    Validator("db.echo", is_type_of=bool, default=False),
)

try:
    settings.validators.validate_all()
except ValidationError as e:
    setup_logger(loglevel=logging.DEBUG)
    logging.error(e.message)
    sys.exit(1)
