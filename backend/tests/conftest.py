"""
Pytest configuration and shared fixtures for all tests.

This file is automatically loaded by pytest and provides:
- Database setup and teardown
- Test client configuration
- Common fixtures used across multiple test files
"""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Set environment variables before importing app
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only-min-32-characters-long"
os.environ["COOKIE_SECURE"] = "False"  # Disable secure cookies for testing

from app.main import app
from app.core.database import Base, get_db
from app.core.security import get_password_hash

# Import ALL models so SQLAlchemy knows about them when creating tables
from app.models import User, UserRole, Board, BoardMember, Column, Task, TaskPriority


# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the database dependency
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def test_client():
    """Create a test client for the FastAPI app."""
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Create tables before each test and drop after."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop all tables
    Base.metadata.drop_all(bind=engine)


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
        "email": user.email,
    }
    db.close()
    return user_data


@pytest.fixture
def admin_user():
    """Create an admin user in the database."""
    db = TestingSessionLocal()
    user = User(
        name="Admin User",
        email="admin@example.com",
        password=get_password_hash("AdminPassword123"),
        role=UserRole.ADMIN
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    user_data = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
    }
    db.close()
    return user_data
