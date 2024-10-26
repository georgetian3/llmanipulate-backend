import os
from dataclasses import dataclass, field
from typing import Any

from dotenv import load_dotenv


class NoDefault: ...


class MissingEnvironmentVariable(Exception): ...


def get_env(variable: str, default: Any = NoDefault()) -> str:
    try:
        return os.environ[variable]
    except KeyError:
        if isinstance(default, NoDefault):
            raise MissingEnvironmentVariable(
                f"Missing environment variable: {variable}"
            )
        return str(default)


load_dotenv()


@dataclass
class DatabaseConfig:
    HOST: str = get_env("DATABASE_HOST")
    PORT: int = int(get_env("DATABASE_PORT"))
    DATABASE: str = get_env("DATABASE_DATABASE")
    USERNAME: str = get_env("DATABASE_USERNAME")
    PASSWORD: str = get_env("DATABASE_PASSWORD")
    DRIVERNAME: str = get_env("DATABASE_DRIVERNAME")


@dataclass
class ServerConfig:
    PORT: int = int(get_env("SERVER_PORT", 8000))
    WORKERS: int = int(get_env("SERVER_WORKERS", 1))


@dataclass
class Config:
    DATABASE: DatabaseConfig = field(default_factory=DatabaseConfig)
    SERVER: ServerConfig = field(default_factory=ServerConfig)
