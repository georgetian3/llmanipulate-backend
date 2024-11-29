import os
from dataclasses import dataclass
from typing import Any, TypeVar

from dotenv import load_dotenv


class NoDefault: ...


class MissingEnvironmentVariable(Exception): ...


T = TypeVar("T")


def get_env(variable: str, default: T | NoDefault = NoDefault()) -> str | T:
    try:
        return os.environ[variable]
    except KeyError:
        if isinstance(default, NoDefault):
            raise MissingEnvironmentVariable(
                f"Missing environment variable: {variable}"
            )
        return default


def int_or_none(x: Any) -> int | None:
    try:
        return int(x)
    except Exception:
        return None


load_dotenv()



@dataclass
class DatabaseConfig:
    HOST: str | None = get_env("DATABASE_HOST", "localhost")
    PORT: int = int_or_none(get_env("DATABASE_PORT", 5432))
    DATABASE: str = get_env("DATABASE_DATABASE", "myapp_db")
    USERNAME: str = get_env("DATABASE_USERNAME", "myapp_user")
    PASSWORD: str = get_env("DATABASE_PASSWORD", "secure_password")
    DRIVERNAME: str = get_env("DATABASE_DRIVERNAME", "postgresql+asyncpg")




@dataclass
class ServerConfig:
    PORT: int = int(get_env("SERVER_PORT", 8000))
    WORKERS: int = int(get_env("SERVER_WORKERS", 1))

@dataclass
class AuthConfig:
    ADMIN_ID: str | None = get_env("ADMIN_ID", None)