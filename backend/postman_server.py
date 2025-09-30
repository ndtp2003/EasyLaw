#!/usr/bin/env python3
"""
Simple authentication server for Postman testing.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Optional

# Import FastAPI and related
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from jose import jwt, JWTError
from passlib.context import CryptContext
import uvicorn

# Configuration
JWT_SECRET = "EasyLawSecret2024"
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 1440

# Security setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security_scheme = HTTPBearer()

# FastAPI app
app = FastAPI(
    title="EasyLaw Authentication API",
    description="Authentication system for Postman testing",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for testing (replace with MongoDB later)
users_db = {}

# Pydantic models
class UserLogin(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str

class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    status: str
    created_at: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse

class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

# Helper functions
def hash_password(password: str) -> str:
    """Hash password with bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """Verify JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def validate_password(password: str) -> bool:
    """Validate password strength."""
    if len(password) < 8:
        return False
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    return has_upper and has_lower and has_digit

def get_user_by_email(email: str):
    """Get user by email."""
    return users_db.get(email)

def get_user_by_id(user_id: str):
    """Get user by ID."""
    for email, user in users_db.items():
        if user["id"] == user_id:
            return user
    return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)):
    """Get current user from token."""
    payload = verify_token(credentials.credentials)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

def init_demo_accounts():
    """Initialize demo accounts."""
    demo_accounts = [
        {
            "email": "admin@gmail.com",
            "password": "Admin@12345",
            "role": "admin"
        },
        {
            "email": "user@gmail.com", 
            "password": "User@12345",
            "role": "user"
        }
    ]
    
    for account in demo_accounts:
        if account["email"] not in users_db:
            user_id = f"user_{len(users_db) + 1}"
            users_db[account["email"]] = {
                "id": user_id,
                "email": account["email"],
                "password_hash": hash_password(account["password"]),
                "role": account["role"],
                "status": "active",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }

# Initialize demo accounts on startup
init_demo_accounts()

# API Routes
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "EasyLaw Authentication API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "health": "GET /health",
            "register": "POST /api/v1/auth/register",
            "login": "POST /api/v1/auth/login",
            "profile": "GET /api/v1/auth/me",
            "demo": "GET /api/v1/auth/demo-accounts"
        }
    }

@app.get("/health")
async def health():
    """Health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "users_count": len(users_db)
    }

@app.post("/api/v1/auth/register", response_model=TokenResponse)
async def register(user_data: UserRegister):
    """Register new user."""
    # Validate passwords match
    if user_data.password != user_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Passwords do not match"
        )
    
    # Validate password strength
    if not validate_password(user_data.password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 8 characters with uppercase, lowercase, and number"
        )
    
    # Check if user exists
    if get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
    
    # Create user
    user_id = f"user_{len(users_db) + 1}"
    password_hash = hash_password(user_data.password)
    now = datetime.utcnow()
    
    user_doc = {
        "id": user_id,
        "email": user_data.email,
        "password_hash": password_hash,
        "role": "user",
        "status": "active",
        "created_at": now,
        "updated_at": now
    }
    
    users_db[user_data.email] = user_doc
    
    # Create token
    token_data = {"sub": user_id, "email": user_data.email, "role": "user"}
    access_token = create_access_token(token_data)
    
    # Create response
    user_response = UserResponse(
        id=user_id,
        email=user_data.email,
        role="user",
        status="active",
        created_at=now.isoformat()
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=JWT_EXPIRE_MINUTES * 60,
        user=user_response
    )

