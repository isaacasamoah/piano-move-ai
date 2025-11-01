"""Application configuration using environment variables."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Twilio credentials (optional - set these in Railway dashboard)
    twilio_account_sid: str = "not_set"
    twilio_auth_token: str = "not_set"
    twilio_phone_number: str = "not_set"

    # Anthropic API (optional for Phase 1)
    anthropic_api_key: str = "not_set"

    # Database (optional, defaults to SQLite)
    database_url: str = "sqlite:///./pianomove.db"

    # Application settings
    app_name: str = "PianoMove AI"
    debug: bool = False

    # Server URL for Twilio webhooks (set this to your deployed URL)
    server_url: str = "http://localhost:8000"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
