from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: str = "development"

    database_url: str = "postgresql+asyncpg://temporal:temporal@localhost:5432/temporal_agent"
    redis_url: str = "redis://localhost:6379"

    anthropic_api_key: str = ""
    fred_api_key: str = ""
    eia_api_key: str = ""

    sentry_dsn: str = ""

    cors_origins: list[str] = ["http://localhost:3000"]


settings = Settings()
