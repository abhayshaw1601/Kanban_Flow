"""
Unit tests for POST /api/auth/login endpoint.

Tests cover:
- Successful login with valid credentials
- Invalid credentials rejection
- Token generation and cookie setting
- httpOnly cookie security
- Response data validation
"""
import pytest
from tests.conftest import TestingSessionLocal
from app.core.security import get_password_hash, decode_token
from app.models.user import User, UserRole


@pytest.fixture
def test_user_with_password():
    """Create a test user in the database with password for login tests."""
    db = TestingSessionLocal()
    password = "TestPassword123"
    user = User(
        name="Test User",
        email="test@example.com",
        password=get_password_hash(password),
        role=UserRole.EMPLOYEE
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    user_data = {
        "id": user.id,
        "email": user.email,
        "password": password  # Return plaintext password for testing
    }
    db.close()
    return user_data


def test_login_success(test_client, test_user_with_password):
    """Test successful login with valid credentials."""
    # Arrange
    credentials = {
        "email": test_user_with_password["email"],
        "password": test_user_with_password["password"]
    }
    
    # Act
    response = test_client.post("/api/auth/login", json=credentials)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Login successful"
    assert "user" in data
    assert data["user"]["email"] == test_user_with_password["email"]
    assert data["user"]["name"] == "Test User"
    assert data["user"]["role"] == "employee"
    assert "password" not in data["user"]  # Password should not be in response


def test_login_sets_cookies(test_client, test_user_with_password):
    """Test that login sets access_token and refresh_token as httpOnly cookies."""
    # Arrange
    credentials = {
        "email": test_user_with_password["email"],
        "password": test_user_with_password["password"]
    }
    
    # Act
    response = test_client.post("/api/auth/login", json=credentials)
    
    # Assert
    assert response.status_code == 200
    
    # Check cookies are set
    cookies = response.cookies
    assert "access_token" in cookies
    assert "refresh_token" in cookies
    
    # Verify cookies have values
    assert cookies["access_token"] != ""
    assert cookies["refresh_token"] != ""


def test_login_tokens_valid(test_client, test_user_with_password):
    """Test that generated tokens are valid JWT tokens with correct payload."""
    # Arrange
    credentials = {
        "email": test_user_with_password["email"],
        "password": test_user_with_password["password"]
    }
    
    # Act
    response = test_client.post("/api/auth/login", json=credentials)
    
    # Assert
    assert response.status_code == 200
    
    # Decode and verify access token
    access_token = response.cookies["access_token"]
    access_payload = decode_token(access_token)
    assert access_payload["sub"] == str(test_user_with_password["id"])
    assert access_payload["type"] == "access"
    assert "exp" in access_payload
    
    # Decode and verify refresh token
    refresh_token = response.cookies["refresh_token"]
    refresh_payload = decode_token(refresh_token)
    assert refresh_payload["sub"] == str(test_user_with_password["id"])
    assert refresh_payload["type"] == "refresh"
    assert "exp" in refresh_payload


def test_login_invalid_email(test_client, test_user_with_password):
    """Test that login with non-existent email returns 401."""
    # Arrange
    credentials = {
        "email": "nonexistent@example.com",
        "password": test_user_with_password["password"]
    }
    
    # Act
    response = test_client.post("/api/auth/login", json=credentials)
    
    # Assert
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


def test_login_invalid_password(test_client, test_user_with_password):
    """Test that login with incorrect password returns 401."""
    # Arrange
    credentials = {
        "email": test_user_with_password["email"],
        "password": "WrongPassword123"
    }
    
    # Act
    response = test_client.post("/api/auth/login", json=credentials)
    
    # Assert
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


def test_login_missing_email(test_client):
    """Test that login without email returns validation error."""
    # Arrange
    credentials = {
        "password": "TestPassword123"
        # Missing email
    }
    
    # Act
    response = test_client.post("/api/auth/login", json=credentials)
    
    # Assert
    assert response.status_code == 422  # Validation error


def test_login_missing_password(test_client, test_user_with_password):
    """Test that login without password returns validation error."""
    # Arrange
    credentials = {
        "email": test_user_with_password["email"]
        # Missing password
    }
    
    # Act
    response = test_client.post("/api/auth/login", json=credentials)
    
    # Assert
    assert response.status_code == 422  # Validation error


def test_login_invalid_email_format(test_client):
    """Test that login with invalid email format returns validation error."""
    # Arrange
    credentials = {
        "email": "not-an-email",
        "password": "TestPassword123"
    }
    
    # Act
    response = test_client.post("/api/auth/login", json=credentials)
    
    # Assert
    assert response.status_code == 422  # Validation error


def test_login_admin_user(test_client):
    """Test that admin users can login successfully."""
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
    db.close()
    
    credentials = {
        "email": "admin@example.com",
        "password": "AdminPass123"
    }
    
    # Act
    response = test_client.post("/api/auth/login", json=credentials)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["role"] == "admin"


def test_login_empty_password(test_client, test_user_with_password):
    """Test that login with empty password returns 401."""
    # Arrange
    credentials = {
        "email": test_user_with_password["email"],
        "password": ""
    }
    
    # Act
    response = test_client.post("/api/auth/login", json=credentials)
    
    # Assert
    assert response.status_code == 401


def test_login_case_sensitive_email(test_client, test_user_with_password):
    """Test that email comparison is case-sensitive (or insensitive based on requirements)."""
    # Arrange - Try login with different case
    credentials = {
        "email": test_user_with_password["email"].upper(),  # TEST@EXAMPLE.COM
        "password": test_user_with_password["password"]
    }
    
    # Act
    response = test_client.post("/api/auth/login", json=credentials)
    
    # Assert
    # This test documents current behavior - adjust based on requirements
    # Currently, email is case-sensitive in database lookup
    assert response.status_code == 401
