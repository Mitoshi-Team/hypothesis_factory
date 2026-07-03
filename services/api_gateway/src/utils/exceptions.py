"""Custom application exceptions for the API Gateway service."""


class BaseAppError(Exception):
    """Base exception for all application-specific errors."""

    def __init__(self, message: str) -> None:
        """Initialize the base application error exception.

        Args:
            message: Descriptive error message.
        """
        super().__init__(message)
        self.message = message


class EntityNotFoundError(BaseAppError):
    """Exception raised when a requested resource is not found."""


class ValidationAppError(BaseAppError):
    """Exception raised when validation of application data fails."""


class ServiceUnavailableError(BaseAppError):
    """Exception raised when a required downstream service is unavailable."""
