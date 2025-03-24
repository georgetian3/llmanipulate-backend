from typing import Literal
from uuid import uuid4

from pydantic import UUID4
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="", env_file=".env", env_file_encoding="utf-8", extra="allow"
    )

    database_host: str | None = None
    database_port: int | None = None
    database_name: str | None = "llmanipulate.sqlite3"
    database_username: str | None = None
    database_password: str | None = None
    database_driver: str | None = "sqlite+aiosqlite"

    frontend_url: str = "*"

    load_fixtures: bool = True

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    admin_id: UUID4 = uuid4()


SETTINGS = Settings()
