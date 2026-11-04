
from typing import Literal
from urllib.parse import quote_plus

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application configuration
    PROJECT_NAME: str = "Grocery POS Billing System"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Literal["development", "production"] = "development"
    DEBUG: bool = False

    # PostgreSQL configuration
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = Field(default=5432, ge=1, le=65535)
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_DB: str = "grocery_pos"

    # Optional direct database URL
    DATABASE_URL: str | None = None

    @property
    def sync_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL

        if not self.POSTGRES_PASSWORD:
            raise ValueError("Database password is not configured.")

        user = quote_plus(self.POSTGRES_USER)
        password = quote_plus(self.POSTGRES_PASSWORD)
        database = quote_plus(self.POSTGRES_DB)

        return (
            f"postgresql://{user}:{password}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{database}"
        )

    # JWT configuration
    SECRET_KEY: str
    ALGORITHM: Literal["HS256"] = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        gt=0,
        le=60,
    )

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, value: str) -> str:
        value = value.strip()

        if len(value) < 32:
            raise ValueError(
                "SECRET_KEY must contain at least 32 characters."
            )

        if value == "pos-grocery-enterprise-secure-jwt-token-key-2026":
            raise ValueError(
                "The old default JWT secret cannot be used."
            )

        return value

    # CORS configuration
    BACKEND_CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000",
        ]
    )

    @model_validator(mode="after")
    def validate_application_configuration(self):
        if not self.DATABASE_URL and not self.POSTGRES_PASSWORD:
            raise ValueError(
                "Configure DATABASE_URL or POSTGRES_PASSWORD."
            )

        if self.ENVIRONMENT == "production" and self.DEBUG:
            raise ValueError(
                "DEBUG must be False in production."
            )

        return self


settings = Settings()
