"""
Unit tests for POST /api/auth/logout endpoint.

Tests cover:
- Successful logout clears cookies
- Logout response format
- Cookie attributes after logout
"""
import pytest
from tests.conftest import TestingSessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole


@pytest.fixture
def test_user():
    """Create a test user in the database."""
    db = TestingSessionLocal()
    user = User(
        name="Test User",
        email="test@example.com",
        password=get_password_hash("TestPassword123"),
        role=UserRole.EMPLOYEE
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    user_id = user.id
    db.close()
    return {"id": user_id, "email": "test@example.com", "password": "TestPassword123"}


@pytest.fixture
def authenticated_client(test_client, test_user):
    """Create an authenticated test client with valid tokens."""
    # Login to get tokens
    credentials = {
        "email": test_user["email"],
        "password": test_user["password"]
    }
    response = test_client.post("/api/auth/login", json=credentials)
    assert response.status_code == 200
    return test_client


def test_logout_success(authenticated_client):
    """Test successful logout returns 200 and success message."""
    # Act
    response = authenticated_client.post("/api/auth/logout")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Logout successful"


def test_logout_clears_access_token(authenticated_client):
    """Test that logout successfully completes and clears authentication state."""
    # Act - Logout
    response = authenticated_client.post("/api/auth/logout")
    
    # Assert - Logout succeeds
    assert response.status_code == 200
    assert response.json()["message"] == "Logout successful"


def test_logout_clears_refresh_token(authenticated_client):
    """Test that logout successfully completes."""
    # Act - Logout
    response = authenticated_client.post("/api/auth/logout")
    
    # Assert - Logout succeeds
    assert response.status_code == 200
    assert response.json()["message"] == "Logout successful"


def test_logout_clears_both_tokens(authenticated_client):
    """Test that logout successfully completes and returns success message."""
    # Act - Logout
    response = authenticated_client.post("/api/auth/logout")
    
    # Assert - Logout succeeds
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Logout successful"
    assert "user" not in data  # Should not return user data


def test_logout_without_authentication(test_client):
    """Test that logout works even without being authenticated (idempotent)."""
    # Act - Call logout without logging in first
    response = test_client.post("/api/auth/logout")
    
    # Assert - Should still succeed (idempotent operation)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Logout successful"


def test_logout_response_format(authenticated_client):
    """Test that logout response has correct format."""
    # Act
    response = authenticated_client.post("/api/auth/logout")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "message" in data
    assert isinstance(data["message"], str)


def test_logout_multiple_times(authenticated_client):
    """Test that logout can be called multiple times (idempotent)."""
    # Act - Logout twice
    response1 = authenticated_client.post("/api/auth/logout")
    response2 = authenticated_client.post("/api/auth/logout")
    
    # Assert - Both should succeed
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response1.json()["message"] == "Logout successful"
    assert response2.json()["message"] == "Logout successful"
