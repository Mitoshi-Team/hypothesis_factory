"""Dependency injection utilities for the API endpoints."""

from src.config import Settings, get_settings


def get_app_settings() -> Settings:
    """Dependency injection helper to retrieve application settings.

    Returns:
        The Settings instance configured for the application.
    """
    return get_settings()
