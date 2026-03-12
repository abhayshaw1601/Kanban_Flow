"""
Unit tests for Pydantic schemas.

Tests schema validation, serialization, and ensures password fields are excluded from responses.
"""
import pytest
from datetime import datetime
from pydantic import ValidationError
from app.schemas import (
    UserCreate, UserResponse,
    LoginRequest, TokenResponse,
    BoardCreate, BoardResponse, BoardDetail,
    ColumnResponse,
    TaskCreate, TaskUpdate, TaskMove, TaskResponse
)


class TestUserSchemas:
    """Tests for user-related schemas."""
    
    def test_user_create_valid(self):
        """Test UserCreate with valid data."""
        user_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "SecurePass123"
        }
        user = UserCreate(**user_data)
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.password == "SecurePass123"
    
    def test_user_create_invalid_email(self):
        """Test UserCreate rejects invalid email."""
        with pytest.raises(ValidationError):
            UserCreate(name="John", email="invalid-email", password="SecurePass123")
    
    def test_user_create_short_password(self):
        """Test UserCreate rejects password shorter than 8 characters."""
        with pytest.raises(ValidationError):
            UserCreate(name="John", email="john@example.com", password="short")
    
    def test_user_response_excludes_password(self):
        """Test UserResponse schema does not include password field (Requirement 3.4)."""
        # Verify password field is not in the schema
        assert "password" not in UserResponse.model_fields
    
    def test_user_response_valid(self):
        """Test UserResponse with valid data."""
        user_data = {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "avatar": "https://example.com/avatar.jpg",
            "role": "employee",
            "created_at": datetime.utcnow()
        }
        user = UserResponse(**user_data)
        assert user.id == 1
        assert user.name == "John Doe"
        assert user.role == "employee"


class TestAuthSchemas:
    """Tests for authentication-related schemas."""
    
    def test_login_request_valid(self):
        """Test LoginRequest with valid data."""
        login_data = {
            "email": "user@example.com",
            "password": "password123"
        }
        login = LoginRequest(**login_data)
        assert login.email == "user@example.com"
        assert login.password == "password123"
    
    def test_login_request_invalid_email(self):
        """Test LoginRequest rejects invalid email."""
        with pytest.raises(ValidationError):
            LoginRequest(email="not-an-email", password="password123")
    
    def test_token_response_valid(self):
        """Test TokenResponse with valid data."""
        token_data = {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
        token = TokenResponse(**token_data)
        assert token.access_token.startswith("eyJ")
        assert token.token_type == "bearer"


class TestBoardSchemas:
    """Tests for board-related schemas."""
    
    def test_board_create_valid(self):
        """Test BoardCreate with valid data."""
        board_data = {
            "name": "Project Board",
            "description": "A board for tracking project tasks"
        }
        board = BoardCreate(**board_data)
        assert board.name == "Project Board"
        assert board.description == "A board for tracking project tasks"
    
    def test_board_create_without_description(self):
        """Test BoardCreate with optional description omitted."""
        board = BoardCreate(name="Simple Board")
        assert board.name == "Simple Board"
        assert board.description is None
    
    def test_board_create_empty_name(self):
        """Test BoardCreate rejects empty name."""
        with pytest.raises(ValidationError):
            BoardCreate(name="", description="Test")
    
    def test_board_response_valid(self):
        """Test BoardResponse with valid data."""
        board_data = {
            "id": 1,
            "name": "Project Board",
            "description": "Test board",
            "created_at": datetime.utcnow(),
            "created_by": 1
        }
        board = BoardResponse(**board_data)
        assert board.id == 1
        assert board.name == "Project Board"
        assert board.created_by == 1


class TestColumnSchemas:
    """Tests for column-related schemas."""
    
    def test_column_response_valid(self):
        """Test ColumnResponse with valid data."""
        column_data = {
            "id": 1,
            "name": "To-Do",
            "order": 0,
            "board_id": 1
        }
        column = ColumnResponse(**column_data)
        assert column.id == 1
        assert column.name == "To-Do"
        assert column.order == 0
        assert column.board_id == 1


class TestTaskSchemas:
    """Tests for task-related schemas."""
    
    def test_task_create_valid(self):
        """Test TaskCreate with valid data."""
        task_data = {
            "title": "Implement feature",
            "description": "# Feature\nImplement the new feature",
            "due_date": datetime.utcnow(),
            "priority": "high",
            "column_id": 1,
            "assignee_id": 2
        }
        task = TaskCreate(**task_data)
        assert task.title == "Implement feature"
        assert task.priority == "high"
        assert task.column_id == 1
        assert task.assignee_id == 2
    
    def test_task_create_minimal(self):
        """Test TaskCreate with only required fields."""
        task = TaskCreate(title="Simple task", column_id=1)
        assert task.title == "Simple task"
        assert task.column_id == 1
        assert task.priority == "medium"  # default value
        assert task.description is None
        assert task.assignee_id is None
    
    def test_task_create_invalid_priority(self):
        """Test TaskCreate rejects invalid priority (Requirement 7.5)."""
        with pytest.raises(ValidationError):
            TaskCreate(title="Task", column_id=1, priority="urgent")
    
    def test_task_create_valid_priorities(self):
        """Test TaskCreate accepts all valid priority values (Requirement 7.5)."""
        for priority in ["low", "medium", "high"]:
            task = TaskCreate(title="Task", column_id=1, priority=priority)
            assert task.priority == priority
    
    def test_task_update_partial(self):
        """Test TaskUpdate allows partial updates."""
        update = TaskUpdate(title="Updated title")
        assert update.title == "Updated title"
        assert update.priority is None
        assert update.description is None
    
    def test_task_update_invalid_priority(self):
        """Test TaskUpdate rejects invalid priority (Requirement 7.5)."""
        with pytest.raises(ValidationError):
            TaskUpdate(priority="critical")
    
    def test_task_move_valid(self):
        """Test TaskMove with valid data."""
        move_data = {
            "column_id": 2,
            "order": 3
        }
        move = TaskMove(**move_data)
        assert move.column_id == 2
        assert move.order == 3
    
    def test_task_move_negative_order(self):
        """Test TaskMove rejects negative order."""
        with pytest.raises(ValidationError):
            TaskMove(column_id=1, order=-1)
    
    def test_task_response_valid(self):
        """Test TaskResponse with valid data."""
        task_data = {
            "id": 1,
            "title": "Test task",
            "description": "Description",
            "due_date": datetime.utcnow(),
            "priority": "medium",
            "order": 0,
            "column_id": 1,
            "assignee_id": 2,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        task = TaskResponse(**task_data)
        assert task.id == 1
        assert task.title == "Test task"
        assert task.priority == "medium"
