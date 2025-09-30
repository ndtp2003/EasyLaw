"""
Authentication schemas for API validation.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
from app.models.user import UserRole, UserStatus


class UserRegistration(BaseModel):
    """User registration schema."""
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=100, description="User password")
    confirm_password: str = Field(..., description="Password confirmation")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        # Add password strength validation
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "StrongPass123",
                "confirm_password": "StrongPass123"
            }
        }


class UserLogin(BaseModel):
    """User login schema."""
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")
    remember_me: bool = Field(default=False, description="Extended session duration")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "StrongPass123",
                "remember_me": false
            }
        }


class UserResponse(BaseModel):
    """User response schema."""
    
    id: str = Field(..., description="User ID")
    email: EmailStr = Field(..., description="User email")
    role: UserRole = Field(..., description="User role")
    status: UserStatus = Field(..., description="User status")
    created_at: str = Field(..., description="Creation timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "email": "user@example.com",
                "role": "user",
                "status": "active",
                "created_at": "2024-01-01T12:00:00Z"
            }
        }


class TokenResponse(BaseModel):
    """JWT token response schema."""
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: UserResponse = Field(..., description="User information")
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIs...",
                "token_type": "bearer",
                "expires_in": 86400,
                "user": {
                    "id": "507f1f77bcf86cd799439011",
                    "email": "user@example.com",
                    "role": "user",
                    "status": "active",
                    "created_at": "2024-01-01T12:00:00Z"
                }
            }
        }


class PasswordReset(BaseModel):
    """Password reset request schema."""
    
    email: EmailStr = Field(..., description="User email address")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }


class PasswordChange(BaseModel):
    """Password change schema."""
    
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password")
    confirm_password: str = Field(..., description="New password confirmation")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "current_password": "OldPass123",
                "new_password": "NewStrongPass456",
                "confirm_password": "NewStrongPass456"
            }
        }
