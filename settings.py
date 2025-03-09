from datetime import datetime
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )

    database_host: str | None = None
    database_port: int | None = None
    database_name: str | None = "llmanipulate.sqlite3"
    database_username: str | None = None
    database_password: str | None = None
    database_driver: str | None = "sqlite+aiosqlite"

    frontend_url: str = "*"

    secret: str = "SECRET"

    auth_strategy: Literal["jwt", "redis"] = "jwt"

    redis_host: str | None = "localhost"
    redis_port: int | None = 6379

    oauth_google_client_id: str | None = None
    oauth_google_client_secret: str | None = None
    oauth_github_client_id: str | None = None
    oauth_github_client_secret: str | None = None
    oauth_facebook_client_id: str | None = None
    oauth_facebook_client_secret: str | None = None

    load_fixtures: bool = True

    access_token_lifetime_seconds: int = (
        datetime(9999, 12, 31) - datetime.now()
    ).seconds

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"


settings = Settings()
