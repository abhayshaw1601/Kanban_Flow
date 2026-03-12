"""
Unit tests for POST /api/auth/refresh endpoint.

Tests cover:
- Successful token refresh with valid refresh token
- Invalid refresh token rejection
- Missing refresh token handling
- Access token type rejection (only refresh tokens allowed)
- Expired refresh token handling
- User deletion after token issuance
- New access token validation
"""
import pytest
from datetime import datetime, timedelta
from jose import jwt
from tests.conftest import TestingSessionLocal
from app.core.security import get_password_hash, create_refresh_token, create_access_token, decode_token
from app.core.config import settings
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
    return {"id": user_id, "email": "test@example.com", "name": "Test User"}


@pytest.fixture
def valid_refresh_token(test_user):
    """Generate a valid refresh token for the test user."""
    return create_refresh_token(data={"sub": str(test_user["id"])})


def test_refresh_success(test_client, test_user, valid_refresh_token):
    """Test successful token refresh with valid refresh token."""
    # Arrange
    test_client.cookies.set("refresh_token", valid_refresh_token)
    
    # Act
    response = test_client.post("/api/auth/refresh")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Access token refreshed successfully"
    
    # Verify new access token is set in cookies
    assert "access_token" in response.cookies
    assert response.cookies["access_token"] != ""


def test_refresh_generates_valid_access_token(test_client, test_user, valid_refresh_token):
    """Test that refresh generates a valid access token with correct payload."""
    # Arrange
    test_client.cookies.set("refresh_token", valid_refresh_token)
    
    # Act
    response = test_client.post("/api/auth/refresh")
    
    # Assert
    assert response.status_code == 200
    
    # Decode and verify new access token
    new_access_token = response.cookies["access_token"]
    payload = decode_token(new_access_token)
    
    assert payload["sub"] == str(test_user["id"])
    assert payload["type"] == "access"
    assert "exp" in payload
    
    # Verify expiration is approximately 30 minutes from now
    exp_time = datetime.utcfromtimestamp(payload["exp"])
    expected_exp = datetime.utcnow() + timedelta(minutes=30)
    time_diff = abs((exp_time - expected_exp).total_seconds())
    assert time_diff < 5  # Allow 5 seconds tolerance


def test_refresh_missing_token(test_client):
    """Test that refresh without token returns 401."""
    # Act - No refresh token cookie set
    response = test_client.post("/api/auth/refresh")
    
    # Assert
    assert response.status_code == 401
    assert "not provided" in response.json()["detail"].lower()


def test_refresh_invalid_token(test_client):
    """Test that refresh with invalid token returns 401."""
    # Arrange
    test_client.cookies.set("refresh_token", "invalid-token-string")
    
    # Act
    response = test_client.post("/api/auth/refresh")
    
    # Assert
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


