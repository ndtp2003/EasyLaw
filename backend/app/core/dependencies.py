"""
FastAPI dependencies for authentication and authorization.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .security import security, extract_user_from_token
from .exceptions import AuthenticationError, AuthorizationError
from ..models.user import UserRole


# HTTP Bearer token scheme
security_scheme = HTTPBearer()


async def get_current_user_token(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme)
) -> dict:
    """Extract and verify current user from JWT token."""
    try:
        token_data = security.verify_token(credentials.credentials)
        user_info = extract_user_from_token(token_data)
        
        if not user_info.get("user_id"):
            raise AuthenticationError("Invalid token payload")
        
        return user_info
    
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    current_user: dict = Depends(get_current_user_token)
) -> dict:
    """Get current authenticated user."""
    return current_user


async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Get current active user (can add additional checks here)."""
    # TODO: Check user status in database if needed
    return current_user


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Require admin role for access."""
    if current_user.get("role") != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_user_or_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Require user or admin role for access."""
    user_role = current_user.get("role")
    if user_role not in [UserRole.USER.value, UserRole.ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User access required"
        )
    return current_user


class RoleChecker:
    """Role-based access control checker."""
    
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles
    
    def __call__(self, current_user: dict = Depends(get_current_user)):
        if current_user.get("role") not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(self.allowed_roles)}"
            )
        return current_user


# Pre-defined role checkers
admin_required = RoleChecker([UserRole.ADMIN.value])
user_required = RoleChecker([UserRole.USER.value, UserRole.ADMIN.value])
