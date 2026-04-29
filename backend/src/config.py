from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: str = "development"
    secret_key: str = "change-me"

    database_url: str = "postgresql+asyncpg://temporal:temporal@localhost:5432/temporal_agent"
    redis_url: str = "redis://localhost:6379"

    anthropic_api_key: str = ""
    fred_api_key: str = ""

    sentry_dsn: str = ""

    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30

    cors_origins: list[str] = ["http://localhost:3000"]

    @field_validator("secret_key", "jwt_secret")
    @classmethod
    def reject_insecure_defaults(cls, v: str, info: object) -> str:
        if v == "change-me":
            raise ValueError(f"{info} must be set to a secure value via environment variable")
        return v


settings = Settings()
