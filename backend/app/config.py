"""Application configuration.

All settings are read from environment variables (or a .env file) and validated
at startup. Importing `settings` anywhere gives a single typed source of truth;
there are no scattered os.getenv calls elsewhere in the codebase.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = "postgresql+psycopg://tracepilot:tracepilot@localhost:5432/tracepilot"

    # Auth / JWT
    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Cache / jobs
    REDIS_URL: str = "redis://localhost:6379/0"

    # Health checker
    HEALTH_CHECK_INTERVAL_SECONDS: int = 60

    # App
    ENVIRONMENT: str = "local"
    DEBUG: bool = True
    CORS_ORIGINS: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