def test_refresh_expired_token(test_client, test_user):
    """Test that refresh with expired token returns 401."""
    # Arrange - Create an expired refresh token
    expired_token_data = {
        "sub": str(test_user["id"]),
        "exp": datetime.utcnow() - timedelta(days=1),  # Expired yesterday
        "type": "refresh"
    }
    expired_token = jwt.encode(expired_token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    test_client.cookies.set("refresh_token", expired_token)
    
    # Act
    response = test_client.post("/api/auth/refresh")
    
    # Assert
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower() or "expired" in response.json()["detail"].lower()


def test_refresh_with_access_token(test_client, test_user):
    """Test that refresh rejects access tokens (only refresh tokens allowed)."""
    # Arrange - Try to use an access token instead of refresh token
    access_token = create_access_token(data={"sub": str(test_user["id"])})
    test_client.cookies.set("refresh_token", access_token)
    
    # Act
    response = test_client.post("/api/auth/refresh")
    
    # Assert
    assert response.status_code == 401
    assert "token type" in response.json()["detail"].lower()


def test_refresh_user_not_found(test_client):
    """Test that refresh fails if user no longer exists."""
    # Arrange - Create token for non-existent user
    fake_user_id = 99999
    token = create_refresh_token(data={"sub": str(fake_user_id)})
    test_client.cookies.set("refresh_token", token)
    
    # Act
    response = test_client.post("/api/auth/refresh")
    
    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_refresh_deleted_user(test_client, test_user, valid_refresh_token):
    """Test that refresh fails if user is deleted after token was issued."""
    # Arrange - Delete the user
    db = TestingSessionLocal()
    user = db.query(User).filter(User.id == test_user["id"]).first()
    db.delete(user)
    db.commit()
    db.close()
    
    test_client.cookies.set("refresh_token", valid_refresh_token)
    
    # Act
    response = test_client.post("/api/auth/refresh")
    
    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_refresh_token_without_sub(test_client):
    """Test that refresh fails if token doesn't contain user ID (sub)."""
    # Arrange - Create token without 'sub' claim
    invalid_token_data = {
        "exp": datetime.utcnow() + timedelta(days=7),
        "type": "refresh"
        # Missing 'sub'
    }
    invalid_token = jwt.encode(invalid_token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    test_client.cookies.set("refresh_token", invalid_token)
    
    # Act
    response = test_client.post("/api/auth/refresh")
    
    # Assert
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


def test_refresh_token_with_invalid_sub(test_client):
    """Test that refresh fails if token contains non-numeric user ID."""
    # Arrange - Create token with invalid 'sub' value
    invalid_token_data = {
        "sub": "not-a-number",
        "exp": datetime.utcnow() + timedelta(days=7),
        "type": "refresh"
    }
    invalid_token = jwt.encode(invalid_token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    test_client.cookies.set("refresh_token", invalid_token)
    
    # Act
    response = test_client.post("/api/auth/refresh")
    
    # Assert
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


def test_refresh_token_without_type(test_client, test_user):
    """Test that refresh fails if token doesn't contain type field."""
    # Arrange - Create token without 'type' claim
    invalid_token_data = {
        "sub": str(test_user["id"]),
        "exp": datetime.utcnow() + timedelta(days=7)
        # Missing 'type'
    }
    invalid_token = jwt.encode(invalid_token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    test_client.cookies.set("refresh_token", invalid_token)
    
    # Act
    response = test_client.post("/api/auth/refresh")
    
    # Assert
    assert response.status_code == 401
    assert "token type" in response.json()["detail"].lower()


def test_refresh_preserves_refresh_token(test_client, test_user, valid_refresh_token):
    """Test that refresh only updates access token, not refresh token."""
    # Arrange
    test_client.cookies.set("refresh_token", valid_refresh_token)
    
    # Act
    response = test_client.post("/api/auth/refresh")
    
    # Assert
    assert response.status_code == 200
    
    # Verify access token is in response cookies
    assert "access_token" in response.cookies
    
    # Verify refresh token is NOT updated (not in response cookies)
    # The original refresh token should still be valid
    assert "refresh_token" not in response.cookies or response.cookies.get("refresh_token") == ""


def test_refresh_admin_user(test_client):
    """Test that admin users can refresh their tokens."""
    # Arrange - Create admin user
    db = TestingSessionLocal()
    admin = User(
        name="Admin User",
        email="admin@example.com",
        password=get_password_hash("AdminPass123"),
        role=UserRole.ADMIN
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    admin_id = admin.id
    db.close()
    
    # Create refresh token for admin
    admin_refresh_token = create_refresh_token(data={"sub": str(admin_id)})
    test_client.cookies.set("refresh_token", admin_refresh_token)
    
    # Act
    response = test_client.post("/api/auth/refresh")
    
    # Assert
    assert response.status_code == 200
    assert "access_token" in response.cookies


def test_refresh_multiple_times(test_client, test_user, valid_refresh_token):
    """Test that the same refresh token can be used multiple times."""
    # Arrange
    test_client.cookies.set("refresh_token", valid_refresh_token)
    
    # Act - First refresh
    response1 = test_client.post("/api/auth/refresh")
    assert response1.status_code == 200
    first_access_token = response1.cookies["access_token"]
    
    # Act - Second refresh with same refresh token
    response2 = test_client.post("/api/auth/refresh")
    assert response2.status_code == 200
    second_access_token = response2.cookies["access_token"]
    
    # Assert - Both should succeed
    # Note: Tokens may be identical if generated in the same second with same expiration
    # The important thing is both requests succeed
    
    # Both access tokens should be valid
    payload1 = decode_token(first_access_token)
    payload2 = decode_token(second_access_token)
    assert payload1["sub"] == str(test_user["id"])
    assert payload2["sub"] == str(test_user["id"])
    assert payload1["type"] == "access"
    assert payload2["type"] == "access"
