#!/usr/bin/env python3
"""
Simple test script to verify the authentication system
Run this after starting the application to test the auth endpoints
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_register():
    """Test company and user registration"""
    print("Testing company and user registration...")
    
    register_data = {
        "company_name": "Test Company Inc",
        "company_email": "admin@testcompany.com",
        "industry": "Technology",
        "company_size": "10-50",
        "owner_email": "owner@testcompany.com",
        "owner_username": "testowner",
        "owner_password": "testpassword123",
        "owner_first_name": "John",
        "owner_last_name": "Doe"
    }
    
    response = requests.post(f"{API_BASE}/auth/register", json=register_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Registration successful!")
        print(f"Company ID: {data['company']['id']}")
        print(f"User ID: {data['user']['id']}")
        print(f"Access Token: {data['tokens']['access_token'][:50]}...")
        
        # Save tokens for later tests
        return data['tokens']['access_token'], data['tokens']['refresh_token']
    else:
        print(f"❌ Registration failed: {response.text}")
        return None, None

def test_login():
    """Test user login"""
    print("Testing user login...")
    
    login_data = {
        "email": "owner@testcompany.com",
        "password": "testpassword123",
        "remember_me": False
    }
    
    response = requests.post(f"{API_BASE}/auth/login", json=login_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Login successful!")
        print(f"User: {data['user']['first_name']} {data['user']['last_name']}")
        print(f"Company: {data['company']['name']}")
        print(f"Role: {data['user']['role']}")
        
        return data['tokens']['access_token'], data['tokens']['refresh_token']
    else:
        print(f"❌ Login failed: {response.text}")
        return None, None

def test_get_current_user(access_token):
    """Test getting current user info"""
    print("Testing get current user...")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{API_BASE}/auth/me", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Get current user successful!")
        print(f"User: {data['first_name']} {data['last_name']}")
        print(f"Email: {data['email']}")
        print(f"Company ID: {data['company_id']}")
    else:
        print(f"❌ Get current user failed: {response.text}")

def test_refresh_token(refresh_token):
    """Test token refresh"""
    print("Testing token refresh...")
    
    refresh_data = {"refresh_token": refresh_token}
    response = requests.post(f"{API_BASE}/auth/refresh", json=refresh_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Token refresh successful!")
        print(f"New Access Token: {data['access_token'][:50]}...")
        print(f"New Refresh Token: {data['refresh_token'][:50]}...")
        return data['access_token'], data['refresh_token']
    else:
        print(f"❌ Token refresh failed: {response.text}")
        return None, None

def test_logout(access_token):
    """Test user logout"""
    print("Testing user logout...")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(f"{API_BASE}/auth/logout", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Logout successful!")
        print(f"Message: {data['message']}")
    else:
        print(f"❌ Logout failed: {response.text}")

def main():
    """Run all tests"""
    print("🚀 Starting Authentication System Tests")
    print("=" * 50)
    print(f"Base URL: {BASE_URL}")
    print(f"Time: {datetime.now()}")
    print()
    
    # Test health endpoint
    test_health()
    
    # Test registration
    access_token, refresh_token = test_register()
    
    if access_token:
        print("=" * 50)
        
        # Test login
        login_access_token, login_refresh_token = test_login()
        
        # Test get current user
        test_get_current_user(access_token)
        
        # Test token refresh
        new_access_token, new_refresh_token = test_refresh_token(refresh_token)
        
        # Test logout
        test_logout(access_token)
        
        print("=" * 50)
        print("🎉 All tests completed!")
    else:
        print("❌ Cannot continue tests without successful registration")

if __name__ == "__main__":
    main()
