#!/usr/bin/env python3
"""
Test script to verify AI authentication is working
"""

import requests
import json

def test_ai_endpoints():
    """Test AI endpoints to debug authentication issues"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing AI Endpoints Authentication")
    print("=" * 50)
    
    # Test 1: Health endpoint (should work without auth)
    print("1. Testing AI Health Endpoint (no auth required)...")
    try:
        response = requests.get(f"{base_url}/ai/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # Test 2: Analyze endpoint (requires auth)
    print("2. Testing AI Analyze Endpoint (auth required)...")
    try:
        response = requests.post(
            f"{base_url}/ai/analyze",
            json={"prompt": "test task", "context": "test context"}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Correctly returns 401 Unauthorized (as expected without auth)")
        else:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    print("💡 Next Steps:")
    print("   1. Make sure you're logged in to the frontend")
    print("   2. Check browser cookies for 'access_token'")
    print("   3. Try the AI button from a logged-in session")

if __name__ == "__main__":
    test_ai_endpoints()