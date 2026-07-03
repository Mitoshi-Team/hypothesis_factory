"""Configuration management for the API Gateway service."""

from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file.

    Attributes:
        ENVIRONMENT: The current deployment environment (e.g., development, production).
        DEBUG: Flag to enable debug mode and verbose logging.
        APP_NAME: Name of the microservice.
        HOST: Host address to bind the server.
        PORT: Port number to bind the server.
        CORS_ORIGINS: List of allowed origins for CORS.
        API_PREFIX: API router prefix.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ENVIRONMENT: str = Field(
        default="development", description="Deployment environment"
    )
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    APP_NAME: str = Field(default="api-gateway", description="Application name")
    HOST: str = Field(
        default="0.0.0.0",  # noqa: S104
        description="Host to bind the server",
    )
    PORT: int = Field(default=8000, description="Port to run the application on")
    CORS_ORIGINS: List[str] = Field(
        default=["*"], description="List of allowed CORS origins"
    )
    API_PREFIX: str = Field(default="/api/v1", description="API route prefix")


def get_settings() -> Settings:
    """Retrieve and cache the application settings.

    Returns:
        The settings instance loaded from environment variables.
    """
    return Settings()
