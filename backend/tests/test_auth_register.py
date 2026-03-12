"""
Unit tests for POST /api/auth/register endpoint.

Tests cover:
- Successful user registration
- Email uniqueness validation
- Password hashing
- Default role assignment
- Response data validation
"""
import pytest
from tests.conftest import TestingSessionLocal
from app.core.security import verify_password
from app.models.user import User, UserRole


def test_register_success(test_client):
    """Test successful user registration with valid data."""
    # Arrange
    user_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "password": "SecurePass123"
    }
    
    # Act
    response = test_client.post("/api/auth/register", json=user_data)
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == user_data["name"]
    assert data["email"] == user_data["email"]
    assert data["role"] == "employee"  # Default role
    assert "password" not in data  # Password should not be in response
    assert "id" in data
    assert "created_at" in data
    assert data["avatar"] is None


def test_register_password_hashed(test_client):
    """Test that password is hashed with bcrypt, not stored as plaintext."""
    # Arrange
    user_data = {
        "name": "Jane Smith",
        "email": "jane@example.com",
        "password": "MyPassword456"
    }
    
    # Act
    response = test_client.post("/api/auth/register", json=user_data)
    
    # Assert
    assert response.status_code == 201
    
    # Verify password is hashed in database
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == user_data["email"]).first()
    assert user is not None
    assert user.password != user_data["password"]  # Not plaintext
    assert user.password.startswith("$2b$")  # Bcrypt hash format
    assert verify_password(user_data["password"], user.password)  # Can verify
    db.close()


def test_register_duplicate_email(test_client):
    """Test that registering with duplicate email returns 400 error."""
    # Arrange
    user_data = {
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "password": "Password789"
    }
    
    # Act - Register first user
    response1 = test_client.post("/api/auth/register", json=user_data)
    assert response1.status_code == 201
    
    # Act - Try to register with same email
    user_data2 = {
        "name": "Alice Different",
        "email": "alice@example.com",  # Same email
        "password": "DifferentPass123"
    }
    response2 = test_client.post("/api/auth/register", json=user_data2)
    
    # Assert
    assert response2.status_code == 400
    assert "email already registered" in response2.json()["detail"].lower()


def test_register_invalid_email(test_client):
    """Test that invalid email format returns validation error."""
    # Arrange
    user_data = {
        "name": "Bob Wilson",
        "email": "not-an-email",  # Invalid email
        "password": "ValidPass123"
    }
    
    # Act
    response = test_client.post("/api/auth/register", json=user_data)
    
    # Assert
    assert response.status_code == 422  # Validation error


def test_register_short_password(test_client):
    """Test that password shorter than 8 characters returns validation error."""
    # Arrange
    user_data = {
        "name": "Charlie Brown",
        "email": "charlie@example.com",
        "password": "short"  # Less than 8 characters
    }
    
    # Act
    response = test_client.post("/api/auth/register", json=user_data)
    
    # Assert
    assert response.status_code == 422  # Validation error


def test_register_missing_name(test_client):
    """Test that missing name field returns validation error."""
    # Arrange
    user_data = {
        "email": "test@example.com",
        "password": "ValidPass123"
        # Missing name
    }
    
    # Act
    response = test_client.post("/api/auth/register", json=user_data)
    
    # Assert
    assert response.status_code == 422  # Validation error


def test_register_empty_name(test_client):
    """Test that empty name returns validation error."""
    # Arrange
    user_data = {
        "name": "",  # Empty name
        "email": "test@example.com",
        "password": "ValidPass123"
    }
    
    # Act
    response = test_client.post("/api/auth/register", json=user_data)
    
    # Assert
    assert response.status_code == 422  # Validation error


def test_register_default_employee_role(test_client):
    """Test that new users are assigned employee role by default."""
    # Arrange
    user_data = {
        "name": "David Lee",
        "email": "david@example.com",
        "password": "Password123"
    }
    
    # Act
    response = test_client.post("/api/auth/register", json=user_data)
    
    # Assert
    assert response.status_code == 201
    
    # Verify role in database
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == user_data["email"]).first()
    assert user is not None
    assert user.role == UserRole.EMPLOYEE
    db.close()


def test_register_multiple_users(test_client):
    """Test that multiple users can be registered successfully."""
    # Arrange
    users = [
        {"name": "User 1", "email": "user1@example.com", "password": "Password123"},
        {"name": "User 2", "email": "user2@example.com", "password": "Password456"},
        {"name": "User 3", "email": "user3@example.com", "password": "Password789"},
    ]
    
    # Act & Assert
    for user_data in users:
        response = test_client.post("/api/auth/register", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["name"] == user_data["name"]
    
    # Verify all users in database
    db = TestingSessionLocal()
    user_count = db.query(User).count()
    assert user_count == 3
    db.close()
