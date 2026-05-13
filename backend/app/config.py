"""Application settings loaded from environment variables or .env file."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── app ──────────────────────────────────────────────────────────────
    app_name: str = "Rental Platform API"
    environment: str = "development"
    debug: bool = False

    # ── database ─────────────────────────────────────────────────────────
    database_url: str = "sqlite:///./rental_platform.db"

    # ── auth ─────────────────────────────────────────────────────────────
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    auth_hash_algorithm: str = "bcrypt"

    # ── cors ─────────────────────────────────────────────────────────────
    # Comma-separated list of allowed origins.
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings singleton."""
    return Settings()
