from functools import lru_cache
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
from pydantic import field_validator

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://gallery:gallery@localhost:5432/gallery"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:4173,http://127.0.0.1:4173"
    max_upload_bytes: int = 1024 * 1024 * 1024
    redis_url: str = ""
    redis_channel: str = "photo-gallery:events"
    ws_allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @field_validator("redis_url")
    @classmethod
    def validate_redis_url(cls, value: str) -> str:
        if value:
            parsed = urlsplit(value)
            if parsed.scheme not in {"redis", "rediss"} or not parsed.hostname:
                raise ValueError("REDIS_URL must use redis:// or rediss://")
            if any(key.startswith("ssl_") for key in parse_qs(parsed.query)):
                raise ValueError("TLS overrides are not allowed in REDIS_URL")
        return value

    @property
    def ws_origin_list(self) -> list[str]:
        return [origin.strip().rstrip("/") for origin in self.ws_allowed_origins.split(",") if origin.strip()]

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
