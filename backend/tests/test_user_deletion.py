"""
Tests for user deletion functionality.

This module tests the DELETE /api/users/me endpoint to ensure:
- Users can delete their own profiles
- Tasks assigned to deleted users are unassigned
- Board memberships are removed
- Authentication cookies are cleared
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models.user import User, UserRole
from app.models.task import Task, TaskPriority
from app.models.board import Board
from app.models.column import Column
from app.models.board_member import BoardMember
from app.models.company import Company
from app.core.security import get_password_hash
from tests.conftest import TestingSessionLocal


client = TestClient(app)


def test_delete_user_requires_authentication():
    """Test that user deletion requires authentication."""
    response = client.delete("/api/users/me")
    
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]