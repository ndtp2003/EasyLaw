"""
Authentication controller for FastAPI endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from ..schemas.auth import (
    UserRegistration, 
    UserLogin, 
    TokenResponse, 
    UserResponse,
    PasswordChange
)
from ..services.auth_service import AuthService
from ..core.dependencies import get_current_user, require_admin
from ..core.exceptions import (
    AuthenticationError,
    ValidationError,
    ConflictError,
    NotFoundError
)


router = APIRouter()
auth_service = AuthService()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegistration):
    """Register a new user account."""
    try:
        return await auth_service.register_user(user_data)
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    """User login authentication."""
    try:
        return await auth_service.login_user(user_data)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    """Refresh access token."""
    try:
        return await auth_service.refresh_token(refresh_token)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information."""
    try:
        return await auth_service.get_current_user(current_user["user_id"])
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_user)
):
    """Change user password."""
    try:
        success = await auth_service.change_password(
            current_user["user_id"],
            password_data.current_password,
            password_data.new_password
        )
        
        if success:
            return {"message": "Password changed successfully"}
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """User logout (client-side token removal)."""
    # In JWT, logout is handled client-side by removing the token
    # Server-side logout would require token blacklisting
    return {"message": "Logged out successfully"}


@router.post("/admin/deactivate-user")
async def admin_deactivate_user(
    target_user_id: str,
    admin_user: dict = Depends(require_admin)
):
    """Admin endpoint to deactivate a user account."""
    try:
        success = await auth_service.deactivate_user(
            admin_user["user_id"],
            target_user_id
        )
        
        if success:
            return {"message": f"User {target_user_id} deactivated successfully"}
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/admin/init")
async def initialize_admin():
    """Initialize admin user (one-time setup)."""
    try:
        admin_user = await auth_service.ensure_admin_exists()
        return {
            "message": "Admin user initialized successfully",
            "admin_email": admin_user.email,
            "note": "Default password is 'admin123' - please change it immediately"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize admin: {str(e)}"
        )


@router.get("/health")
async def auth_health_check():
    """Auth service health check."""
    return {
        "service": "auth",
        "status": "healthy",
        "endpoints": [
            "POST /register",
            "POST /login", 
            "POST /refresh",
            "GET /me",
            "POST /change-password",
            "POST /logout"
        ]
    }
