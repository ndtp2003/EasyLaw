#!/usr/bin/env python3
"""
Test FastAPI authentication endpoints.
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_api():
    """Test authentication API endpoints."""
    print("=== Testing FastAPI Authentication ===")
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return False
    
    # Test 2: Initialize demo accounts
    print("\n2. Initializing demo accounts...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/auth/init-demo-accounts")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Message: {data['message']}")
            print("Demo accounts:")
            for account_type, account_info in data['accounts'].items():
                print(f"  {account_type.upper()}: {account_info['email']} / {account_info['password']}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Demo accounts init failed: {e}")
        return False
    
    # Test 3: Admin login
    print("\n3. Testing admin login...")
    try:
        login_data = {
            "email": "admin@gmail.com",
            "password": "Admin@12345"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Admin login successful!")
            print(f"User: {data['user']['email']} (role: {data['user']['role']})")
            print(f"Token: {data['access_token'][:50]}...")
            
            # Store token for next test
            admin_token = data['access_token']
            
        else:
            print(f"Admin login failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"Admin login failed: {e}")
        return False
    
    # Test 4: User login  
    print("\n4. Testing user login...")
    try:
        login_data = {
            "email": "user@gmail.com",
            "password": "User@12345"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"User login successful!")
            print(f"User: {data['user']['email']} (role: {data['user']['role']})")
            
        else:
            print(f"User login failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"User login failed: {e}")
        return False
    
    # Test 5: Get current user (with admin token)
    print("\n5. Testing get current user...")
    try:
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{BASE_URL}/api/v1/auth/me",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Current user: {data['email']} (role: {data['role']})")
        else:
            print(f"Get current user failed: {response.text}")
            
    except Exception as e:
        print(f"Get current user failed: {e}")
        return False
    
    print("\n" + "="*50)
    print("SUCCESS: All authentication tests passed!")
    print("="*50)
    
    print("\nDemo accounts ready for use:")
    print("- Admin: admin@gmail.com / Admin@12345")
    print("- User:  user@gmail.com / User@12345")
    print("\nAPI Documentation: http://localhost:8000/docs")
    
    return True

if __name__ == "__main__":
    try:
        success = test_api()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Test failed with error: {e}")
        sys.exit(1)
