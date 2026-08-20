from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    # Database
    # Option 1: Full connection URL (recommended for Render external URL)
    DATABASE_CONNECTION_URL: str | None = None

    # Option 2: Individual components
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "book_store"
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = ""

    # JWT
    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Server
    APP_NAME: str = "Book Store API"
    DEBUG: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def DATABASE_URL(self) -> str:
        """
        Return the full connection URL if provided.
        Otherwise fall back to a local SQLite database so the app works
        out-of-the-box without an external PostgreSQL server.
        """
        if self.DATABASE_CONNECTION_URL:
            return self.DATABASE_CONNECTION_URL
        # Local dev fallback — create ./bookstore.db in the Backend folder
        return "sqlite:///./bookstore.db"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()