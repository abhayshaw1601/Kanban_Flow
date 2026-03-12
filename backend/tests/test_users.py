"""
Tests for user management endpoints.

Tests the /api/users/me endpoint for retrieving current user profile.
"""

import pytest
from tests.conftest import TestingSessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash


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
    user_data = {
        "id": user.id,
        "name": user.name,
        "email": user.email
    }
    db.close()
    return user_data


@pytest.fixture
def authenticated_client(test_client, test_user):
    """Create an authenticated test client with valid tokens."""
    # Login to get tokens
    credentials = {
        "email": "test@example.com",
        "password": "TestPassword123"
    }
    response = test_client.post("/api/auth/login", json=credentials)
    assert response.status_code == 200
    return test_client


def test_get_current_user_profile_success(authenticated_client, test_user):
    """
    Test GET /api/users/me returns current user profile.
    
    Validates: Requirements 3.1, 24.5
    """
    # Get user profile
    response = authenticated_client.get("/api/users/me")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify all required fields are present
    assert data["id"] == test_user["id"]
    assert data["name"] == test_user["name"]
    assert data["email"] == test_user["email"]
    assert data["role"] == "employee"
    assert "created_at" in data
    
    # Verify password is NOT included in response (Requirement 3.4)
    assert "password" not in data


def test_get_current_user_profile_unauthenticated(test_client):
    """
    Test GET /api/users/me returns 401 when not authenticated.
    
    Validates: Requirements 29.1, 29.2
    """
    response = test_client.get("/api/users/me")
    
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


def test_get_current_user_profile_invalid_token(test_client):
    """
    Test GET /api/users/me returns 401 with invalid token.
    
    Validates: Requirements 29.1, 29.2
    """
    response = test_client.get("/api/users/me", cookies={"access_token": "invalid_token"})
    
    assert response.status_code == 401
    assert "Invalid token" in response.json()["detail"]


def test_get_current_user_profile_with_avatar(test_client):
    """
    Test GET /api/users/me includes avatar when present.
    
    Validates: Requirements 3.1
    """
    # Create user with avatar
    db = TestingSessionLocal()
    password = "TestPassword123"
    user = User(
        name="Avatar User",
        email="avatar@example.com",
        password=get_password_hash(password),
        role=UserRole.EMPLOYEE,
        avatar="https://example.com/avatar.jpg"
    )
    db.add(user)
    db.commit()
    db.close()
    
    # Login
    login_response = test_client.post(
        "/api/auth/login",
        json={"email": "avatar@example.com", "password": password}
    )
    assert login_response.status_code == 200
    
    # Get profile (TestClient maintains cookies automatically)
    response = test_client.get("/api/users/me")
    
    assert response.status_code == 200
    data = response.json()
    assert data["avatar"] == "https://example.com/avatar.jpg"


def test_get_current_user_profile_admin_role(test_client):
    """
    Test GET /api/users/me correctly returns admin role.
    
    Validates: Requirements 3.1, 2.1
    """
    # Create admin user
    db = TestingSessionLocal()
    password = "AdminPassword123"
    admin = User(
        name="Admin User",
        email="admin@test.com",
        password=get_password_hash(password),
        role=UserRole.ADMIN
    )
    db.add(admin)
    db.commit()
    db.close()
    
    # Login as admin
    login_response = test_client.post(
        "/api/auth/login",
        json={"email": "admin@test.com", "password": password}
    )
    assert login_response.status_code == 200
    
    # Get profile (TestClient maintains cookies automatically)
    response = test_client.get("/api/users/me")
    
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "admin"


def test_get_current_user_profile_employee_role(authenticated_client, test_user):
    """
    Test GET /api/users/me correctly returns employee role.
    
    Validates: Requirements 3.1, 2.1
    """
    # Get profile
    response = authenticated_client.get("/api/users/me")
    
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "employee"


