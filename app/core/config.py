from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    project_name: str = "Organizations Directory API"
    api_version: str = "0.1.0"
    debug: bool = False
    api_key: str = Field(alias="API_KEY")
    database_url: str = Field(
        default="sqlite+aiosqlite:///./app.db",
        alias="DATABASE_URL",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
