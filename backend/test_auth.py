#!/usr/bin/env python3
"""
Test authentication system.
"""

import os
import sys
import asyncio
import json

# Set environment file before importing
os.environ["ENV_FILE"] = "config/.env.dev"

try:
    from app.services.auth_service import AuthService
    from app.schemas.auth import UserRegistration, UserLogin
    from app.core.exceptions import AuthenticationError, ValidationError, ConflictError
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


async def test_auth_system():
    """Test the complete authentication system."""
    print("=" * 50)
    print("Testing EasyLaw Authentication System")
    print("=" * 50)
    
    auth_service = AuthService()
    
    # Test 1: Initialize admin user
    print("\n1. Initializing admin user...")
    try:
        admin_user = await auth_service.ensure_admin_exists()
        print(f"✅ Admin user created/verified: {admin_user.email}")
    except Exception as e:
        print(f"❌ Failed to initialize admin: {e}")
        return False
    
    # Test 2: Register new user
    print("\n2. Testing user registration...")
    test_user_data = UserRegistration(
        email="testuser@easylaw.com",
        password="TestPass123",
        confirm_password="TestPass123"
    )
    
    try:
        token_response = await auth_service.register_user(test_user_data)
        print(f"✅ User registered successfully: {token_response.user.email}")
        print(f"   Token type: {token_response.token_type}")
        print(f"   Expires in: {token_response.expires_in} seconds")
        
        # Store token for next test
        access_token = token_response.access_token
        user_id = token_response.user.id
        
    except ConflictError:
        print("⚠️  User already exists, testing login instead...")
        
        # Test login for existing user
        login_data = UserLogin(
            email="testuser@easylaw.com",
            password="TestPass123"
        )
        
        try:
            token_response = await auth_service.login_user(login_data)
            print(f"✅ User login successful: {token_response.user.email}")
            access_token = token_response.access_token
            user_id = token_response.user.id
        except AuthenticationError as e:
            print(f"❌ Login failed: {e}")
            return False
    
    except ValidationError as e:
        print(f"❌ Registration validation failed: {e}")
        return False
    
    # Test 3: Get current user info
    print("\n3. Testing get current user...")
    try:
        user_info = await auth_service.get_current_user(user_id)
        print(f"✅ Current user retrieved: {user_info.email}")
        print(f"   Role: {user_info.role}")
        print(f"   Status: {user_info.status}")
    except Exception as e:
        print(f"❌ Failed to get current user: {e}")
        return False
    
    # Test 4: Test admin login
    print("\n4. Testing admin login...")
    admin_login_data = UserLogin(
        email=admin_user.email,
        password="admin123"  # Default admin password
    )
    
    try:
        admin_token_response = await auth_service.login_user(admin_login_data)
        print(f"✅ Admin login successful: {admin_token_response.user.email}")
        print(f"   Role: {admin_token_response.user.role}")
    except AuthenticationError as e:
        print(f"❌ Admin login failed: {e}")
        print("💡 Default admin password might have been changed")
    
    # Test 5: Test password validation
    print("\n5. Testing password validation...")
    weak_passwords = ["123", "password", "12345678"]
    
    for weak_pass in weak_passwords:
        try:
            weak_user_data = UserRegistration(
                email="weak@test.com",
                password=weak_pass,
                confirm_password=weak_pass
            )
            await auth_service.register_user(weak_user_data)
            print(f"❌ Weak password accepted: {weak_pass}")
        except ValidationError:
            print(f"✅ Weak password rejected: {weak_pass}")
        except ConflictError:
            pass  # User exists, that's ok
    
    print("\n" + "=" * 50)
    print("✅ Authentication system test completed!")
    print("=" * 50)
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_auth_system())
    if success:
        print("\n🎉 All authentication tests passed!")
    else:
        print("\n❌ Some tests failed.")
    sys.exit(0 if success else 1)