@pytest.fixture
def admin_user():
    """Create an admin user in the database."""
    db = TestingSessionLocal()
    admin = User(
        name="Admin User",
        email="admin@example.com",
        password=get_password_hash("AdminPassword123"),
        role=UserRole.ADMIN
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    admin_data = {
        "id": admin.id,
        "name": admin.name,
        "email": admin.email
    }
    db.close()
    return admin_data


@pytest.fixture
def authenticated_admin_client(test_client, admin_user):
    """Create an authenticated admin test client with valid tokens."""
    # Login to get tokens
    credentials = {
        "email": "admin@example.com",
        "password": "AdminPassword123"
    }
    response = test_client.post("/api/auth/login", json=credentials)
    assert response.status_code == 200
    return test_client


@pytest.fixture
def multiple_users():
    """Create multiple users in the database for testing user list."""
    db = TestingSessionLocal()
    
    # Create admin
    admin = User(
        name="Admin User",
        email="admin@list.com",
        password=get_password_hash("AdminPassword123"),
        role=UserRole.ADMIN
    )
    db.add(admin)
    
    # Create employees
    employees = [
        User(
            name="Alice Employee",
            email="alice@list.com",
            password=get_password_hash("Password123"),
            role=UserRole.EMPLOYEE
        ),
        User(
            name="Bob Employee",
            email="bob@list.com",
            password=get_password_hash("Password123"),
            role=UserRole.EMPLOYEE
        ),
        User(
            name="Carol Employee",
            email="carol@list.com",
            password=get_password_hash("Password123"),
            role=UserRole.EMPLOYEE
        )
    ]
    
    for employee in employees:
        db.add(employee)
    
    db.commit()
    db.close()
    
    return {
        "admin": {"email": "admin@list.com", "password": "AdminPassword123"},
        "employee": {"email": "alice@list.com", "password": "Password123"}
    }


def test_get_all_users_as_admin_success(test_client, multiple_users):
    """
    Test GET /api/users returns all users when accessed by admin.
    
    Validates: Requirements 3.2, 24.6
    """
    # Login as admin
    login_response = test_client.post(
        "/api/auth/login",
        json=multiple_users["admin"]
    )
    assert login_response.status_code == 200
    
    # Get all users
    response = test_client.get("/api/users")
    
    assert response.status_code == 200
    data = response.json()
    
    # Should return a list
    assert isinstance(data, list)
    
    # Should have at least 4 users (admin + 3 employees)
    assert len(data) >= 4
    
    # Verify each user has required fields
    for user in data:
        assert "id" in user
        assert "name" in user
        assert "email" in user
        assert "role" in user
        assert "created_at" in user
        
        # Verify password is NOT included (Requirement 3.4)
        assert "password" not in user
    
    # Verify we have both admin and employee users
    roles = [user["role"] for user in data]
    assert "admin" in roles
    assert "employee" in roles


def test_get_all_users_as_employee_forbidden(test_client, multiple_users):
    """
    Test GET /api/users returns 403 when accessed by employee.
    
    Validates: Requirements 3.3
    """
    # Login as employee
    login_response = test_client.post(
        "/api/auth/login",
        json=multiple_users["employee"]
    )
    assert login_response.status_code == 200
    
    # Try to get all users
    response = test_client.get("/api/users")
    
    assert response.status_code == 403
    assert "Admin access required" in response.json()["detail"]


def test_get_all_users_unauthenticated(test_client):
    """
    Test GET /api/users returns 401 when not authenticated.
    
    Validates: Requirements 29.1, 29.2
    """
    response = test_client.get("/api/users")
    
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


def test_get_all_users_excludes_passwords(test_client, multiple_users):
    """
    Test GET /api/users never includes password hashes in response.
    
    Validates: Requirements 3.4
    """
    # Login as admin
    login_response = test_client.post(
        "/api/auth/login",
        json=multiple_users["admin"]
    )
    assert login_response.status_code == 200
    
    # Get all users
    response = test_client.get("/api/users")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify no user has password field
    for user in data:
        assert "password" not in user
        # Also verify the response doesn't contain any bcrypt hash patterns
        response_text = str(user)
        assert "$2b$" not in response_text  # bcrypt hash prefix


def test_get_all_users_returns_all_fields(test_client, multiple_users):
    """
    Test GET /api/users returns all expected user fields.
    
    Validates: Requirements 3.2
    """
    # Login as admin
    login_response = test_client.post(
        "/api/auth/login",
        json=multiple_users["admin"]
    )
    assert login_response.status_code == 200
    
    # Get all users
    response = test_client.get("/api/users")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check first user has all expected fields
    if len(data) > 0:
        user = data[0]
        assert "id" in user
        assert "name" in user
        assert "email" in user
        assert "avatar" in user  # Can be null
        assert "role" in user
        assert "created_at" in user
        
        # Verify types
        assert isinstance(user["id"], int)
        assert isinstance(user["name"], str)
        assert isinstance(user["email"], str)
        assert user["role"] in ["admin", "employee"]
        assert isinstance(user["created_at"], str)  # ISO format datetime string
