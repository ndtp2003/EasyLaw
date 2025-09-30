"""
Security utilities for JWT token handling and password management.
"""

from jose import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from passlib.hash import bcrypt

from .config import settings
from .exceptions import AuthenticationError


class SecurityUtils:
    """Security utilities for password hashing and JWT tokens."""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.algorithm = settings.jwt_algorithm
        self.secret_key = settings.jwt_secret
        self.expire_minutes = settings.jwt_expire_minutes
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        # Bcrypt has a 72-byte limit, truncate if necessary
        if len(password.encode('utf-8')) > 72:
            password = password[:72]
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        # Bcrypt has a 72-byte limit, truncate if necessary
        if len(plain_password.encode('utf-8')) > 72:
            plain_password = plain_password[:72]
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=self.expire_minutes)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create a JWT refresh token (longer expiry)."""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=30)  # 30 days for refresh
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.JWTError:
            raise AuthenticationError("Invalid token")
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decode token without verification (for debugging)."""
        try:
            return jwt.decode(token, options={"verify_signature": False})
        except Exception:
            return {}


# Global security instance
security = SecurityUtils()


def validate_password_strength(password: str) -> bool:
    """Validate password strength requirements."""
    if len(password) < 8:
        return False
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    
    return has_upper and has_lower and has_digit


def generate_user_token_data(user_id: str, email: str, role: str) -> Dict[str, Any]:
    """Generate token payload data for user."""
    return {
        "sub": user_id,  # Subject (user ID)
        "email": email,
        "role": role,
        "scope": "access"
    }


def extract_user_from_token(token_data: Dict[str, Any]) -> Dict[str, str]:
    """Extract user information from token payload."""
    return {
        "user_id": token_data.get("sub"),
        "email": token_data.get("email"),
        "role": token_data.get("role")
    }
