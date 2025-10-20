"""
Configuration management using environment variables
"""

import os

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from netwiz_backend import (
    APP_AUTHOR,
    APP_DESCRIPTION,
    APP_EMAIL,
    APP_NAME,
    APP_VERSION,
    __license__,
    __status__,
    __url__,
)

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables and __init__.py"""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # App Configuration - defaults from __init__.py dunders
    app_name: str = Field(default=APP_NAME, alias="APP_NAME")
    app_version: str = Field(default=APP_VERSION, alias="APP_VERSION")
    app_description: str = Field(default=APP_DESCRIPTION, alias="APP_DESCRIPTION")
    app_author: str = Field(default=APP_AUTHOR, alias="APP_AUTHOR")
    app_email: str = Field(default=APP_EMAIL, alias="APP_EMAIL")
    app_license: str = Field(default=__license__, alias="APP_LICENSE")
    app_url: str = Field(default=__url__, alias="APP_URL")
    app_status: str = Field(default=__status__, alias="APP_STATUS")

    # Environment Configuration
    environment: str = Field(default="prod", alias="ENVIRONMENT")
    debug: bool = Field(
        default_factory=lambda: os.environ.get("ENVIRONMENT", "prod") == "development"
    )
    reload: bool = Field(
        default_factory=lambda: os.environ.get("ENVIRONMENT", "prod") == "development"
    )

    # Server Configuration
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=5000, alias="PORT")

    # Database Configuration (required)
    mongodb_uri: str = Field(alias="MONGODB_URI")
    mongodb_database: str = Field(alias="MONGODB_DATABASE")

    # CORS Configuration
    cors_origins: str = Field(default="*", alias="CORS_ORIGINS")

    @field_validator("cors_origins", mode="after")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # Logging Configuration
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="json", alias="LOG_FORMAT")

    # API Configuration
    api_prefix: str = Field(default="/api", alias="API_PREFIX")

    # JWT Configuration
    jwt_secret_key: str = Field(
        default="your-secret-key-change-in-production", alias="JWT_SECRET_KEY"
    )
    jwt_refresh_secret_key: str = Field(
        default="your-refresh-secret-key-change-in-production",
        alias="JWT_REFRESH_SECRET_KEY",
    )
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(
        default=30, alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    jwt_refresh_token_expire_days: int = Field(
        default=7, alias="JWT_REFRESH_TOKEN_EXPIRE_DAYS"
    )

    # Password Configuration
    password_pepper: str = Field(
        default="NetWizAOSDFAMSDF",
        alias="PASSWORD_PEPPER",
        description="Application-specific pepper for password hashing",
    )
    admin_temp_password: str = Field(
        default="admin",
        alias="ADMIN_TEMP_PASSWORD",
        description="Temporary password for auto-created admin account",
    )


# Create global settings instance
settings = Settings()
