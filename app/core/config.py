from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    app_base_url: str = "http://localhost:8080"
    app_secret_key: str = Field(default="development-only-change-me", min_length=16)
    database_url: str = "sqlite+pysqlite:///./data/goodtogo.db"
    document_storage_path: str = "./data/documents"
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()

