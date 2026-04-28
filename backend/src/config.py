from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")

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


settings = Settings()
