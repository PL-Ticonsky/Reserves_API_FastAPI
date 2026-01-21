"""
app/core/config.py

Purpose:
- Centralize application configuration loaded from environment variables.
- Provide a single `settings` object used across the app (DB, JWT, timezone).

Why this exists:
- Avoid hardcoding secrets/URLs in code.
- Keep configuration consistent between the API runtime and migrations.
- Validate required environment variables early.

Usage:
    from app.core.config import settings
    print(settings.database_url)

Notes:
- `.env` is for local development and is NOT committed to git.
- `.env.example` documents required variables for new setups.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    database_url: str

    # JWT
    jwt_secret: str
    jwt_expires_minutes: int = 60

    # Provider settings (single provider MVP)
    provider_timezone: str = "America/Bogota"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
