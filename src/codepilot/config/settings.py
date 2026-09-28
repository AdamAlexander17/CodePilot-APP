"""Application settings, loaded from environment variables and the .env file."""

from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="CODEPILOT_",
        extra="ignore",
    )

    # --- Application ---
    app_name: str = "CodePilot Enterprise"
    environment: Literal["local", "test", "production"] = "local"
    debug: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # --- LLM ---
    llm_provider: Literal["ollama", "anthropic", "openai"] = "ollama"
    llm_model_fast: str = "qwen2.5-coder:7b"
    llm_model_deep: str = "qwen3:8b"
    llm_base_url: str = "http://localhost:11434"
    llm_api_key: SecretStr | None = None
    llm_temperature: float = 0.0

        # --- Postgres (platform DB: investigations, approvals, audit) ---
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: SecretStr = SecretStr("root")
    postgres_db: str = "Code-Pilot-DB"

    @property
    def postgres_dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:"
            f"{self.postgres_password.get_secret_value()}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            )

    # --- MySQL (target application DB — what CodePilot investigates) ---
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: SecretStr = SecretStr("root")
    mysql_db: str = "CodePilotAI"

    @property
    def mysql_dsn(self) -> str:
        return (
            f"mysql+asyncmy://{self.mysql_user}:"
            f"{self.mysql_password.get_secret_value()}@"
            f"{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"
            )


@lru_cache
def get_settings() -> Settings:
    return Settings()



