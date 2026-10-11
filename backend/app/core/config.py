import os

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict

    class Settings(BaseSettings):
        PROJECT_NAME: str = "Lumbung ERP"
        VERSION: str = "0.1.0"
        API_V1_PREFIX: str = "/api/v1"

        # Environment
        ENVIRONMENT: str = "development"
        DEBUG: bool = True
        DEMO_MODE: bool = True

        # Security
        SECRET_KEY: str = "insecure-secret-key-change-in-production-min-32-chars-long"
        ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
        REFRESH_TOKEN_EXPIRE_DAYS: int = 14

        # CORS
        FRONTEND_ORIGIN: str = "http://localhost:5173"

        # Database
        DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/lumbung"

        # Integrations (Optional in dev, fake mode enabled if not provided)
        MIDTRANS_SERVER_KEY: str = ""
        MIDTRANS_CLIENT_KEY: str = ""
        MIDTRANS_IS_PRODUCTION: bool = False
        TELEGRAM_BOT_TOKEN: str = ""
        RESEND_API_KEY: str = ""
        INTERNAL_JOB_SECRET: str = "dev-internal-secret"

        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            case_sensitive=True,
            extra="ignore",
        )

except ImportError:
    from dataclasses import dataclass

    @dataclass
    class Settings:  # type: ignore[no-redef]
        PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Lumbung ERP")
        VERSION: str = "0.1.0"
        API_V1_PREFIX: str = "/api/v1"

        # Environment
        ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
        DEBUG: bool = os.getenv("DEBUG", "true").lower() in ("true", "1")
        DEMO_MODE: bool = os.getenv(
            "DEMO_MODE", "true").lower() in ("true", "1")

        # Security
        SECRET_KEY: str = os.getenv(
            "SECRET_KEY", "insecure-secret-key-change-in-production-min-32-chars-long")
        ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
        REFRESH_TOKEN_EXPIRE_DAYS: int = int(
            os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "14"))

        # CORS
        FRONTEND_ORIGIN: str = os.getenv(
            "FRONTEND_ORIGIN", "http://localhost:5173")

        # Database
        DATABASE_URL: str = os.getenv(
            "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/lumbung")

        # Integrations
        MIDTRANS_SERVER_KEY: str = os.getenv("MIDTRANS_SERVER_KEY", "")
        MIDTRANS_CLIENT_KEY: str = os.getenv("MIDTRANS_CLIENT_KEY", "")
        MIDTRANS_IS_PRODUCTION: bool = os.getenv(
            "MIDTRANS_IS_PRODUCTION", "false").lower() in ("true", "1")
        TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
        RESEND_API_KEY: str = os.getenv("RESEND_API_KEY", "")
        INTERNAL_JOB_SECRET: str = os.getenv(
            "INTERNAL_JOB_SECRET", "dev-internal-secret")


settings = Settings()
