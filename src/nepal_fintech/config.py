"""Application configuration loaded from .env via pydantic-settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration — all values overridable via .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM
    llm_model: str = "gpt-4o-mini"
    llm_api_key: str = ""
    llm_base_url: str | None = None

    # Encryption (Fernet key)
    encryption_key: str = ""

    # Database
    db_path: str = "nepal_fintech.db"

    # ChromaDB
    chroma_persist_dir: str = "chroma_data"

    # App server
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False


settings = Settings()
