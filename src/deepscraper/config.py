"""Application configuration powered by Pydantic settings."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the scraping platform."""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="allow",
        env_prefix=""
    )

    deepseek_api_key: Optional[str] = Field(default=None, alias="DEEPSEEK_API_KEY")
    deepseek_base_url: str = Field(default="https://api.deepseek.com/v1", alias="DEEPSEEK_BASE_URL")

    postgres_dsn: str = Field(alias="POSTGRES_DSN")
    redis_url: str = Field(alias="REDIS_URL")

    minio_endpoint: str = Field(alias="MINIO_ENDPOINT")
    minio_access_key: str = Field(alias="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(alias="MINIO_SECRET_KEY")
    minio_bucket: str = Field(alias="MINIO_BUCKET")
    minio_secure: bool = Field(default=False, alias="MINIO_SECURE")

    proxy_list_path: Path = Field(default=Path("./proxies.txt"), alias="PROXY_LIST_PATH")
    playwright_stealth: bool = Field(default=True, alias="PLAYWRIGHT_STEALTH")
    captcha_provider: str = Field(default="twocaptcha", alias="CAPTCHA_PROVIDER")
    captcha_api_key: Optional[str] = Field(default=None, alias="CAPTCHA_API_KEY")

    headless: bool = Field(default=True, alias="HEADLESS")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    page_timeout: int = Field(default=30_000, alias="PAGE_TIMEOUT")
    max_concurrency: int = Field(default=4, alias="MAX_CONCURRENCY")
    export_dir: Path = Field(default=Path("./exports"), alias="EXPORT_DIR")

    @property
    def proxy_list(self) -> List[str]:
        if not self.proxy_list_path.exists():
            return []
        return [line.strip() for line in self.proxy_list_path.read_text().splitlines() if line.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()


__all__ = ["Settings", "get_settings"]