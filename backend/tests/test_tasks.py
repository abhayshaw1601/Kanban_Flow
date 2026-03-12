"""
Unit tests for task management endpoints.

Tests cover:
- POST /api/tasks - Task creation (admin only)
- Task validation (priority, assignee, column)
- Order calculation
- Authorization checks
"""
import pytest
from datetime import datetime, timedelta
from tests.conftest import TestingSessionLocal
from app.models.user import User, UserRole
from app.models.board import Board
from app.models.column import Column
from app.models.task import Task, TaskPriority
from app.models.board_member import BoardMember
from app.core.security import get_password_hash


@pytest.fixture
def admin_with_password():
    """Create an admin user with known password for login."""
    db = TestingSessionLocal()
    password = "AdminPass123"
    admin = User(
        name="Admin User",
        email="admin@example.com",
        password=get_password_hash(password),
        role=UserRole.ADMIN
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    admin_data = {
        "id": admin.id,
        "email": admin.email,
        "password": password
    }
    db.close()
    return admin_data


@pytest.fixture
def employee_with_password():
    """Create an employee user with known password for login."""
    db = TestingSessionLocal()
    password = "EmployeePass123"
    employee = User(
        name="Employee User",
        email="employee@example.com",
        password=get_password_hash(password),
        role=UserRole.EMPLOYEE
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)
    employee_data = {
        "id": employee.id,
        "email": employee.email,
        "password": password
    }
    db.close()
    return employee_data


@pytest.fixture
def admin_client(admin_with_password):
    """Create a test client with admin authentication."""
    from fastapi.testclient import TestClient
    from app.main import app
    
    with TestClient(app) as client:
        response = client.post("/api/auth/login", json={
            "email": admin_with_password["email"],
            "password": admin_with_password["password"]
        })
        assert response.status_code == 200
        yield client


@pytest.fixture
def employee_client(employee_with_password):
    """Create a test client with employee authentication."""
    from fastapi.testclient import TestClient
    from app.main import app
    
    with TestClient(app) as client:
        response = client.post("/api/auth/login", json={
            "email": employee_with_password["email"],
            "password": employee_with_password["password"]
        })
        assert response.status_code == 200
        yield client


@pytest.fixture
def test_board_with_column(admin_with_password):
    """Create a test board with columns for task creation."""
    db = TestingSessionLocal()
    
    # Create board
    board = Board(
        name="Test Board",
        description="Board for task testing",
        created_by=admin_with_password["id"]
    )
    db.add(board)
    db.flush()
    
    # Create columns
    column1 = Column(name="To-Do", order=0, board_id=board.id)
    column2 = Column(name="In Progress", order=1, board_id=board.id)
    column3 = Column(name="Done", order=2, board_id=board.id)
    
    db.add(column1)
    db.add(column2)
    db.add(column3)
    db.commit()
    
    board_data = {
        "board_id": board.id,
        "column_ids": {
            "todo": column1.id,
            "in_progress": column2.id,
            "done": column3.id
        }
    }
    db.close()
    return board_data


class TestCreateTask:
    """Tests for POST /api/tasks endpoint."""
    
    def test_create_task_success(self, admin_client, test_board_with_column, admin_with_password):
        """Test successful task creation by admin."""
        # Arrange
        task_data = {
            "title": "Test Task",
            "description": "A test task for unit testing",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        
        # Act
        response = admin_client.post("/api/tasks", json=task_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["description"] == "A test task for unit testing"
        assert data["priority"] == "medium"
        assert data["column_id"] == test_board_with_column["column_ids"]["todo"]
        assert data["order"] == 0  # First task in column
        assert data["assignee_id"] is None
        assert "created_at" in data
        assert "updated_at" in data
        assert "id" in data
    
    def test_create_task_with_all_fields(self, admin_client, test_board_with_column, admin_with_password):
        """Test task creation with all optional fields."""
        # Arrange
        due_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
        task_data = {
            "title": "Complete Task",
            "description": "# Task with markdown\n\n- Item 1\n- Item 2",
            "due_date": due_date,
            "priority": "high",
            "column_id": test_board_with_column["column_ids"]["in_progress"],
            "assignee_id": admin_with_password["id"]
        }
        
        # Act
        response = admin_client.post("/api/tasks", json=task_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Complete Task"
        assert data["description"] == "# Task with markdown\n\n- Item 1\n- Item 2"
        assert data["priority"] == "high"
        assert data["assignee_id"] == admin_with_password["id"]
        assert data["due_date"] is not None
    
    def test_create_task_low_priority(self, admin_client, test_board_with_column):
        """Test task creation with low priority."""
        # Arrange
        task_data = {
            "title": "Low Priority Task",
            "priority": "low",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        
        # Act
        response = admin_client.post("/api/tasks", json=task_data)
        
        # Assert
        assert response.status_code == 201
        assert response.json()["priority"] == "low"
    
    def test_create_task_high_priority(self, admin_client, test_board_with_column):
        """Test task creation with high priority."""
        # Arrange
        task_data = {
            "title": "High Priority Task",
            "priority": "high",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        
        # Act
        response = admin_client.post("/api/tasks", json=task_data)
        
        # Assert
        assert response.status_code == 201
        assert response.json()["priority"] == "high"
    
    def test_create_task_invalid_priority(self, admin_client, test_board_with_column):
        """Test that task creation with invalid priority fails."""
        # Arrange
        task_data = {
            "title": "Invalid Priority Task",
            "priority": "urgent",  # Invalid priority
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        
        # Act
        response = admin_client.post("/api/tasks", json=task_data)
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_create_task_invalid_column(self, admin_client):
        """Test that task creation with non-existent column fails."""
        # Arrange
        task_data = {
            "title": "Task with Invalid Column",
            "priority": "medium",
            "column_id": 99999  # Non-existent column
        }
        
        # Act
        response = admin_client.post("/api/tasks", json=task_data)
        
        # Assert
        assert response.status_code == 400
        assert "column" in response.json()["detail"].lower()
    
    def test_create_task_invalid_assignee(self, admin_client, test_board_with_column):
        """Test that task creation with non-existent assignee fails."""
        # Arrange
        task_data = {
            "title": "Task with Invalid Assignee",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"],
            "assignee_id": 99999  # Non-existent user
        }
        
        # Act
        response = admin_client.post("/api/tasks", json=task_data)
        
        # Assert
        assert response.status_code == 400
        assert "user" in response.json()["detail"].lower()
    
    def test_create_task_order_calculation_empty_column(self, admin_client, test_board_with_column):
        """Test that first task in column gets order 0."""
        # Arrange
        task_data = {
            "title": "First Task",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        
        # Act
        response = admin_client.post("/api/tasks", json=task_data)
        
        # Assert
        assert response.status_code == 201
        assert response.json()["order"] == 0
    
    def test_create_task_order_calculation_append(self, admin_client, test_board_with_column):
        """Test that new tasks are appended to end of column."""
        # Arrange - Create first task
        task1_data = {
            "title": "First Task",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        response1 = admin_client.post("/api/tasks", json=task1_data)
        assert response1.status_code == 201
        assert response1.json()["order"] == 0
        
        # Create second task
        task2_data = {
            "title": "Second Task",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        
        # Act
        response2 = admin_client.post("/api/tasks", json=task2_data)
        
        # Assert
        assert response2.status_code == 201
        assert response2.json()["order"] == 1
        
        # Create third task
        task3_data = {
            "title": "Third Task",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        response3 = admin_client.post("/api/tasks", json=task3_data)
        assert response3.status_code == 201
        assert response3.json()["order"] == 2
    
    def test_create_task_order_different_columns(self, admin_client, test_board_with_column):
        """Test that order is calculated per column."""
        # Arrange - Create task in first column
        task1_data = {
            "title": "Task in To-Do",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        response1 = admin_client.post("/api/tasks", json=task1_data)
        assert response1.status_code == 201
        assert response1.json()["order"] == 0
        
        # Create task in second column
        task2_data = {
            "title": "Task in In Progress",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["in_progress"]
        }
        
        # Act
        response2 = admin_client.post("/api/tasks", json=task2_data)
        
        # Assert - Should also have order 0 since it's in a different column
        assert response2.status_code == 201
        assert response2.json()["order"] == 0
    
    def test_create_task_employee_forbidden(self, employee_client, test_board_with_column):
        """Test that employee users cannot create tasks."""
        # Arrange
        task_data = {
            "title": "Employee Task",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        
        # Act
        response = employee_client.post("/api/tasks", json=task_data)
        
        # Assert
        assert response.status_code == 403
        assert "admin" in response.json()["detail"].lower()
    
    def test_create_task_unauthenticated(self, test_client, test_board_with_column):
        """Test that unauthenticated users cannot create tasks."""
        # Arrange
        task_data = {
            "title": "Unauthenticated Task",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        
        # Act
        response = test_client.post("/api/tasks", json=task_data)
        
        # Assert
        assert response.status_code == 401
    
    def test_create_task_missing_title(self, admin_client, test_board_with_column):
        """Test that task creation without title fails."""
        # Arrange
        task_data = {
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
            # Missing title
        }
        
        # Act
        response = admin_client.post("/api/tasks", json=task_data)
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_create_task_empty_title(self, admin_client, test_board_with_column):
        """Test that task creation with empty title fails."""
        # Arrange
        task_data = {
            "title": "",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        
        # Act
        response = admin_client.post("/api/tasks", json=task_data)
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_create_task_missing_column_id(self, admin_client):
        """Test that task creation without column_id fails."""
        # Arrange
        task_data = {
            "title": "Task Without Column",
            "priority": "medium"
            # Missing column_id
        }
        
        # Act
        response = admin_client.post("/api/tasks", json=task_data)
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_create_task_default_priority(self, admin_client, test_board_with_column):
        """Test that task creation without priority defaults to medium."""
        # Arrange
        task_data = {
            "title": "Task with Default Priority",
            "column_id": test_board_with_column["column_ids"]["todo"]
            # No priority specified
        }
        
        # Act
        response = admin_client.post("/api/tasks", json=task_data)
        
        # Assert
        assert response.status_code == 201
        assert response.json()["priority"] == "medium"
    
    def test_create_task_null_description(self, admin_client, test_board_with_column):
        """Test task creation with null description."""
        # Arrange
        task_data = {
            "title": "Task with Null Description",
            "description": None,
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        
        # Act
        response = admin_client.post("/api/tasks", json=task_data)
        
        # Assert
        assert response.status_code == 201
        assert response.json()["description"] is None
    
    def test_create_task_null_assignee(self, admin_client, test_board_with_column):
        """Test task creation with null assignee."""
        # Arrange
        task_data = {
            "title": "Unassigned Task",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"],
            "assignee_id": None
        }
        
        # Act
        response = admin_client.post("/api/tasks", json=task_data)
        
        # Assert
        assert response.status_code == 201
        assert response.json()["assignee_id"] is None
    
    def test_create_task_null_due_date(self, admin_client, test_board_with_column):
        """Test task creation with null due date."""
        # Arrange
        task_data = {
            "title": "Task Without Due Date",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"],
            "due_date": None
        }
        
        # Act
        response = admin_client.post("/api/tasks", json=task_data)
        
        # Assert
        assert response.status_code == 201
        assert response.json()["due_date"] is None
    
    def test_create_task_markdown_description(self, admin_client, test_board_with_column):
        """Test task creation with markdown description."""
        # Arrange
        markdown_content = """# Task Description

## Overview
This is a **bold** statement with *italic* text.

### Checklist
- [ ] Item 1
- [x] Item 2
- [ ] Item 3

```python
def hello():
    print("Hello, World!")
```

[Link to docs](https://example.com)
"""
        task_data = {
            "title": "Task with Markdown",
            "description": markdown_content,
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        
        # Act
        response = admin_client.post("/api/tasks", json=task_data)
        
        # Assert
        assert response.status_code == 201
        assert response.json()["description"] == markdown_content
    
    def test_create_task_timestamps(self, admin_client, test_board_with_column):
        """Test that created_at and updated_at are set correctly."""
        # Arrange
        before_creation = datetime.utcnow()
        task_data = {
            "title": "Task for Timestamp Test",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        
        # Act
        response = admin_client.post("/api/tasks", json=task_data)
        after_creation = datetime.utcnow()
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        
        created_at = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
        updated_at = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
        
        # Timestamps should be within the test execution window
        assert before_creation <= created_at <= after_creation
        assert before_creation <= updated_at <= after_creation
        
        # For new tasks, created_at and updated_at should be equal (or very close)
        assert abs((created_at - updated_at).total_seconds()) < 1
    
    def test_create_task_database_persistence(self, admin_client, test_board_with_column):
        """Test that created task is properly persisted in database."""
        # Arrange
        task_data = {
            "title": "Persistent Task",
            "description": "Testing database persistence",
            "priority": "high",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        
        # Act
        response = admin_client.post("/api/tasks", json=task_data)
        
        # Assert
        assert response.status_code == 201
        task_id = response.json()["id"]
        
        # Verify task exists in database
        db = TestingSessionLocal()
        task = db.query(Task).filter(Task.id == task_id).first()
        db.close()
        
        assert task is not None
        assert task.title == "Persistent Task"
        assert task.description == "Testing database persistence"
        assert task.priority == TaskPriority.HIGH
        assert task.column_id == test_board_with_column["column_ids"]["todo"]
    
    def test_create_task_with_special_characters(self, admin_client, test_board_with_column):
        """Test task creation with special characters in title and description."""
        # Arrange
        task_data = {
            "title": "Task with 特殊字符 & émojis 🚀",
            "description": "Description with <html> & special chars: @#$%",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        
        # Act
        response = admin_client.post("/api/tasks", json=task_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Task with 特殊字符 & émojis 🚀"
        assert data["description"] == "Description with <html> & special chars: @#$%"
    
    def test_create_task_long_title(self, admin_client, test_board_with_column):
        """Test task creation with maximum length title."""
        # Arrange
        task_data = {
            "title": "T" * 200,  # Max length from schema
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        
        # Act
        response = admin_client.post("/api/tasks", json=task_data)
        
        # Assert
        assert response.status_code == 201
        assert len(response.json()["title"]) == 200
    
    def test_create_task_title_too_long(self, admin_client, test_board_with_column):
        """Test that task creation with title exceeding max length fails."""
        # Arrange
        task_data = {
            "title": "T" * 201,  # Exceeds max length
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        
        # Act
        response = admin_client.post("/api/tasks", json=task_data)
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_create_multiple_tasks(self, admin_client, test_board_with_column):
        """Test creating multiple tasks in sequence."""
        # Arrange
        tasks_to_create = [
            {"title": "Task 1", "priority": "low"},
            {"title": "Task 2", "priority": "medium"},
            {"title": "Task 3", "priority": "high"}
        ]
        
        created_ids = []
        
        # Act
        for i, task_data in enumerate(tasks_to_create):
            task_data["column_id"] = test_board_with_column["column_ids"]["todo"]
            response = admin_client.post("/api/tasks", json=task_data)
            
            # Assert
            assert response.status_code == 201
            data = response.json()
            assert data["order"] == i  # Order should increment
            created_ids.append(data["id"])
        
        # Verify all tasks have unique IDs
        assert len(created_ids) == len(set(created_ids))
    
    def test_create_task_with_future_due_date(self, admin_client, test_board_with_column):
        """Test task creation with future due date."""
        # Arrange
        future_date = (datetime.utcnow() + timedelta(days=30)).isoformat()
        task_data = {
            "title": "Future Task",
            "due_date": future_date,
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        
        # Act
        response = admin_client.post("/api/tasks", json=task_data)
        
        # Assert
        assert response.status_code == 201
        assert response.json()["due_date"] is not None
    
    def test_create_task_with_past_due_date(self, admin_client, test_board_with_column):
        """Test task creation with past due date (overdue task)."""
        # Arrange
        past_date = (datetime.utcnow() - timedelta(days=7)).isoformat()
        task_data = {
            "title": "Overdue Task",
            "due_date": past_date,
            "priority": "high",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        
        # Act
        response = admin_client.post("/api/tasks", json=task_data)
        
        # Assert
        assert response.status_code == 201
        assert response.json()["due_date"] is not None



class TestUpdateTask:
    """Tests for PATCH /api/tasks/:id endpoint."""
    
    def test_update_task_admin_all_fields(self, admin_client, test_board_with_column, admin_with_password, employee_with_password):
        """Test admin can update all task fields."""
        # Arrange - Create a task first
        task_data = {
            "title": "Original Title",
            "description": "Original description",
            "priority": "low",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]
        
        # Act - Update all fields
        due_date = (datetime.utcnow() + timedelta(days=5)).isoformat()
        update_data = {
            "title": "Updated Title",
            "description": "Updated description with **markdown**",
            "due_date": due_date,
            "priority": "high",
            "assignee_id": employee_with_password["id"]
        }
        response = admin_client.patch(f"/api/tasks/{task_id}", json=update_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Updated Title"
        assert data["description"] == "Updated description with **markdown**"
        assert data["priority"] == "high"
        assert data["assignee_id"] == employee_with_password["id"]
        assert data["due_date"] is not None
        
        # Verify updated_at changed
        original_updated_at = datetime.fromisoformat(create_response.json()["updated_at"].replace("Z", "+00:00"))
        new_updated_at = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
        assert new_updated_at > original_updated_at
    
    def test_update_task_admin_partial_fields(self, admin_client, test_board_with_column):
        """Test admin can update only some fields."""
        # Arrange - Create a task
        task_data = {
            "title": "Original Title",
            "description": "Original description",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]
        
        # Act - Update only title and priority
        update_data = {
            "title": "New Title",
            "priority": "high"
        }
        response = admin_client.patch(f"/api/tasks/{task_id}", json=update_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Title"
        assert data["priority"] == "high"
        assert data["description"] == "Original description"  # Unchanged
    
    def test_update_task_admin_title_only(self, admin_client, test_board_with_column):
        """Test admin can update only title."""
        # Arrange
        task_data = {
            "title": "Original Title",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act
        update_data = {"title": "Updated Title Only"}
        response = admin_client.patch(f"/api/tasks/{task_id}", json=update_data)
        
        # Assert
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Title Only"
    
    def test_update_task_admin_description_only(self, admin_client, test_board_with_column):
        """Test admin can update only description."""
        # Arrange
        task_data = {
            "title": "Task Title",
            "description": "Original",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act
        update_data = {"description": "# Updated Description\n\nWith markdown"}
        response = admin_client.patch(f"/api/tasks/{task_id}", json=update_data)
        
        # Assert
        assert response.status_code == 200
        assert response.json()["description"] == "# Updated Description\n\nWith markdown"
    
    def test_update_task_admin_priority_only(self, admin_client, test_board_with_column):
        """Test admin can update only priority."""
        # Arrange
        task_data = {
            "title": "Task",
            "priority": "low",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act
        update_data = {"priority": "high"}
        response = admin_client.patch(f"/api/tasks/{task_id}", json=update_data)
        
        # Assert
        assert response.status_code == 200
        assert response.json()["priority"] == "high"
    
    def test_update_task_admin_assignee_only(self, admin_client, test_board_with_column, employee_with_password):
        """Test admin can update only assignee."""
        # Arrange
        task_data = {
            "title": "Task",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act
        update_data = {"assignee_id": employee_with_password["id"]}
        response = admin_client.patch(f"/api/tasks/{task_id}", json=update_data)
        
        # Assert
        assert response.status_code == 200
        assert response.json()["assignee_id"] == employee_with_password["id"]
    
    def test_update_task_admin_due_date_only(self, admin_client, test_board_with_column):
        """Test admin can update only due date."""
        # Arrange
        task_data = {
            "title": "Task",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act
        due_date = (datetime.utcnow() + timedelta(days=10)).isoformat()
        update_data = {"due_date": due_date}
        response = admin_client.patch(f"/api/tasks/{task_id}", json=update_data)
        
        # Assert
        assert response.status_code == 200
        assert response.json()["due_date"] is not None
    
    def test_update_task_employee_forbidden_title(self, employee_client, admin_client, test_board_with_column):
        """Test employee cannot update title."""
        # Arrange - Admin creates task
        task_data = {
            "title": "Original Title",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act - Employee tries to update title
        update_data = {"title": "Employee Updated Title"}
        response = employee_client.patch(f"/api/tasks/{task_id}", json=update_data)
        
        # Assert
        assert response.status_code == 403
        assert "employee" in response.json()["detail"].lower()
    
    def test_update_task_employee_forbidden_description(self, employee_client, admin_client, test_board_with_column):
        """Test employee cannot update description."""
        # Arrange
        task_data = {
            "title": "Task",
            "description": "Original",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act
        update_data = {"description": "Employee Updated"}
        response = employee_client.patch(f"/api/tasks/{task_id}", json=update_data)
        
        # Assert
        assert response.status_code == 403
    
    def test_update_task_employee_forbidden_priority(self, employee_client, admin_client, test_board_with_column):
        """Test employee cannot update priority."""
        # Arrange
        task_data = {
            "title": "Task",
            "priority": "low",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act
        update_data = {"priority": "high"}
        response = employee_client.patch(f"/api/tasks/{task_id}", json=update_data)
        
        # Assert
        assert response.status_code == 403
    
    def test_update_task_employee_forbidden_assignee(self, employee_client, admin_client, test_board_with_column, employee_with_password):
        """Test employee cannot update assignee."""
        # Arrange
        task_data = {
            "title": "Task",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act
        update_data = {"assignee_id": employee_with_password["id"]}
        response = employee_client.patch(f"/api/tasks/{task_id}", json=update_data)
        
        # Assert
        assert response.status_code == 403
    
    def test_update_task_employee_forbidden_due_date(self, employee_client, admin_client, test_board_with_column):
        """Test employee cannot update due date."""
        # Arrange
        task_data = {
            "title": "Task",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act
        due_date = (datetime.utcnow() + timedelta(days=5)).isoformat()
        update_data = {"due_date": due_date}
        response = employee_client.patch(f"/api/tasks/{task_id}", json=update_data)
        
        # Assert
        assert response.status_code == 403
    
    def test_update_task_employee_can_update_column_id(self, employee_client, admin_client, test_board_with_column):
        """Test employee can update column_id (status-related field)."""
        # Arrange
        task_data = {
            "title": "Task",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act
        update_data = {"column_id": test_board_with_column["column_ids"]["in_progress"]}
        response = employee_client.patch(f"/api/tasks/{task_id}", json=update_data)
        
        # Assert
        assert response.status_code == 200
        assert response.json()["column_id"] == test_board_with_column["column_ids"]["in_progress"]
    
    def test_update_task_employee_can_update_order(self, employee_client, admin_client, test_board_with_column):
        """Test employee can update order (status-related field)."""
        # Arrange
        task_data = {
            "title": "Task",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        original_order = create_response.json()["order"]
        
        # Act
        update_data = {"order": original_order + 5}
        response = employee_client.patch(f"/api/tasks/{task_id}", json=update_data)
        
        # Assert
        assert response.status_code == 200
        assert response.json()["order"] == original_order + 5
    
    def test_update_task_employee_can_update_both_status_fields(self, employee_client, admin_client, test_board_with_column):
        """Test employee can update both column_id and order together."""
        # Arrange
        task_data = {
            "title": "Task",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act
        update_data = {
            "column_id": test_board_with_column["column_ids"]["done"],
            "order": 10
        }
        response = employee_client.patch(f"/api/tasks/{task_id}", json=update_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["column_id"] == test_board_with_column["column_ids"]["done"]
        assert data["order"] == 10
    
    def test_update_task_invalid_priority(self, admin_client, test_board_with_column):
        """Test that updating with invalid priority fails."""
        # Arrange
        task_data = {
            "title": "Task",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act
        update_data = {"priority": "urgent"}  # Invalid priority
        response = admin_client.patch(f"/api/tasks/{task_id}", json=update_data)
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_update_task_invalid_assignee(self, admin_client, test_board_with_column):
        """Test that updating with non-existent assignee fails."""
        # Arrange
        task_data = {
            "title": "Task",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act
        update_data = {"assignee_id": 99999}  # Non-existent user
        response = admin_client.patch(f"/api/tasks/{task_id}", json=update_data)
        
        # Assert
        assert response.status_code == 400
        assert "user" in response.json()["detail"].lower()
    
    def test_update_task_nonexistent_task(self, admin_client):
        """Test that updating non-existent task returns 404."""
        # Act
        update_data = {"title": "Updated Title"}
        response = admin_client.patch("/api/tasks/99999", json=update_data)
        
        # Assert
        assert response.status_code == 404
        assert "task" in response.json()["detail"].lower()
    
    def test_update_task_unauthenticated(self, test_client, admin_client, test_board_with_column):
        """Test that unauthenticated users cannot update tasks."""
        # Arrange - Create task as admin
        task_data = {
            "title": "Task",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act - Try to update without authentication
        update_data = {"title": "Hacked Title"}
        response = test_client.patch(f"/api/tasks/{task_id}", json=update_data)
        
        # Assert
        assert response.status_code == 401
    
    def test_update_task_empty_update(self, admin_client, test_board_with_column):
        """Test that updating with no fields returns task unchanged."""
        # Arrange
        task_data = {
            "title": "Original Title",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        original_data = create_response.json()
        
        # Act - Send empty update
        update_data = {}
        response = admin_client.patch(f"/api/tasks/{task_id}", json=update_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == original_data["title"]
        assert data["priority"] == original_data["priority"]
    
    def test_update_task_null_assignee(self, admin_client, test_board_with_column, employee_with_password):
        """Test admin can set assignee to null (unassign)."""
        # Arrange - Create task with assignee
        task_data = {
            "title": "Task",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"],
            "assignee_id": employee_with_password["id"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        assert create_response.json()["assignee_id"] == employee_with_password["id"]
        
        # Act - Set assignee to null
        update_data = {"assignee_id": None}
        response = admin_client.patch(f"/api/tasks/{task_id}", json=update_data)
        
        # Assert
        assert response.status_code == 200
        assert response.json()["assignee_id"] is None
    
    def test_update_task_null_description(self, admin_client, test_board_with_column):
        """Test admin can set description to null."""
        # Arrange
        task_data = {
            "title": "Task",
            "description": "Original description",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act
        update_data = {"description": None}
        response = admin_client.patch(f"/api/tasks/{task_id}", json=update_data)
        
        # Assert
        assert response.status_code == 200
        assert response.json()["description"] is None
    
    def test_update_task_null_due_date(self, admin_client, test_board_with_column):
        """Test admin can set due_date to null."""
        # Arrange
        due_date = (datetime.utcnow() + timedelta(days=5)).isoformat()
        task_data = {
            "title": "Task",
            "due_date": due_date,
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        assert create_response.json()["due_date"] is not None
        
        # Act
        update_data = {"due_date": None}
        response = admin_client.patch(f"/api/tasks/{task_id}", json=update_data)
        
        # Assert
        assert response.status_code == 200
        assert response.json()["due_date"] is None
    
    def test_update_task_updated_at_timestamp(self, admin_client, test_board_with_column):
        """Test that updated_at timestamp is updated on task update."""
        # Arrange
        task_data = {
            "title": "Original Title",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        original_updated_at = create_response.json()["updated_at"]
        
        # Wait a moment to ensure timestamp difference
        import time
        time.sleep(0.1)
        
        # Act
        update_data = {"title": "Updated Title"}
        response = admin_client.patch(f"/api/tasks/{task_id}", json=update_data)
        
        # Assert
        assert response.status_code == 200
        new_updated_at = response.json()["updated_at"]
        assert new_updated_at != original_updated_at
        
        # Parse and compare timestamps
        original_dt = datetime.fromisoformat(original_updated_at.replace("Z", "+00:00"))
        new_dt = datetime.fromisoformat(new_updated_at.replace("Z", "+00:00"))
        assert new_dt > original_dt
    
    def test_update_task_database_persistence(self, admin_client, test_board_with_column):
        """Test that task updates are properly persisted in database."""
        # Arrange
        task_data = {
            "title": "Original Title",
            "priority": "low",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act
        update_data = {
            "title": "Updated Title",
            "priority": "high"
        }
        response = admin_client.patch(f"/api/tasks/{task_id}", json=update_data)
        assert response.status_code == 200
        
        # Assert - Verify in database
        db = TestingSessionLocal()
        task = db.query(Task).filter(Task.id == task_id).first()
        db.close()
        
        assert task is not None
        assert task.title == "Updated Title"
        assert task.priority == TaskPriority.HIGH
    
    def test_update_task_multiple_updates(self, admin_client, test_board_with_column):
        """Test multiple sequential updates to the same task."""
        # Arrange
        task_data = {
            "title": "Version 1",
            "priority": "low",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act - Update 1
        response1 = admin_client.patch(f"/api/tasks/{task_id}", json={"title": "Version 2"})
        assert response1.status_code == 200
        assert response1.json()["title"] == "Version 2"
        
        # Act - Update 2
        response2 = admin_client.patch(f"/api/tasks/{task_id}", json={"priority": "medium"})
        assert response2.status_code == 200
        assert response2.json()["priority"] == "medium"
        assert response2.json()["title"] == "Version 2"  # Previous update persisted
        
        # Act - Update 3
        response3 = admin_client.patch(f"/api/tasks/{task_id}", json={"title": "Version 3", "priority": "high"})
        assert response3.status_code == 200
        assert response3.json()["title"] == "Version 3"
        assert response3.json()["priority"] == "high"
    
    def test_update_task_with_special_characters(self, admin_client, test_board_with_column):
        """Test updating task with special characters."""
        # Arrange
        task_data = {
            "title": "Original",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act
        update_data = {
            "title": "Updated with 特殊字符 & émojis 🎉",
            "description": "Description with <html> & special: @#$%"
        }
        response = admin_client.patch(f"/api/tasks/{task_id}", json=update_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated with 特殊字符 & émojis 🎉"
        assert data["description"] == "Description with <html> & special: @#$%"
    
    def test_update_task_priority_transitions(self, admin_client, test_board_with_column):
        """Test all priority transitions (low -> medium -> high)."""
        # Arrange
        task_data = {
            "title": "Task",
            "priority": "low",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act & Assert - low to medium
        response1 = admin_client.patch(f"/api/tasks/{task_id}", json={"priority": "medium"})
        assert response1.status_code == 200
        assert response1.json()["priority"] == "medium"
        
        # Act & Assert - medium to high
        response2 = admin_client.patch(f"/api/tasks/{task_id}", json={"priority": "high"})
        assert response2.status_code == 200
        assert response2.json()["priority"] == "high"
        
        # Act & Assert - high to low
        response3 = admin_client.patch(f"/api/tasks/{task_id}", json={"priority": "low"})
        assert response3.status_code == 200
        assert response3.json()["priority"] == "low"
    
    def test_update_task_long_title(self, admin_client, test_board_with_column):
        """Test updating task with maximum length title."""
        # Arrange
        task_data = {
            "title": "Short",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act
        long_title = "T" * 200  # Max length
        update_data = {"title": long_title}
        response = admin_client.patch(f"/api/tasks/{task_id}", json=update_data)
        
        # Assert
        assert response.status_code == 200
        assert len(response.json()["title"]) == 200
    
    def test_update_task_title_too_long(self, admin_client, test_board_with_column):
        """Test that updating with title exceeding max length fails."""
        # Arrange
        task_data = {
            "title": "Short",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act
        too_long_title = "T" * 201  # Exceeds max length
        update_data = {"title": too_long_title}
        response = admin_client.patch(f"/api/tasks/{task_id}", json=update_data)
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_update_task_markdown_description(self, admin_client, test_board_with_column):
        """Test updating task with markdown description."""
        # Arrange
        task_data = {
            "title": "Task",
            "description": "Plain text",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act
        markdown_content = """# Updated Description

## Features
- **Bold** text
- *Italic* text
- [Links](https://example.com)

```python
def hello():
    print("Hello!")
```
"""
        update_data = {"description": markdown_content}
        response = admin_client.patch(f"/api/tasks/{task_id}", json=update_data)
        
        # Assert
        assert response.status_code == 200
        assert response.json()["description"] == markdown_content



class TestMoveTask:
    """Tests for PATCH /api/tasks/:id/move endpoint."""
    
    def test_move_task_to_different_column(self, admin_client, test_board_with_column):
        """Test moving a task from one column to another."""
        # Arrange - Create task in To-Do column
        task_data = {
            "title": "Task to Move",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]
        assert create_response.json()["column_id"] == test_board_with_column["column_ids"]["todo"]
        assert create_response.json()["order"] == 0
        
        # Act - Move task to In Progress column
        move_data = {
            "column_id": test_board_with_column["column_ids"]["in_progress"],
            "order": 0
        }
        response = admin_client.patch(f"/api/tasks/{task_id}/move", json=move_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["column_id"] == test_board_with_column["column_ids"]["in_progress"]
        assert data["order"] == 0
        assert data["title"] == "Task to Move"  # Other fields unchanged
    
    def test_move_task_employee_allowed(self, employee_client, admin_client, test_board_with_column):
        """Test that employee users can move tasks."""
        # Arrange - Admin creates task
        task_data = {
            "title": "Employee Task",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act - Employee moves task
        move_data = {
            "column_id": test_board_with_column["column_ids"]["done"],
            "order": 0
        }
        response = employee_client.patch(f"/api/tasks/{task_id}/move", json=move_data)
        
        # Assert
        assert response.status_code == 200
        assert response.json()["column_id"] == test_board_with_column["column_ids"]["done"]
    
    def test_move_task_reorder_within_column(self, admin_client, test_board_with_column):
        """Test reordering a task within the same column."""
        # Arrange - Create three tasks in the same column
        task_ids = []
        for i in range(3):
            task_data = {
                "title": f"Task {i}",
                "priority": "medium",
                "column_id": test_board_with_column["column_ids"]["todo"]
            }
            response = admin_client.post("/api/tasks", json=task_data)
            assert response.status_code == 201
            task_ids.append(response.json()["id"])
            assert response.json()["order"] == i
        
        # Act - Move first task (order 0) to position 2
        move_data = {
            "column_id": test_board_with_column["column_ids"]["todo"],
            "order": 2
        }
        response = admin_client.patch(f"/api/tasks/{task_ids[0]}/move", json=move_data)
        
        # Assert
        assert response.status_code == 200
        assert response.json()["order"] == 2
        
        # Verify other tasks were reordered
        db = TestingSessionLocal()
        task1 = db.query(Task).filter(Task.id == task_ids[1]).first()
        task2 = db.query(Task).filter(Task.id == task_ids[2]).first()
        db.close()
        
        assert task1.order == 0  # Was 1, moved down
        assert task2.order == 1  # Was 2, moved down
    
    def test_move_task_reorder_move_up(self, admin_client, test_board_with_column):
        """Test moving a task up within the same column."""
        # Arrange - Create three tasks
        task_ids = []
        for i in range(3):
            task_data = {
                "title": f"Task {i}",
                "priority": "medium",
                "column_id": test_board_with_column["column_ids"]["todo"]
            }
            response = admin_client.post("/api/tasks", json=task_data)
            task_ids.append(response.json()["id"])
        
        # Act - Move last task (order 2) to position 0
        move_data = {
            "column_id": test_board_with_column["column_ids"]["todo"],
            "order": 0
        }
        response = admin_client.patch(f"/api/tasks/{task_ids[2]}/move", json=move_data)
        
        # Assert
        assert response.status_code == 200
        assert response.json()["order"] == 0
        
        # Verify other tasks were reordered
        db = TestingSessionLocal()
        task0 = db.query(Task).filter(Task.id == task_ids[0]).first()
        task1 = db.query(Task).filter(Task.id == task_ids[1]).first()
        db.close()
        
        assert task0.order == 1  # Was 0, moved up
        assert task1.order == 2  # Was 1, moved up
    
    def test_move_task_reorder_move_down(self, admin_client, test_board_with_column):
        """Test moving a task down within the same column."""
        # Arrange - Create three tasks
        task_ids = []
        for i in range(3):
            task_data = {
                "title": f"Task {i}",
                "priority": "medium",
                "column_id": test_board_with_column["column_ids"]["todo"]
            }
            response = admin_client.post("/api/tasks", json=task_data)
            task_ids.append(response.json()["id"])
        
        # Act - Move first task (order 0) to position 1
        move_data = {
            "column_id": test_board_with_column["column_ids"]["todo"],
            "order": 1
        }
        response = admin_client.patch(f"/api/tasks/{task_ids[0]}/move", json=move_data)
        
        # Assert
        assert response.status_code == 200
        assert response.json()["order"] == 1
        
        # Verify other task was reordered
        db = TestingSessionLocal()
        task1 = db.query(Task).filter(Task.id == task_ids[1]).first()
        task2 = db.query(Task).filter(Task.id == task_ids[2]).first()
        db.close()
        
        assert task1.order == 0  # Was 1, moved down
        assert task2.order == 2  # Was 2, unchanged
    
    def test_move_task_to_empty_column(self, admin_client, test_board_with_column):
        """Test moving a task to an empty column."""
        # Arrange - Create task in To-Do
        task_data = {
            "title": "Task",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act - Move to empty Done column
        move_data = {
            "column_id": test_board_with_column["column_ids"]["done"],
            "order": 0
        }
        response = admin_client.patch(f"/api/tasks/{task_id}/move", json=move_data)
        
        # Assert
        assert response.status_code == 200
        assert response.json()["column_id"] == test_board_with_column["column_ids"]["done"]
        assert response.json()["order"] == 0
    
    def test_move_task_to_column_with_existing_tasks(self, admin_client, test_board_with_column):
        """Test moving a task to a column that already has tasks."""
        # Arrange - Create two tasks in In Progress
        for i in range(2):
            task_data = {
                "title": f"Existing Task {i}",
                "priority": "medium",
                "column_id": test_board_with_column["column_ids"]["in_progress"]
            }
            admin_client.post("/api/tasks", json=task_data)
        
        # Create task in To-Do
        task_data = {
            "title": "Task to Move",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act - Move to In Progress at position 1 (between existing tasks)
        move_data = {
            "column_id": test_board_with_column["column_ids"]["in_progress"],
            "order": 1
        }
        response = admin_client.patch(f"/api/tasks/{task_id}/move", json=move_data)
        
        # Assert
        assert response.status_code == 200
        assert response.json()["order"] == 1
        
        # Verify existing tasks were reordered
        db = TestingSessionLocal()
        tasks_in_progress = db.query(Task).filter(
            Task.column_id == test_board_with_column["column_ids"]["in_progress"]
        ).order_by(Task.order).all()
        db.close()
        
        assert len(tasks_in_progress) == 3
        assert tasks_in_progress[0].title == "Existing Task 0"
        assert tasks_in_progress[0].order == 0
        assert tasks_in_progress[1].title == "Task to Move"
        assert tasks_in_progress[1].order == 1
        assert tasks_in_progress[2].title == "Existing Task 1"
        assert tasks_in_progress[2].order == 2
    
    def test_move_task_source_column_reordering(self, admin_client, test_board_with_column):
        """Test that source column tasks are reordered when task is moved out."""
        # Arrange - Create three tasks in To-Do
        task_ids = []
        for i in range(3):
            task_data = {
                "title": f"Task {i}",
                "priority": "medium",
                "column_id": test_board_with_column["column_ids"]["todo"]
            }
            response = admin_client.post("/api/tasks", json=task_data)
            task_ids.append(response.json()["id"])
        
        # Act - Move middle task (order 1) to different column
        move_data = {
            "column_id": test_board_with_column["column_ids"]["in_progress"],
            "order": 0
        }
        response = admin_client.patch(f"/api/tasks/{task_ids[1]}/move", json=move_data)
        
        # Assert
        assert response.status_code == 200
        
        # Verify source column tasks were reordered
        db = TestingSessionLocal()
        task0 = db.query(Task).filter(Task.id == task_ids[0]).first()
        task2 = db.query(Task).filter(Task.id == task_ids[2]).first()
        db.close()
        
        assert task0.order == 0  # Unchanged
        assert task2.order == 1  # Was 2, moved down to fill gap
    
    def test_move_task_append_to_end_of_column(self, admin_client, test_board_with_column):
        """Test moving a task to the end of a column."""
        # Arrange - Create two tasks in In Progress
        for i in range(2):
            task_data = {
                "title": f"Existing Task {i}",
                "priority": "medium",
                "column_id": test_board_with_column["column_ids"]["in_progress"]
            }
            admin_client.post("/api/tasks", json=task_data)
        
        # Create task in To-Do
        task_data = {
            "title": "Task to Move",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act - Move to end of In Progress (order 2)
        move_data = {
            "column_id": test_board_with_column["column_ids"]["in_progress"],
            "order": 2
        }
        response = admin_client.patch(f"/api/tasks/{task_id}/move", json=move_data)
        
        # Assert
        assert response.status_code == 200
        assert response.json()["order"] == 2
    
    def test_move_task_invalid_column(self, admin_client, test_board_with_column):
        """Test that moving to non-existent column fails."""
        # Arrange
        task_data = {
            "title": "Task",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act
        move_data = {
            "column_id": 99999,  # Non-existent column
            "order": 0
        }
        response = admin_client.patch(f"/api/tasks/{task_id}/move", json=move_data)
        
        # Assert
        assert response.status_code == 400
        assert "column" in response.json()["detail"].lower()
    
    def test_move_task_nonexistent_task(self, admin_client, test_board_with_column):
        """Test that moving non-existent task returns 404."""
        # Act
        move_data = {
            "column_id": test_board_with_column["column_ids"]["todo"],
            "order": 0
        }
        response = admin_client.patch("/api/tasks/99999/move", json=move_data)
        
        # Assert
        assert response.status_code == 404
        assert "task" in response.json()["detail"].lower()
    
    def test_move_task_unauthenticated(self, test_client, admin_client, test_board_with_column):
        """Test that unauthenticated users cannot move tasks."""
        # Arrange - Create task as admin
        task_data = {
            "title": "Task",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act - Try to move without authentication
        move_data = {
            "column_id": test_board_with_column["column_ids"]["in_progress"],
            "order": 0
        }
        response = test_client.patch(f"/api/tasks/{task_id}/move", json=move_data)
        
        # Assert
        assert response.status_code == 401
    
    def test_move_task_negative_order(self, admin_client, test_board_with_column):
        """Test that moving with negative order fails validation."""
        # Arrange
        task_data = {
            "title": "Task",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act
        move_data = {
            "column_id": test_board_with_column["column_ids"]["todo"],
            "order": -1  # Invalid negative order
        }
        response = admin_client.patch(f"/api/tasks/{task_id}/move", json=move_data)
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_move_task_updated_at_timestamp(self, admin_client, test_board_with_column):
        """Test that updated_at timestamp is updated when task is moved."""
        # Arrange
        task_data = {
            "title": "Task",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        original_updated_at = create_response.json()["updated_at"]
        
        # Wait a moment to ensure timestamp difference
        import time
        time.sleep(0.1)
        
        # Act
        move_data = {
            "column_id": test_board_with_column["column_ids"]["in_progress"],
            "order": 0
        }
        response = admin_client.patch(f"/api/tasks/{task_id}/move", json=move_data)
        
        # Assert
        assert response.status_code == 200
        new_updated_at = response.json()["updated_at"]
        assert new_updated_at != original_updated_at
        
        # Parse and compare timestamps
        original_dt = datetime.fromisoformat(original_updated_at.replace("Z", "+00:00"))
        new_dt = datetime.fromisoformat(new_updated_at.replace("Z", "+00:00"))
        assert new_dt > original_dt
    
    def test_move_task_preserves_other_fields(self, admin_client, test_board_with_column, employee_with_password):
        """Test that moving a task preserves all other fields."""
        # Arrange - Create task with all fields
        due_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
        task_data = {
            "title": "Complete Task",
            "description": "# Description\n\nWith markdown",
            "due_date": due_date,
            "priority": "high",
            "column_id": test_board_with_column["column_ids"]["todo"],
            "assignee_id": employee_with_password["id"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act - Move task
        move_data = {
            "column_id": test_board_with_column["column_ids"]["done"],
            "order": 0
        }
        response = admin_client.patch(f"/api/tasks/{task_id}/move", json=move_data)
        
        # Assert - All fields preserved except column_id and order
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Complete Task"
        assert data["description"] == "# Description\n\nWith markdown"
        assert data["priority"] == "high"
        assert data["assignee_id"] == employee_with_password["id"]
        assert data["due_date"] is not None
        assert data["column_id"] == test_board_with_column["column_ids"]["done"]
        assert data["order"] == 0
    
    def test_move_task_same_position_no_change(self, admin_client, test_board_with_column):
        """Test moving a task to its current position (no-op)."""
        # Arrange
        task_data = {
            "title": "Task",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        original_data = create_response.json()
        
        # Act - Move to same position
        move_data = {
            "column_id": test_board_with_column["column_ids"]["todo"],
            "order": 0
        }
        response = admin_client.patch(f"/api/tasks/{task_id}/move", json=move_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["column_id"] == original_data["column_id"]
        assert data["order"] == original_data["order"]
    
    def test_move_task_database_persistence(self, admin_client, test_board_with_column):
        """Test that task movement is properly persisted in database."""
        # Arrange
        task_data = {
            "title": "Task",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act
        move_data = {
            "column_id": test_board_with_column["column_ids"]["in_progress"],
            "order": 0
        }
        response = admin_client.patch(f"/api/tasks/{task_id}/move", json=move_data)
        assert response.status_code == 200
        
        # Assert - Verify in database
        db = TestingSessionLocal()
        task = db.query(Task).filter(Task.id == task_id).first()
        db.close()
        
        assert task is not None
        assert task.column_id == test_board_with_column["column_ids"]["in_progress"]
        assert task.order == 0
    
    def test_move_task_complex_reordering_scenario(self, admin_client, test_board_with_column):
        """Test complex scenario with multiple tasks and movements."""
        # Arrange - Create 5 tasks in To-Do
        task_ids = []
        for i in range(5):
            task_data = {
                "title": f"Task {i}",
                "priority": "medium",
                "column_id": test_board_with_column["column_ids"]["todo"]
            }
            response = admin_client.post("/api/tasks", json=task_data)
            task_ids.append(response.json()["id"])
        
        # Create 2 tasks in In Progress
        for i in range(2):
            task_data = {
                "title": f"Progress Task {i}",
                "priority": "medium",
                "column_id": test_board_with_column["column_ids"]["in_progress"]
            }
            admin_client.post("/api/tasks", json=task_data)
        
        # Act - Move task from position 2 in To-Do to position 1 in In Progress
        move_data = {
            "column_id": test_board_with_column["column_ids"]["in_progress"],
            "order": 1
        }
        response = admin_client.patch(f"/api/tasks/{task_ids[2]}/move", json=move_data)
        
        # Assert
        assert response.status_code == 200
        assert response.json()["order"] == 1
        
        # Verify To-Do column has 4 tasks with correct order
        db = TestingSessionLocal()
        todo_tasks = db.query(Task).filter(
            Task.column_id == test_board_with_column["column_ids"]["todo"]
        ).order_by(Task.order).all()
        assert len(todo_tasks) == 4
        assert todo_tasks[0].order == 0
        assert todo_tasks[1].order == 1
        assert todo_tasks[2].order == 2
        assert todo_tasks[3].order == 3
        
        # Verify In Progress column has 3 tasks with correct order
        progress_tasks = db.query(Task).filter(
            Task.column_id == test_board_with_column["column_ids"]["in_progress"]
        ).order_by(Task.order).all()
        db.close()
        
        assert len(progress_tasks) == 3
        assert progress_tasks[0].title == "Progress Task 0"
        assert progress_tasks[0].order == 0
        assert progress_tasks[1].title == "Task 2"
        assert progress_tasks[1].order == 1
        assert progress_tasks[2].title == "Progress Task 1"
        assert progress_tasks[2].order == 2
    
    def test_move_task_missing_column_id(self, admin_client, test_board_with_column):
        """Test that move request without column_id fails."""
        # Arrange
        task_data = {
            "title": "Task",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act
        move_data = {
            "order": 0
            # Missing column_id
        }
        response = admin_client.patch(f"/api/tasks/{task_id}/move", json=move_data)
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_move_task_missing_order(self, admin_client, test_board_with_column):
        """Test that move request without order fails."""
        # Arrange
        task_data = {
            "title": "Task",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act
        move_data = {
            "column_id": test_board_with_column["column_ids"]["in_progress"]
            # Missing order
        }
        response = admin_client.patch(f"/api/tasks/{task_id}/move", json=move_data)
        
        # Assert
        assert response.status_code == 422  # Validation error



class TestDeleteTask:
    """Tests for DELETE /api/tasks/:id endpoint."""
    
    def test_delete_task_success(self, admin_client, test_board_with_column):
        """Test successful task deletion by admin."""
        # Arrange - Create a task
        task_data = {
            "title": "Task to Delete",
            "description": "This task will be deleted",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]
        
        # Act - Delete the task
        response = admin_client.delete(f"/api/tasks/{task_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Task deleted successfully"
        assert data["id"] == task_id
        
        # Verify task no longer exists in database
        db = TestingSessionLocal()
        task = db.query(Task).filter(Task.id == task_id).first()
        db.close()
        assert task is None
    
    def test_delete_task_subsequent_get_returns_404(self, admin_client, test_board_with_column):
        """Test that after deletion, subsequent attempts to retrieve the task return 404."""
        # Arrange - Create a task
        task_data = {
            "title": "Task to Delete",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act - Delete the task
        delete_response = admin_client.delete(f"/api/tasks/{task_id}")
        assert delete_response.status_code == 200
        
        # Assert - Try to update the deleted task (should fail)
        update_response = admin_client.patch(f"/api/tasks/{task_id}", json={"title": "Updated"})
        assert update_response.status_code == 404
        assert "task" in update_response.json()["detail"].lower()
    
    def test_delete_task_nonexistent_task(self, admin_client):
        """Test that deleting a non-existent task returns 404."""
        # Act
        response = admin_client.delete("/api/tasks/99999")
        
        # Assert
        assert response.status_code == 404
        assert "task" in response.json()["detail"].lower()
    
    def test_delete_task_employee_forbidden(self, employee_client, admin_client, test_board_with_column):
        """Test that employee users cannot delete tasks."""
        # Arrange - Admin creates a task
        task_data = {
            "title": "Task",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act - Employee tries to delete
        response = employee_client.delete(f"/api/tasks/{task_id}")
        
        # Assert
        assert response.status_code == 403
        assert "admin" in response.json()["detail"].lower()
        
        # Verify task still exists
        db = TestingSessionLocal()
        task = db.query(Task).filter(Task.id == task_id).first()
        db.close()
        assert task is not None
    
    def test_delete_task_unauthenticated(self, test_client, admin_client, test_board_with_column):
        """Test that unauthenticated users cannot delete tasks."""
        # Arrange - Create a task
        task_data = {
            "title": "Task",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act - Try to delete without authentication
        response = test_client.delete(f"/api/tasks/{task_id}")
        
        # Assert
        assert response.status_code == 401
        
        # Verify task still exists
        db = TestingSessionLocal()
        task = db.query(Task).filter(Task.id == task_id).first()
        db.close()
        assert task is not None
    
    def test_delete_task_with_assignee(self, admin_client, test_board_with_column, employee_with_password):
        """Test deleting a task that has an assignee."""
        # Arrange - Create task with assignee
        task_data = {
            "title": "Assigned Task",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"],
            "assignee_id": employee_with_password["id"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        assert create_response.json()["assignee_id"] == employee_with_password["id"]
        
        # Act - Delete the task
        response = admin_client.delete(f"/api/tasks/{task_id}")
        
        # Assert
        assert response.status_code == 200
        
        # Verify task is deleted
        db = TestingSessionLocal()
        task = db.query(Task).filter(Task.id == task_id).first()
        db.close()
        assert task is None
    
    def test_delete_task_with_all_fields(self, admin_client, test_board_with_column, admin_with_password):
        """Test deleting a task with all optional fields populated."""
        # Arrange - Create task with all fields
        due_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
        task_data = {
            "title": "Complete Task",
            "description": "# Full task\n\nWith all fields",
            "due_date": due_date,
            "priority": "high",
            "column_id": test_board_with_column["column_ids"]["in_progress"],
            "assignee_id": admin_with_password["id"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act - Delete the task
        response = admin_client.delete(f"/api/tasks/{task_id}")
        
        # Assert
        assert response.status_code == 200
        
        # Verify task is deleted
        db = TestingSessionLocal()
        task = db.query(Task).filter(Task.id == task_id).first()
        db.close()
        assert task is None
    
    def test_delete_multiple_tasks(self, admin_client, test_board_with_column):
        """Test deleting multiple tasks in sequence."""
        # Arrange - Create three tasks
        task_ids = []
        for i in range(3):
            task_data = {
                "title": f"Task {i}",
                "priority": "medium",
                "column_id": test_board_with_column["column_ids"]["todo"]
            }
            response = admin_client.post("/api/tasks", json=task_data)
            task_ids.append(response.json()["id"])
        
        # Act - Delete all tasks
        for task_id in task_ids:
            response = admin_client.delete(f"/api/tasks/{task_id}")
            assert response.status_code == 200
        
        # Assert - Verify all tasks are deleted
        db = TestingSessionLocal()
        for task_id in task_ids:
            task = db.query(Task).filter(Task.id == task_id).first()
            assert task is None
        db.close()
    
    def test_delete_task_twice(self, admin_client, test_board_with_column):
        """Test that deleting the same task twice returns 404 on second attempt."""
        # Arrange - Create a task
        task_data = {
            "title": "Task",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act - Delete the task first time
        response1 = admin_client.delete(f"/api/tasks/{task_id}")
        assert response1.status_code == 200
        
        # Act - Try to delete again
        response2 = admin_client.delete(f"/api/tasks/{task_id}")
        
        # Assert
        assert response2.status_code == 404
        assert "task" in response2.json()["detail"].lower()
    
    def test_delete_task_from_column_with_multiple_tasks(self, admin_client, test_board_with_column):
        """Test deleting a task from a column that has multiple tasks."""
        # Arrange - Create three tasks in the same column
        task_ids = []
        for i in range(3):
            task_data = {
                "title": f"Task {i}",
                "priority": "medium",
                "column_id": test_board_with_column["column_ids"]["todo"]
            }
            response = admin_client.post("/api/tasks", json=task_data)
            task_ids.append(response.json()["id"])
        
        # Act - Delete the middle task
        response = admin_client.delete(f"/api/tasks/{task_ids[1]}")
        
        # Assert
        assert response.status_code == 200
        
        # Verify middle task is deleted
        db = TestingSessionLocal()
        deleted_task = db.query(Task).filter(Task.id == task_ids[1]).first()
        assert deleted_task is None
        
        # Verify other tasks still exist
        task0 = db.query(Task).filter(Task.id == task_ids[0]).first()
        task2 = db.query(Task).filter(Task.id == task_ids[2]).first()
        assert task0 is not None
        assert task2 is not None
        db.close()
    
    def test_delete_task_database_persistence(self, admin_client, test_board_with_column):
        """Test that task deletion is properly persisted in database."""
        # Arrange - Create a task
        task_data = {
            "title": "Task to Delete",
            "description": "Testing database persistence",
            "priority": "high",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Verify task exists before deletion
        db = TestingSessionLocal()
        task_before = db.query(Task).filter(Task.id == task_id).first()
        assert task_before is not None
        db.close()
        
        # Act - Delete the task
        response = admin_client.delete(f"/api/tasks/{task_id}")
        assert response.status_code == 200
        
        # Assert - Verify task is deleted from database
        db = TestingSessionLocal()
        task_after = db.query(Task).filter(Task.id == task_id).first()
        db.close()
        assert task_after is None
    
    def test_delete_task_response_format(self, admin_client, test_board_with_column):
        """Test that delete response has correct format."""
        # Arrange - Create a task
        task_data = {
            "title": "Task",
            "priority": "medium",
            "column_id": test_board_with_column["column_ids"]["todo"]
        }
        create_response = admin_client.post("/api/tasks", json=task_data)
        task_id = create_response.json()["id"]
        
        # Act - Delete the task
        response = admin_client.delete(f"/api/tasks/{task_id}")
        
        # Assert - Check response format
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "id" in data
        assert isinstance(data["message"], str)
        assert isinstance(data["id"], int)
        assert data["id"] == task_id
    
    def test_delete_task_different_priorities(self, admin_client, test_board_with_column):
        """Test deleting tasks with different priorities."""
        # Arrange - Create tasks with different priorities
        priorities = ["low", "medium", "high"]
        task_ids = []
        
        for priority in priorities:
            task_data = {
                "title": f"Task with {priority} priority",
                "priority": priority,
                "column_id": test_board_with_column["column_ids"]["todo"]
            }
            response = admin_client.post("/api/tasks", json=task_data)
            task_ids.append(response.json()["id"])
        
        # Act & Assert - Delete each task
        for task_id in task_ids:
            response = admin_client.delete(f"/api/tasks/{task_id}")
            assert response.status_code == 200
            
            # Verify deletion
            db = TestingSessionLocal()
            task = db.query(Task).filter(Task.id == task_id).first()
            db.close()
            assert task is None
    
    def test_delete_task_from_different_columns(self, admin_client, test_board_with_column):
        """Test deleting tasks from different columns."""
        # Arrange - Create tasks in different columns
        column_ids = [
            test_board_with_column["column_ids"]["todo"],
            test_board_with_column["column_ids"]["in_progress"],
            test_board_with_column["column_ids"]["done"]
        ]
        task_ids = []
        
        for column_id in column_ids:
            task_data = {
                "title": f"Task in column {column_id}",
                "priority": "medium",
                "column_id": column_id
            }
            response = admin_client.post("/api/tasks", json=task_data)
            task_ids.append(response.json()["id"])
        
        # Act & Assert - Delete each task
        for task_id in task_ids:
            response = admin_client.delete(f"/api/tasks/{task_id}")
            assert response.status_code == 200
            
            # Verify deletion
            db = TestingSessionLocal()
            task = db.query(Task).filter(Task.id == task_id).first()
            db.close()
            assert task is None