@app.post("/api/v1/auth/login", response_model=TokenResponse)
async def login(login_data: UserLogin):
    """User login."""
    # Get user
    user = get_user_by_email(login_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Update last login
    user["last_login"] = datetime.utcnow()
    user["updated_at"] = datetime.utcnow()
    
    # Create token
    expires_delta = timedelta(days=30) if login_data.remember_me else None
    token_data = {"sub": user["id"], "email": user["email"], "role": user["role"]}
    access_token = create_access_token(token_data, expires_delta)
    
    # Calculate expires_in
    if expires_delta:
        expires_in = int(expires_delta.total_seconds())
    else:
        expires_in = JWT_EXPIRE_MINUTES * 60
    
    # Create response
    user_response = UserResponse(
        id=user["id"],
        email=user["email"],
        role=user["role"],
        status=user["status"],
        created_at=user["created_at"].isoformat()
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in,
        user=user_response
    )

@app.get("/api/v1/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information."""
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        role=current_user["role"],
        status=current_user["status"],
        created_at=current_user["created_at"].isoformat()
    )

@app.post("/api/v1/auth/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_user)
):
    """Change user password."""
    # Verify current password
    if not verify_password(password_data.current_password, current_user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    # Validate new passwords match
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="New passwords do not match"
        )
    
    # Validate new password strength
    if not validate_password(password_data.new_password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 8 characters with uppercase, lowercase, and number"
        )
    
    # Update password
    current_user["password_hash"] = hash_password(password_data.new_password)
    current_user["updated_at"] = datetime.utcnow()
    
    return {"message": "Password changed successfully"}

@app.post("/api/v1/auth/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """User logout (client-side token removal)."""
    return {"message": "Logged out successfully"}

@app.get("/api/v1/auth/demo-accounts")
async def get_demo_accounts():
    """Get demo accounts information."""
    return {
        "message": "Demo accounts available for testing",
        "accounts": {
            "admin": {
                "email": "admin@gmail.com",
                "password": "Admin@12345",
                "role": "admin"
            },
            "user": {
                "email": "user@gmail.com", 
                "password": "User@12345",
                "role": "user"
            }
        },
        "usage": {
            "login": "POST /api/v1/auth/login with email/password",
            "register": "POST /api/v1/auth/register with email/password/confirm_password",
            "profile": "GET /api/v1/auth/me with Authorization: Bearer <token>"
        }
    }

@app.get("/api/v1/auth/users")
async def list_users():
    """List all users (for testing)."""
    users = []
    for email, user in users_db.items():
        users.append({
            "id": user["id"],
            "email": user["email"],
            "role": user["role"],
            "status": user["status"],
            "created_at": user["created_at"].isoformat(),
            "last_login": user.get("last_login", {}).get("isoformat", lambda: "Never")() if user.get("last_login") else "Never"
        })
    
    return {"users": users, "total": len(users)}

# Test functions
def test_server_functions():
    """Test server functions."""
    print("=== Testing Server Functions ===")
    
    try:
        # Test password hashing
        test_password = "TestPass123"
        hashed = hash_password(test_password)
        verified = verify_password(test_password, hashed)
        print(f"[OK] Password hashing: {verified}")
        
        # Test JWT tokens
        token_data = {"sub": "test_user", "email": "test@example.com"}
        token = create_access_token(token_data)
        decoded = verify_token(token)
        print(f"[OK] JWT tokens: {decoded.get('email')}")
        
        # Test demo accounts
        demo_count = len(users_db)
        print(f"[OK] Demo accounts loaded: {demo_count}")
        
        print("[OK] All server functions working!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Server test failed: {e}")
        return False

if __name__ == "__main__":
    print("=== EasyLaw Authentication Server for Postman ===")
    
    # Test functions first
    if test_server_functions():
        print("\n[SERVER] Starting server for Postman testing...")
        print("\n[DEMO] Demo Accounts:")
        print("   Admin: admin@gmail.com / Admin@12345")
        print("   User:  user@gmail.com / User@12345")
        
        print("\n[API] Endpoints:")
        print("   Info: GET http://localhost:8000/")
        print("   Health: GET http://localhost:8000/health")
        print("   Register: POST http://localhost:8000/api/v1/auth/register")
        print("   Login: POST http://localhost:8000/api/v1/auth/login")
        print("   Profile: GET http://localhost:8000/api/v1/auth/me")
        print("   Change Password: POST http://localhost:8000/api/v1/auth/change-password")
        print("   Logout: POST http://localhost:8000/api/v1/auth/logout")
        print("   Demo Info: GET http://localhost:8000/api/v1/auth/demo-accounts")
        print("   List Users: GET http://localhost:8000/api/v1/auth/users")
        
        print("\n[DOCS] API Documentation: http://localhost:8000/docs")
        print("\n[START] Starting server on http://localhost:8000...")
        print("[READY] Ready for Postman testing!")
        print("\nPress Ctrl+C to stop server...")
        
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
    else:
        print("[ERROR] Server test failed. Please check configuration.")
        sys.exit(1)
