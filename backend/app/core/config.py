from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="local", alias="APP_ENV")
    app_name: str = Field(default="AI Brief Decoder Lite API", alias="APP_NAME")
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/ai_brief_decoder",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    # Provider
    provider: str = Field(default="fake", alias="PROVIDER")
    fake_provider_mode: str = Field(default="valid", alias="FAKE_PROVIDER_MODE")
    openai_model_name: str = Field(default="openai:gpt-4o-mini", alias="OPENAI_MODEL_NAME")
    provider_timeout_seconds: float = Field(default=30.0, alias="PROVIDER_TIMEOUT_SECONDS")

    # Cache
    cache_ttl_seconds: int = Field(default=86400, alias="CACHE_TTL_SECONDS")

    # Rate limiting: requests per IP per minute on /decode
    rate_limit_per_minute: int = Field(default=30, alias="RATE_LIMIT_PER_MINUTE")

    # Idempotency key TTL
    idempotency_ttl_seconds: int = Field(default=86400, alias="IDEMPOTENCY_TTL_SECONDS")


@lru_cache
def get_settings() -> Settings:
    return Settings()
