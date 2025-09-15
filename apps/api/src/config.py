# src/config.py
import os
from typing import cast
from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Root path — configurable via env var, defaults to localhost
ROOT_PATH = os.getenv("ROOT_PATH", "http://127.0.0.1:8000")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",          # looks for .env in the backend working dir
        env_file_encoding="utf-8",
        extra="ignore", 
        case_sensitive=False,
    )

    # --- Project fields ---
    PROJECT_NAME: str = "Long-Horizon AI API"
    PROJECT_DESCRIPTION: str = "A prototype to test long-horizon API tasks"
   
    model_config = SettingsConfigDict(env_file=".env")
    API_VERSION: str = "/api/v1"
    ROOT: str = ROOT_PATH

    # --- Database fields ---
    DB_URL: str = cast(str, os.getenv("DB_URL"))
    DB_API_KEY: str = cast(str, os.getenv("DB_API_KEY"))
    DB_EMAIL: str = cast(str, os.getenv("DB_EMAIL"))
    DB_PASSWORD: str = cast(str, os.getenv("DB_PASSWORD"))

    # --- OpenAI fields ---
    print(os.getenv("OPENAI_API_KEY", ""))
    OPENAI_API_KEY: str = cast(str, os.getenv("OPENAI_API_KEY", ""))
    OPENAI_MODEL: str = Field(
        default="gpt-4o-mini",  # or your preferred default
        validation_alias=AliasChoices("OPENAI_MODEL", "openai_model"),
    )


settings = Settings()