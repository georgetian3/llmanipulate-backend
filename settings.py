from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")

    database_host: str | None = None
    database_port: int | None = None
    database_name: str | None = None
    database_username: str | None = None
    database_password: str | None = None
    database_driver: str | None = None

    api_url: str
    api_key: str

    frontend_url: str

    admin_id: str | None = None

    secret: str

    redis_host: str
    redis_port: int

    oauth_google_client_id: str | None = None
    oauth_google_client_secret: str | None = None
    oauth_github_client_id: str | None = None
    oauth_github_client_secret: str | None = None
    oauth_facebook_client_id: str | None = None
    oauth_facebook_client_secret: str | None = None


settings = Settings()
