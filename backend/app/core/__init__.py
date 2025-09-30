"""
Core module for EasyLaw application.
Contains configuration, exceptions, and utilities.
"""

from .config import settings, get_settings
from .exceptions import (
    AppException,
    AuthenticationError,
    AuthorizationError,
    ValidationError,
    NotFoundError,
    ConflictError,
    RateLimitError,
    ExternalServiceError
)
from .logging import setup_logging

__all__ = [
    "settings",
    "get_settings",
    "setup_logging",
    "AppException",
    "AuthenticationError", 
    "AuthorizationError",
    "ValidationError",
    "NotFoundError",
    "ConflictError",
    "RateLimitError",
    "ExternalServiceError"
]
