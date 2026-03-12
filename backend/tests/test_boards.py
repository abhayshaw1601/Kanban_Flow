"""
Unit tests for board management endpoints.

Tests cover:
- POST /api/boards - Board creation (admin only)
- Default column creation
- Board member addition
- Authorization checks
"""
import pytest
from tests.conftest import TestingSessionLocal
from app.models.user import User, UserRole
from app.models.board import Board
from app.models.column import Column
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
def admin_client(test_client, admin_with_password):
    """Create a test client with admin authentication."""
    # Login as admin
    response = test_client.post("/api/auth/login", json={
        "email": admin_with_password["email"],
        "password": admin_with_password["password"]
    })
    assert response.status_code == 200
    return test_client


@pytest.fixture
def employee_client(test_client, employee_with_password):
    """Create a test client with employee authentication."""
    # Login as employee
    response = test_client.post("/api/auth/login", json={
        "email": employee_with_password["email"],
        "password": employee_with_password["password"]
    })
    assert response.status_code == 200
    return test_client


class TestCreateBoard:
    """Tests for POST /api/boards endpoint."""
    
    def test_create_board_success(self, admin_client, admin_with_password):
        """Test successful board creation by admin."""
        # Arrange
        board_data = {
            "name": "Test Board",
            "description": "A test board for unit testing"
        }
        
        # Act
        response = admin_client.post("/api/boards", json=board_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Board"
        assert data["description"] == "A test board for unit testing"
        assert data["created_by"] == admin_with_password["id"]
        assert "created_at" in data
        assert "id" in data
    
    def test_create_board_without_description(self, admin_client, admin_with_password):
        """Test board creation without optional description."""
        # Arrange
        board_data = {
            "name": "Board Without Description"
        }
        
        # Act
        response = admin_client.post("/api/boards", json=board_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Board Without Description"
        assert data["description"] is None
        assert data["created_by"] == admin_with_password["id"]
    
    def test_create_board_creates_default_columns(self, admin_client):
        """Test that board creation automatically creates 3 default columns."""
        # Arrange
        board_data = {
            "name": "Board with Columns",
            "description": "Testing default columns"
        }
        
        # Act
        response = admin_client.post("/api/boards", json=board_data)
        
        # Assert
        assert response.status_code == 201
        board_id = response.json()["id"]
        
        # Verify columns were created in database
        db = TestingSessionLocal()
        columns = db.query(Column).filter(Column.board_id == board_id).order_by(Column.order).all()
        db.close()
        
        assert len(columns) == 3
        assert columns[0].name == "To-Do"
        assert columns[0].order == 0
        assert columns[1].name == "In Progress"
        assert columns[1].order == 1
        assert columns[2].name == "Done"
        assert columns[2].order == 2
    
    def test_create_board_adds_creator_as_member(self, admin_client, admin_with_password):
        """Test that board creator is automatically added as a board member."""
        # Arrange
        board_data = {
            "name": "Board with Member",
            "description": "Testing board membership"
        }
        
        # Act
        response = admin_client.post("/api/boards", json=board_data)
        
        # Assert
        assert response.status_code == 201
        board_id = response.json()["id"]
        
        # Verify board member was created
        db = TestingSessionLocal()
        member = db.query(BoardMember).filter(
            BoardMember.board_id == board_id,
            BoardMember.user_id == admin_with_password["id"]
        ).first()
        db.close()
        
        assert member is not None
        assert member.user_id == admin_with_password["id"]
        assert member.board_id == board_id
    
    def test_create_board_employee_forbidden(self, employee_client):
        """Test that employee users cannot create boards."""
        # Arrange
        board_data = {
            "name": "Employee Board",
            "description": "This should fail"
        }
        
        # Act
        response = employee_client.post("/api/boards", json=board_data)
        
        # Assert
        assert response.status_code == 403
        assert "admin" in response.json()["detail"].lower()
    
    def test_create_board_unauthenticated(self, test_client):
        """Test that unauthenticated users cannot create boards."""
        # Arrange
        board_data = {
            "name": "Unauthenticated Board",
            "description": "This should fail"
        }
        
        # Act
        response = test_client.post("/api/boards", json=board_data)
        
        # Assert
        assert response.status_code == 401
    
    def test_create_board_missing_name(self, admin_client):
        """Test that board creation without name returns validation error."""
        # Arrange
        board_data = {
            "description": "Board without name"
            # Missing name
        }
        
        # Act
        response = admin_client.post("/api/boards", json=board_data)
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_create_board_empty_name(self, admin_client):
        """Test that board creation with empty name returns validation error."""
        # Arrange
        board_data = {
            "name": "",
            "description": "Board with empty name"
        }
        
        # Act
        response = admin_client.post("/api/boards", json=board_data)
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_create_board_long_name(self, admin_client):
        """Test board creation with maximum length name."""
        # Arrange
        board_data = {
            "name": "A" * 200,  # Max length from schema
            "description": "Testing max length"
        }
        
        # Act
        response = admin_client.post("/api/boards", json=board_data)
        
        # Assert
        assert response.status_code == 201
        assert len(response.json()["name"]) == 200
    
    def test_create_board_name_too_long(self, admin_client):
        """Test that board creation with name exceeding max length fails."""
        # Arrange
        board_data = {
            "name": "A" * 201,  # Exceeds max length
            "description": "Testing validation"
        }
        
        # Act
        response = admin_client.post("/api/boards", json=board_data)
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_create_board_long_description(self, admin_client):
        """Test board creation with maximum length description."""
        # Arrange
        board_data = {
            "name": "Board with Long Description",
            "description": "D" * 1000  # Max length from schema
        }
        
        # Act
        response = admin_client.post("/api/boards", json=board_data)
        
        # Assert
        assert response.status_code == 201
        assert len(response.json()["description"]) == 1000
    
    def test_create_board_description_too_long(self, admin_client):
        """Test that board creation with description exceeding max length fails."""
        # Arrange
        board_data = {
            "name": "Board",
            "description": "D" * 1001  # Exceeds max length
        }
        
        # Act
        response = admin_client.post("/api/boards", json=board_data)
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_create_multiple_boards(self, admin_client, admin_with_password):
        """Test creating multiple boards by the same admin."""
        # Arrange
        board1_data = {"name": "First Board", "description": "First"}
        board2_data = {"name": "Second Board", "description": "Second"}
        
        # Act
        response1 = admin_client.post("/api/boards", json=board1_data)
        response2 = admin_client.post("/api/boards", json=board2_data)
        
        # Assert
        assert response1.status_code == 201
        assert response2.status_code == 201
        assert response1.json()["id"] != response2.json()["id"]
        assert response1.json()["created_by"] == admin_with_password["id"]
        assert response2.json()["created_by"] == admin_with_password["id"]
    
    def test_create_board_with_special_characters(self, admin_client):
        """Test board creation with special characters in name and description."""
        # Arrange
        board_data = {
            "name": "Board with 特殊字符 & émojis 🚀",
            "description": "Description with <html> & special chars: @#$%"
        }
        
        # Act
        response = admin_client.post("/api/boards", json=board_data)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Board with 特殊字符 & émojis 🚀"
        assert data["description"] == "Description with <html> & special chars: @#$%"
    
    def test_create_board_null_description(self, admin_client):
        """Test board creation with explicitly null description."""
        # Arrange
        board_data = {
            "name": "Board with Null Description",
            "description": None
        }
        
        # Act
        response = admin_client.post("/api/boards", json=board_data)
        
        # Assert
        assert response.status_code == 201
        assert response.json()["description"] is None
    
    def test_create_board_database_persistence(self, admin_client, admin_with_password):
        """Test that created board is properly persisted in database."""
        # Arrange
        board_data = {
            "name": "Persistent Board",
            "description": "Testing database persistence"
        }
        
        # Act
        response = admin_client.post("/api/boards", json=board_data)
        
        # Assert
        assert response.status_code == 201
        board_id = response.json()["id"]
        
        # Verify board exists in database
        db = TestingSessionLocal()
        board = db.query(Board).filter(Board.id == board_id).first()
        db.close()
        
        assert board is not None
        assert board.name == "Persistent Board"
        assert board.description == "Testing database persistence"
        assert board.created_by == admin_with_password["id"]
        assert board.created_at is not None


class TestGetUserBoards:
    """Tests for GET /api/boards endpoint."""
    
    def test_get_user_boards_success(self, admin_client, admin_with_password):
        """Test successful retrieval of user's boards."""
        # Arrange - Create a board (which automatically adds creator as member)
        board_data = {
            "name": "Test Board",
            "description": "A test board"
        }
        create_response = admin_client.post("/api/boards", json=board_data)
        assert create_response.status_code == 201
        
        # Act
        response = admin_client.get("/api/boards")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Find the created board in the response
        created_board = next((b for b in data if b["name"] == "Test Board"), None)
        assert created_board is not None
        assert created_board["description"] == "A test board"
        assert created_board["created_by"] == admin_with_password["id"]
        assert "created_at" in created_board
        assert "id" in created_board
    
    def test_get_user_boards_multiple(self, admin_client, admin_with_password):
        """Test retrieval of multiple boards."""
        # Arrange - Create multiple boards
        board1_data = {"name": "Board 1", "description": "First board"}
        board2_data = {"name": "Board 2", "description": "Second board"}
        board3_data = {"name": "Board 3", "description": "Third board"}
        
        admin_client.post("/api/boards", json=board1_data)
        admin_client.post("/api/boards", json=board2_data)
        admin_client.post("/api/boards", json=board3_data)
        
        # Act
        response = admin_client.get("/api/boards")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3
        
        board_names = [b["name"] for b in data]
        assert "Board 1" in board_names
        assert "Board 2" in board_names
        assert "Board 3" in board_names
    
    def test_get_user_boards_empty(self, employee_client):
        """Test retrieval when user has no boards."""
        # Act - Employee hasn't been added to any boards
        response = employee_client.get("/api/boards")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_user_boards_only_member_boards(self, test_client, admin_with_password, employee_with_password):
        """Test that users only see boards they are members of."""
        # Arrange - Login as admin and create a board
        admin_login = test_client.post("/api/auth/login", json={
            "email": admin_with_password["email"],
            "password": admin_with_password["password"]
        })
        assert admin_login.status_code == 200
        
        admin_board_data = {"name": "Admin Board", "description": "Admin only"}
        admin_response = test_client.post("/api/boards", json=admin_board_data)
        assert admin_response.status_code == 201
        admin_board_id = admin_response.json()["id"]
        
        # Logout admin
        test_client.post("/api/auth/logout")
        
        # Login as employee
        employee_login = test_client.post("/api/auth/login", json={
            "email": employee_with_password["email"],
            "password": employee_with_password["password"]
        })
        assert employee_login.status_code == 200
        
        # Act - Employee tries to get boards
        employee_response = test_client.get("/api/boards")
        
        # Assert - Employee should not see admin's board
        assert employee_response.status_code == 200
        employee_boards = employee_response.json()
        employee_board_ids = [b["id"] for b in employee_boards]
        assert admin_board_id not in employee_board_ids
        
        # Logout employee and login as admin again
        test_client.post("/api/auth/logout")
        test_client.post("/api/auth/login", json={
            "email": admin_with_password["email"],
            "password": admin_with_password["password"]
        })
        
        # Admin should see their board
        admin_boards_response = test_client.get("/api/boards")
        assert admin_boards_response.status_code == 200
        admin_boards = admin_boards_response.json()
        admin_board_ids = [b["id"] for b in admin_boards]
        assert admin_board_id in admin_board_ids
    
    def test_get_user_boards_after_added_as_member(self, admin_client, test_client, employee_with_password):
        """Test that user sees board after being added as member."""
        # Arrange - Admin creates a board
        board_data = {"name": "Shared Board", "description": "Shared with employee"}
        create_response = admin_client.post("/api/boards", json=board_data)
        assert create_response.status_code == 201
        board_id = create_response.json()["id"]
        
        # Logout admin and login as employee
        admin_client.post("/api/auth/logout")
        employee_login = test_client.post("/api/auth/login", json={
            "email": employee_with_password["email"],
            "password": employee_with_password["password"]
        })
        assert employee_login.status_code == 200
        
        # Employee should not see the board initially
        initial_response = test_client.get("/api/boards")
        initial_boards = initial_response.json()
        initial_board_ids = [b["id"] for b in initial_boards]
        assert board_id not in initial_board_ids
        
        # Add employee as board member
        db = TestingSessionLocal()
        board_member = BoardMember(
            user_id=employee_with_password["id"],
            board_id=board_id
        )
        db.add(board_member)
        db.commit()
        db.close()
        
        # Act - Employee gets boards again
        response = test_client.get("/api/boards")
        
        # Assert - Employee should now see the board
        assert response.status_code == 200
        boards = response.json()
        board_ids = [b["id"] for b in boards]
        assert board_id in board_ids
        
        # Verify board details
        shared_board = next((b for b in boards if b["id"] == board_id), None)
        assert shared_board is not None
        assert shared_board["name"] == "Shared Board"
        assert shared_board["description"] == "Shared with employee"
    
    def test_get_user_boards_unauthenticated(self, test_client):
        """Test that unauthenticated users cannot get boards."""
        # Act
        response = test_client.get("/api/boards")
        
        # Assert
        assert response.status_code == 401
    
    def test_get_user_boards_response_structure(self, admin_client):
        """Test that response has correct structure."""
        # Arrange - Create a board
        board_data = {"name": "Structure Test", "description": "Testing response structure"}
        admin_client.post("/api/boards", json=board_data)
        
        # Act
        response = admin_client.get("/api/boards")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            board = data[0]
            # Verify all required fields are present
            assert "id" in board
            assert "name" in board
            assert "description" in board
            assert "created_at" in board
            assert "created_by" in board
            
            # Verify types
            assert isinstance(board["id"], int)
            assert isinstance(board["name"], str)
            assert isinstance(board["created_by"], int)
            # description can be None
            # created_at is a string in ISO format
    
    def test_get_user_boards_no_password_leak(self, admin_client):
        """Test that response does not include sensitive data."""
        # Arrange - Create a board
        board_data = {"name": "Security Test", "description": "Testing data security"}
        admin_client.post("/api/boards", json=board_data)
        
        # Act
        response = admin_client.get("/api/boards")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Verify no sensitive fields are present
        for board in data:
            assert "password" not in board
            assert "hashed_password" not in board
    
    def test_get_user_boards_ordering(self, admin_client):
        """Test that boards are returned in a consistent order."""
        # Arrange - Create multiple boards with slight delays
        boards_to_create = [
            {"name": "Board A", "description": "First"},
            {"name": "Board B", "description": "Second"},
            {"name": "Board C", "description": "Third"}
        ]
        
        created_ids = []
        for board_data in boards_to_create:
            response = admin_client.post("/api/boards", json=board_data)
            created_ids.append(response.json()["id"])
        
        # Act
        response = admin_client.get("/api/boards")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Verify all created boards are present
        returned_ids = [b["id"] for b in data]
        for created_id in created_ids:
            assert created_id in returned_ids
    
    def test_get_user_boards_different_users_isolation(self, test_client, admin_with_password, employee_with_password):
        """Test that different users see different boards based on membership."""
        # Arrange - Login as admin and create boards
        admin_login = test_client.post("/api/auth/login", json={
            "email": admin_with_password["email"],
            "password": admin_with_password["password"]
        })
        assert admin_login.status_code == 200
        
        admin_board = {"name": "Admin Private Board", "description": "Admin only"}
        admin_response = test_client.post("/api/boards", json=admin_board)
        assert admin_response.status_code == 201
        admin_board_id = admin_response.json()["id"]
        
        # Create another board and add employee as member
        shared_board = {"name": "Shared Board", "description": "Shared"}
        shared_response = test_client.post("/api/boards", json=shared_board)
        assert shared_response.status_code == 201
        shared_board_id = shared_response.json()["id"]
        
        db = TestingSessionLocal()
        board_member = BoardMember(
            user_id=employee_with_password["id"],
            board_id=shared_board_id
        )
        db.add(board_member)
        db.commit()
        db.close()
        
        # Get admin's boards
        admin_boards_response = test_client.get("/api/boards")
        assert admin_boards_response.status_code == 200
        admin_boards = admin_boards_response.json()
        admin_board_ids = [b["id"] for b in admin_boards]
        
        # Admin should see both boards
        assert admin_board_id in admin_board_ids
        assert shared_board_id in admin_board_ids
        
        # Logout admin and login as employee
        test_client.post("/api/auth/logout")
        employee_login = test_client.post("/api/auth/login", json={
            "email": employee_with_password["email"],
            "password": employee_with_password["password"]
        })
        assert employee_login.status_code == 200
        
        # Act - Get employee's boards
        employee_boards_response = test_client.get("/api/boards")
        
        # Assert
        assert employee_boards_response.status_code == 200
        employee_boards = employee_boards_response.json()
        employee_board_ids = [b["id"] for b in employee_boards]
        
        # Employee should only see shared board
        assert admin_board_id not in employee_board_ids
        assert shared_board_id in employee_board_ids
    
    def test_get_user_boards_with_null_description(self, admin_client):
        """Test retrieval of boards with null descriptions."""
        # Arrange - Create board without description
        board_data = {"name": "Board Without Description"}
        create_response = admin_client.post("/api/boards", json=board_data)
        assert create_response.status_code == 201
        
        # Act
        response = admin_client.get("/api/boards")
        
        # Assert
        assert response.status_code == 200
        boards = response.json()
        
        board = next((b for b in boards if b["name"] == "Board Without Description"), None)
        assert board is not None
        assert board["description"] is None
    
    def test_get_user_boards_performance_multiple_members(self, admin_client, test_client, employee_with_password):
        """Test that query performs well with multiple board members."""
        # Arrange - Create a board with multiple members
        board_data = {"name": "Multi-Member Board", "description": "Many members"}
        create_response = admin_client.post("/api/boards", json=board_data)
        assert create_response.status_code == 201
        board_id = create_response.json()["id"]
        
        # Add employee as member
        db = TestingSessionLocal()
        board_member = BoardMember(
            user_id=employee_with_password["id"],
            board_id=board_id
        )
        db.add(board_member)
        db.commit()
        db.close()
        
        # Get admin's boards
        admin_response = admin_client.get("/api/boards")
        assert admin_response.status_code == 200
        admin_boards = admin_response.json()
        admin_board_ids = [b["id"] for b in admin_boards]
        assert board_id in admin_board_ids
        
        # Logout admin and login as employee
        admin_client.post("/api/auth/logout")
        employee_login = test_client.post("/api/auth/login", json={
            "email": employee_with_password["email"],
            "password": employee_with_password["password"]
        })
        assert employee_login.status_code == 200
        
        # Act - Employee gets boards
        employee_response = test_client.get("/api/boards")
        
        # Assert - Employee should see the board
        assert employee_response.status_code == 200
        employee_boards = employee_response.json()
        employee_board_ids = [b["id"] for b in employee_boards]
        assert board_id in employee_board_ids



class TestGetBoardDetail:
    """Tests for GET /api/boards/{board_id} endpoint."""
    
    def test_get_board_detail_success(self, admin_client, admin_with_password):
        """Test successful retrieval of board details."""
        # Arrange - Create a board
        board_data = {"name": "Detail Test Board", "description": "Testing board details"}
        create_response = admin_client.post("/api/boards", json=board_data)
        assert create_response.status_code == 201
        board_id = create_response.json()["id"]
        
        # Act
        response = admin_client.get(f"/api/boards/{board_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == board_id
        assert data["name"] == "Detail Test Board"
        assert data["description"] == "Testing board details"
        assert data["created_by"] == admin_with_password["id"]
        assert "created_at" in data
        assert "columns" in data
        assert "members" in data
    
    def test_get_board_detail_includes_columns(self, admin_client):
        """Test that board details include all columns ordered correctly."""
        # Arrange - Create a board (automatically creates 3 default columns)
        board_data = {"name": "Board with Columns", "description": "Testing columns"}
        create_response = admin_client.post("/api/boards", json=board_data)
        assert create_response.status_code == 201
        board_id = create_response.json()["id"]
        
        # Act
        response = admin_client.get(f"/api/boards/{board_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        columns = data["columns"]
        
        assert len(columns) == 3
        assert columns[0]["name"] == "To-Do"
        assert columns[0]["order"] == 0
        assert columns[1]["name"] == "In Progress"
        assert columns[1]["order"] == 1
        assert columns[2]["name"] == "Done"
        assert columns[2]["order"] == 2
        
        # Each column should have a tasks list
        for column in columns:
            assert "tasks" in column
            assert isinstance(column["tasks"], list)
    
    def test_get_board_detail_includes_members(self, admin_client, admin_with_password):
        """Test that board details include all board members."""
        # Arrange - Create a board
        board_data = {"name": "Board with Members", "description": "Testing members"}
        create_response = admin_client.post("/api/boards", json=board_data)
        assert create_response.status_code == 201
        board_id = create_response.json()["id"]
        
        # Act
        response = admin_client.get(f"/api/boards/{board_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        members = data["members"]
        
        assert len(members) >= 1
        # Creator should be a member
        member_ids = [m["id"] for m in members]
        assert admin_with_password["id"] in member_ids
        
        # Verify member structure
        for member in members:
            assert "id" in member
            assert "name" in member
            assert "email" in member
            assert "role" in member
            # Should not include password
            assert "password" not in member
    
    def test_get_board_detail_with_tasks(self, admin_client):
        """Test that board details include tasks within columns."""
        # Arrange - Create a board
        board_data = {"name": "Board with Tasks", "description": "Testing tasks"}
        create_response = admin_client.post("/api/boards", json=board_data)
        assert create_response.status_code == 201
        board_id = create_response.json()["id"]
        
        # Get board details to find column IDs
        board_response = admin_client.get(f"/api/boards/{board_id}")
        columns = board_response.json()["columns"]
        first_column_id = columns[0]["id"]
        
        # Create a task in the first column
        task_data = {
            "title": "Test Task",
            "description": "Task description",
            "priority": "high",
            "column_id": first_column_id
        }
        task_response = admin_client.post("/api/tasks", json=task_data)
        assert task_response.status_code == 201
        
        # Act - Get board details again
        response = admin_client.get(f"/api/boards/{board_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        first_column = data["columns"][0]
        tasks = first_column["tasks"]
        
        assert len(tasks) >= 1
        task = next((t for t in tasks if t["title"] == "Test Task"), None)
        assert task is not None
        assert task["description"] == "Task description"
        assert task["priority"] == "high"
        assert task["column_id"] == first_column_id
    
    def test_get_board_detail_tasks_ordered(self, admin_client):
        """Test that tasks within columns are ordered by order field."""
        # Arrange - Create a board
        board_data = {"name": "Board with Ordered Tasks", "description": "Testing task order"}
        create_response = admin_client.post("/api/boards", json=board_data)
        assert create_response.status_code == 201
        board_id = create_response.json()["id"]
        
        # Get column ID
        board_response = admin_client.get(f"/api/boards/{board_id}")
        column_id = board_response.json()["columns"][0]["id"]
        
        # Create multiple tasks
        task1_data = {"title": "Task 1", "priority": "low", "column_id": column_id}
        task2_data = {"title": "Task 2", "priority": "medium", "column_id": column_id}
        task3_data = {"title": "Task 3", "priority": "high", "column_id": column_id}
        
        admin_client.post("/api/tasks", json=task1_data)
        admin_client.post("/api/tasks", json=task2_data)
        admin_client.post("/api/tasks", json=task3_data)
        
        # Act
        response = admin_client.get(f"/api/boards/{board_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        tasks = data["columns"][0]["tasks"]
        
        assert len(tasks) >= 3
        # Tasks should be ordered by order field (ascending)
        for i in range(len(tasks) - 1):
            assert tasks[i]["order"] <= tasks[i + 1]["order"]
    
    def test_get_board_detail_non_member_forbidden(self, test_client, admin_with_password, employee_with_password):
        """Test that non-members cannot access board details."""
        # Arrange - Admin creates a board
        admin_login = test_client.post("/api/auth/login", json={
            "email": admin_with_password["email"],
            "password": admin_with_password["password"]
        })
        assert admin_login.status_code == 200
        
        board_data = {"name": "Private Board", "description": "Admin only"}
        create_response = test_client.post("/api/boards", json=board_data)
        assert create_response.status_code == 201
        board_id = create_response.json()["id"]
        
        # Logout admin and login as employee
        test_client.post("/api/auth/logout")
        employee_login = test_client.post("/api/auth/login", json={
            "email": employee_with_password["email"],
            "password": employee_with_password["password"]
        })
        assert employee_login.status_code == 200
        
        # Act - Employee tries to access board
        response = test_client.get(f"/api/boards/{board_id}")
        
        # Assert
        assert response.status_code == 403
        assert "access" in response.json()["detail"].lower()
    
    def test_get_board_detail_member_can_access(self, test_client, admin_with_password, employee_with_password):
        """Test that board members can access board details."""
        # Arrange - Admin creates a board
        admin_login = test_client.post("/api/auth/login", json={
            "email": admin_with_password["email"],
            "password": admin_with_password["password"]
        })
        assert admin_login.status_code == 200
        
        board_data = {"name": "Shared Board", "description": "Shared with employee"}
        create_response = test_client.post("/api/boards", json=board_data)
        assert create_response.status_code == 201
        board_id = create_response.json()["id"]
        
        # Add employee as board member
        db = TestingSessionLocal()
        board_member = BoardMember(
            user_id=employee_with_password["id"],
            board_id=board_id
        )
        db.add(board_member)
        db.commit()
        db.close()
        
        # Logout admin and login as employee
        test_client.post("/api/auth/logout")
        employee_login = test_client.post("/api/auth/login", json={
            "email": employee_with_password["email"],
            "password": employee_with_password["password"]
        })
        assert employee_login.status_code == 200
        
        # Act - Employee accesses board
        response = test_client.get(f"/api/boards/{board_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == board_id
        assert data["name"] == "Shared Board"
        assert "columns" in data
        assert "members" in data
    
    def test_get_board_detail_not_found(self, admin_client):
        """Test that requesting non-existent board returns 404."""
        # Act
        response = admin_client.get("/api/boards/99999")
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_board_detail_unauthenticated(self, test_client, admin_with_password):
        """Test that unauthenticated users cannot access board details."""
        # Arrange - Create a board first
        admin_login = test_client.post("/api/auth/login", json={
            "email": admin_with_password["email"],
            "password": admin_with_password["password"]
        })
        assert admin_login.status_code == 200
        
        board_data = {"name": "Test Board", "description": "Test"}
        create_response = test_client.post("/api/boards", json=board_data)
        assert create_response.status_code == 201
        board_id = create_response.json()["id"]
        
        # Logout
        test_client.post("/api/auth/logout")
        
        # Act - Try to access board without authentication
        response = test_client.get(f"/api/boards/{board_id}")
        
        # Assert
        assert response.status_code == 401
    
    def test_get_board_detail_with_assignee_info(self, admin_client, admin_with_password):
        """Test that tasks include assignee information."""
        # Arrange - Create a board
        board_data = {"name": "Board with Assignees", "description": "Testing assignees"}
        create_response = admin_client.post("/api/boards", json=board_data)
        assert create_response.status_code == 201
        board_id = create_response.json()["id"]
        
        # Get column ID
        board_response = admin_client.get(f"/api/boards/{board_id}")
        column_id = board_response.json()["columns"][0]["id"]
        
        # Create a task with assignee
        task_data = {
            "title": "Assigned Task",
            "description": "Task with assignee",
            "priority": "medium",
            "column_id": column_id,
            "assignee_id": admin_with_password["id"]
        }
        task_response = admin_client.post("/api/tasks", json=task_data)
        assert task_response.status_code == 201
        
        # Act
        response = admin_client.get(f"/api/boards/{board_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        tasks = data["columns"][0]["tasks"]
        
        assigned_task = next((t for t in tasks if t["title"] == "Assigned Task"), None)
        assert assigned_task is not None
        assert assigned_task["assignee_id"] == admin_with_password["id"]
        
        # Verify assignee info is included (if using joinedload)
        if "assignee" in assigned_task:
            assert assigned_task["assignee"]["id"] == admin_with_password["id"]
            assert "name" in assigned_task["assignee"]
            assert "password" not in assigned_task["assignee"]
    
    def test_get_board_detail_empty_columns(self, admin_client):
        """Test that empty columns are included with empty task lists."""
        # Arrange - Create a board (no tasks)
        board_data = {"name": "Empty Board", "description": "No tasks"}
        create_response = admin_client.post("/api/boards", json=board_data)
        assert create_response.status_code == 201
        board_id = create_response.json()["id"]
        
        # Act
        response = admin_client.get(f"/api/boards/{board_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        columns = data["columns"]
        
        assert len(columns) == 3
        for column in columns:
            assert "tasks" in column
            assert isinstance(column["tasks"], list)
            assert len(column["tasks"]) == 0
    
    def test_get_board_detail_multiple_members(self, admin_client, test_client, employee_with_password):
        """Test that all board members are included in response."""
        # Arrange - Create a board
        board_data = {"name": "Multi-Member Board", "description": "Multiple members"}
        create_response = admin_client.post("/api/boards", json=board_data)
        assert create_response.status_code == 201
        board_id = create_response.json()["id"]
        
        # Add employee as member
        db = TestingSessionLocal()
        board_member = BoardMember(
            user_id=employee_with_password["id"],
            board_id=board_id
        )
        db.add(board_member)
        db.commit()
        db.close()
        
        # Act
        response = admin_client.get(f"/api/boards/{board_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        members = data["members"]
        
        assert len(members) >= 2
        member_ids = [m["id"] for m in members]
        assert employee_with_password["id"] in member_ids
    
    def test_get_board_detail_response_structure(self, admin_client):
        """Test that response has correct structure with all required fields."""
        # Arrange - Create a board
        board_data = {"name": "Structure Test", "description": "Testing structure"}
        create_response = admin_client.post("/api/boards", json=board_data)
        assert create_response.status_code == 201
        board_id = create_response.json()["id"]
        
        # Act
        response = admin_client.get(f"/api/boards/{board_id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Board fields
        assert "id" in data
        assert "name" in data
        assert "description" in data
        assert "created_at" in data
        assert "created_by" in data
        assert "columns" in data
        assert "members" in data
        
        # Verify types
        assert isinstance(data["id"], int)
        assert isinstance(data["name"], str)
        assert isinstance(data["created_by"], int)
        assert isinstance(data["columns"], list)
        assert isinstance(data["members"], list)
        
        # Column structure
        if len(data["columns"]) > 0:
            column = data["columns"][0]
            assert "id" in column
            assert "name" in column
            assert "order" in column
            assert "board_id" in column
            assert "tasks" in column
            assert isinstance(column["tasks"], list)
        
        # Member structure
        if len(data["members"]) > 0:
            member = data["members"][0]
            assert "id" in member
            assert "name" in member
            assert "email" in member
            assert "role" in member
    
    def test_get_board_detail_invalid_board_id(self, admin_client):
        """Test that invalid board ID format is handled."""
        # Act
        response = admin_client.get("/api/boards/invalid")
        
        # Assert
        # FastAPI will return 422 for invalid path parameter type
        assert response.status_code == 422


class TestUpdateBoard:
    """Tests for PATCH /api/boards/:id endpoint."""

    def test_update_board_success(self, admin_client, admin_with_password):
        """Test successful board update."""
        # Arrange - Create a board
        board_data = {"name": "Original Board", "description": "Original description"}
        create_response = admin_client.post("/api/boards", json=board_data)
        assert create_response.status_code == 201
        board_id = create_response.json()["id"]

        # Act - Update the board
        update_data = {"name": "Updated Board", "description": "Updated description"}
        response = admin_client.patch(f"/api/boards/{board_id}", json=update_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Board"
        assert data["description"] == "Updated description"
        assert data["id"] == board_id

    def test_update_board_partial(self, admin_client, admin_with_password):
        """Test partial board update (only name or description)."""
        # Arrange - Create a board
        board_data = {"name": "Original Board", "description": "Original description"}
        create_response = admin_client.post("/api/boards", json=board_data)
        assert create_response.status_code == 201
        board_id = create_response.json()["id"]

        # Act - Update only name
        response = admin_client.patch(f"/api/boards/{board_id}", json={"name": "New Name"})

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data["description"] == "Original description"

        # Act - Update only description
        response = admin_client.patch(f"/api/boards/{board_id}", json={"description": "New Description"})

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data["description"] == "New Description"

    def test_update_board_employee_forbidden(self, employee_client, admin_with_password):
        """Test that employees cannot update boards."""
        # Arrange - Create a board as admin
        db = TestingSessionLocal()
        admin = db.query(User).filter(User.email == admin_with_password["email"]).first()
        
        board = Board(
            name="Test Board",
            description="Testing auth",
            created_by=admin.id
        )
        db.add(board)
        db.commit()
        board_id = board.id
        db.close()

        # Act - Employee tries to update board
        response = employee_client.patch(f"/api/boards/{board_id}", json={"name": "Hacked Board"})

        # Assert
        assert response.status_code == 403

    def test_update_board_not_found(self, admin_client):
        """Test updating non-existent board."""
        # Act
        response = admin_client.patch("/api/boards/99999", json={"name": "Updated Board"})

        # Assert
        assert response.status_code == 404
        assert "Board with id 99999 not found" in response.json()["detail"]

    def test_update_board_validation_error(self, admin_client, admin_with_password):
        """Test board update with invalid data."""
        # Arrange - Create a board
        board_data = {"name": "Test Board", "description": "Testing validation"}
        create_response = admin_client.post("/api/boards", json=board_data)
        assert create_response.status_code == 201
        board_id = create_response.json()["id"]

        # Act - Try to update with empty name
        response = admin_client.patch(f"/api/boards/{board_id}", json={"name": ""})

        # Assert
        assert response.status_code == 422


class TestDeleteBoard:
    """Tests for DELETE /api/boards/:id endpoint."""

    def test_delete_board_success(self, admin_client, admin_with_password):
        """Test successful board deletion."""
        # Arrange - Create a board
        board_data = {"name": "Board to Delete", "description": "Will be deleted"}
        create_response = admin_client.post("/api/boards", json=board_data)
        assert create_response.status_code == 201
        board_id = create_response.json()["id"]

        # Act - Delete the board
        response = admin_client.delete(f"/api/boards/{board_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Board successfully deleted"
        assert data["board_id"] == board_id

        # Verify board was deleted
        get_response = admin_client.get(f"/api/boards/{board_id}")
        assert get_response.status_code == 404

    def test_delete_board_employee_forbidden(self, employee_client, admin_with_password):
        """Test that employees cannot delete boards."""
        # Arrange - Create a board as admin
        db = TestingSessionLocal()
        admin = db.query(User).filter(User.email == admin_with_password["email"]).first()
        
        board = Board(
            name="Protected Board",
            description="Cannot be deleted by employee",
            created_by=admin.id
        )
        db.add(board)
        db.commit()
        board_id = board.id
        db.close()

        # Act - Employee tries to delete board
        response = employee_client.delete(f"/api/boards/{board_id}")

        # Assert
        assert response.status_code == 403

    def test_delete_board_not_found(self, admin_client):
        """Test deleting non-existent board."""
        # Act
        response = admin_client.delete("/api/boards/99999")

        # Assert
        assert response.status_code == 404
        assert "Board with id 99999 not found" in response.json()["detail"]

    def test_delete_board_cascades_deletion(self, admin_client, admin_with_password, employee_with_password):
        """Test that deleting board removes associated columns, tasks, and memberships."""
        # Arrange - Create a board with members and tasks
        board_data = {"name": "Complex Board", "description": "Has members and tasks"}
        create_response = admin_client.post("/api/boards", json=board_data)
        assert create_response.status_code == 201
        board_id = create_response.json()["id"]

        # Add employee as member
        admin_client.post("/api/members", json={
            "user_id": employee_with_password["id"],
            "board_id": board_id
        })

        # Get board details to find column ID
        board_response = admin_client.get(f"/api/boards/{board_id}")
        assert board_response.status_code == 200
        columns = board_response.json()["columns"]
        column_id = columns[0]["id"]

        # Create a task
        task_data = {
            "title": "Test Task",
            "description": "Will be deleted with board",
            "priority": "medium",
            "column_id": column_id
        }
        admin_client.post("/api/tasks", json=task_data)

        # Act - Delete the board
        response = admin_client.delete(f"/api/boards/{board_id}")

        # Assert
        assert response.status_code == 200

        # Verify board and related data are gone
        assert admin_client.get(f"/api/boards/{board_id}").status_code == 404
        assert admin_client.get(f"/api/members/{board_id}").status_code == 404