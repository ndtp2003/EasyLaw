"""
Authentication service for business logic.
"""

from typing import Optional, Dict, Any
from datetime import timedelta

from ..repositories.user_repository import UserRepository
from ..models.user import UserInDB, UserRole, UserStatus
from ..schemas.auth import UserRegistration, UserLogin, TokenResponse, UserResponse
from ..core.security import security, validate_password_strength, generate_user_token_data
from ..core.exceptions import (
    AuthenticationError, 
    ValidationError, 
    ConflictError,
    NotFoundError
)


class AuthService:
    """Authentication service for user management."""
    
    def __init__(self):
        self.user_repo = UserRepository()
    
    async def register_user(self, registration_data: UserRegistration) -> TokenResponse:
        """Register a new user."""
        # Validate password strength
        if not validate_password_strength(registration_data.password):
            raise ValidationError(
                "Password must be at least 8 characters with uppercase, lowercase, and number"
            )
        
        # Hash password
        password_hash = security.hash_password(registration_data.password)
        
        # Create user data
        user_data = {
            "email": registration_data.email,
            "password_hash": password_hash,
            "role": UserRole.USER.value,
            "status": UserStatus.ACTIVE.value
        }
        
        try:
            # Create user in database
            user = await self.user_repo.create_user(user_data)
            
            # Generate tokens
            token_data = generate_user_token_data(
                str(user.id), 
                user.email, 
                user.role
            )
            
            access_token = security.create_access_token(token_data)
            refresh_token = security.create_refresh_token(token_data)
            
            # Create response
            user_response = UserResponse(
                id=str(user.id),
                email=user.email,
                role=user.role,
                status=user.status,
                created_at=user.created_at.isoformat()
            )
            
            return TokenResponse(
                access_token=access_token,
                token_type="bearer",
                expires_in=security.expire_minutes * 60,
                user=user_response
            )
            
        except ConflictError:
            raise ConflictError("User with this email already exists")
    
    async def login_user(self, login_data: UserLogin) -> TokenResponse:
        """Authenticate user login."""
        # Get user by email
        user = await self.user_repo.get_user_by_email(login_data.email)
        
        if not user:
            raise AuthenticationError("Invalid email or password")
        
        # Verify password
        if not security.verify_password(login_data.password, user.password_hash):
            raise AuthenticationError("Invalid email or password")
        
        # Check if user is active
        if not user.is_active():
            raise AuthenticationError("Account is deactivated")
        
        # Update last login
        await self.user_repo.update_last_login(str(user.id))
        
        # Generate tokens
        token_data = generate_user_token_data(
            str(user.id), 
            user.email, 
            user.role
        )
        
        # Extended session if remember_me
        expires_delta = None
        if login_data.remember_me:
            expires_delta = timedelta(days=30)
        
        access_token = security.create_access_token(token_data, expires_delta)
        refresh_token = security.create_refresh_token(token_data)
        
        # Create response
        user_response = UserResponse(
            id=str(user.id),
            email=user.email,
            role=user.role,
            status=user.status,
            created_at=user.created_at.isoformat()
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=(expires_delta.total_seconds() if expires_delta else security.expire_minutes * 60),
            user=user_response
        )
    
    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token."""
        try:
            # Verify refresh token
            token_data = security.verify_token(refresh_token)
            
            if token_data.get("type") != "refresh":
                raise AuthenticationError("Invalid refresh token")
            
            # Get user
            user_id = token_data.get("sub")
            user = await self.user_repo.get_user_by_id(user_id)
            
            if not user or not user.is_active():
                raise AuthenticationError("User not found or inactive")
            
            # Generate new access token
            new_token_data = generate_user_token_data(
                str(user.id), 
                user.email, 
                user.role
            )
            
            access_token = security.create_access_token(new_token_data)
            
            # Create response
            user_response = UserResponse(
                id=str(user.id),
                email=user.email,
                role=user.role,
                status=user.status,
                created_at=user.created_at.isoformat()
            )
            
            return TokenResponse(
                access_token=access_token,
                token_type="bearer",
                expires_in=security.expire_minutes * 60,
                user=user_response
            )
            
        except Exception as e:
            raise AuthenticationError("Invalid refresh token")
    
    async def get_current_user(self, user_id: str) -> UserResponse:
        """Get current user information."""
        user = await self.user_repo.get_user_by_id(user_id)
        
        if not user:
            raise NotFoundError("User not found")
        
        return UserResponse(
            id=str(user.id),
            email=user.email,
            role=user.role,
            status=user.status,
            created_at=user.created_at.isoformat()
        )
    
    async def change_password(
        self, 
        user_id: str, 
        current_password: str, 
        new_password: str
    ) -> bool:
        """Change user password."""
        # Get user
        user = await self.user_repo.get_user_by_id(user_id)
        
        if not user:
            raise NotFoundError("User not found")
        
        # Verify current password
        if not security.verify_password(current_password, user.password_hash):
            raise AuthenticationError("Current password is incorrect")
        
        # Validate new password
        if not validate_password_strength(new_password):
            raise ValidationError(
                "Password must be at least 8 characters with uppercase, lowercase, and number"
            )
        
        # Hash new password
        new_password_hash = security.hash_password(new_password)
        
        # Update password
        success = await self.user_repo.change_password(user_id, new_password_hash)
        
        if not success:
            raise ValidationError("Failed to update password")
        
        return True
    
    async def ensure_admin_exists(self) -> UserInDB:
        """Ensure admin user exists."""
        return await self.user_repo.ensure_admin_exists()
    
    async def validate_admin_access(self, user_id: str) -> bool:
        """Validate if user has admin access."""
        user = await self.user_repo.get_user_by_id(user_id)
        return user and user.is_admin() and user.is_active()
    
    async def deactivate_user(self, admin_id: str, target_user_id: str) -> bool:
        """Admin deactivate user account."""
        # Validate admin access
        if not await self.validate_admin_access(admin_id):
            raise AuthenticationError("Admin access required")
        
        # Cannot deactivate yourself
        if admin_id == target_user_id:
            raise ValidationError("Cannot deactivate your own account")
        
        # Deactivate user
        success = await self.user_repo.deactivate_user(target_user_id)
        
        if not success:
            raise NotFoundError("User not found")
        
        return True
