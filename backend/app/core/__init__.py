"""
Core module for EasyLaw application.
Contains configuration, exceptions, security, and utilities.
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
from .security import security, validate_password_strength
from .dependencies import (
    get_current_user,
    get_current_active_user,
    require_admin,
    require_user_or_admin
)

__all__ = [
    "settings",
    "get_settings",
    "setup_logging",
    "security",
    "validate_password_strength",
    "get_current_user",
    "get_current_active_user",
    "require_admin",
    "require_user_or_admin",
    "AppException",
    "AuthenticationError", 
    "AuthorizationError",
    "ValidationError",
    "NotFoundError",
    "ConflictError",
    "RateLimitError",
    "ExternalServiceError"
]
