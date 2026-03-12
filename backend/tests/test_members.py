"""
Unit tests for board membership endpoints.

Tests cover:
- GET /api/members/:boardId - Get board members
- Authorization checks
- Board membership verification
"""
import pytest
from tests.conftest import TestingSessionLocal
from app.models.user import User, UserRole
from app.models.board import Board
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
        "password": password,
        "name": admin.name
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
        "password": password,
        "name": employee.name
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


class TestGetBoardMembers:
    """Tests for GET /api/members/:boardId endpoint."""
    
    def test_get_board_members_success(self, admin_client, admin_with_password):
        """Test successful retrieval of board members."""
        # Arrange - Create a board (admin is automatically added as member)
        board_data = {"name": "Test Board", "description": "Testing members"}
        create_response = admin_client.post("/api/boards", json=board_data)
        assert create_response.status_code == 201
        board_id = create_response.json()["id"]
        
        # Act
        response = admin_client.get(f"/api/members/{board_id}")
        
        # Assert
        assert response.status_code == 200
        members = response.json()
        assert isinstance(members, list)
        assert len(members) == 1
        
        # Verify admin is in the members list
        admin_member = members[0]
        assert admin_member["id"] == admin_with_password["id"]
        assert admin_member["name"] == admin_with_password["name"]
        assert admin_member["email"] == admin_with_password["email"]
        assert admin_member["role"] == "admin"
        assert "created_at" in admin_member
        
        # Verify password is not included
        assert "password" not in admin_member
    
    def test_get_board_members_multiple_members(self, admin_client, admin_with_password, employee_with_password):
        """Test retrieval of board with multiple members."""
        # Arrange - Create a board
        board_data = {"name": "Multi-Member Board", "description": "Multiple members"}
        create_response = admin_client.post("/api/boards", json=board_data)
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
        
        # Act
        response = admin_client.get(f"/api/members/{board_id}")
        
        # Assert
        assert response.status_code == 200
        members = response.json()
        assert len(members) == 2
        
        # Verify both users are in the members list
        member_ids = [m["id"] for m in members]
        assert admin_with_password["id"] in member_ids
        assert employee_with_password["id"] in member_ids
        
        # Verify all required fields are present
        for member in members:
            assert "id" in member
            assert "name" in member
            assert "email" in member
            assert "role" in member
            assert "created_at" in member
            assert "password" not in member
    
    def test_get_board_members_employee_can_access(self, test_client, admin_with_password, employee_with_password):
        """Test that employee members can access board members list."""
        # Arrange - Login as admin and create a board
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
        
        # Act - Employee gets board members
        response = test_client.get(f"/api/members/{board_id}")
        
        # Assert
        assert response.status_code == 200
        members = response.json()
        assert len(members) == 2
        
        member_ids = [m["id"] for m in members]
        assert admin_with_password["id"] in member_ids
        assert employee_with_password["id"] in member_ids
    
    def test_get_board_members_non_member_forbidden(self, employee_client, admin_with_password):
        """Test that non-members cannot access board members list."""
        # Arrange - Create a board as admin (in a separate session)
        db = TestingSessionLocal()
        admin = db.query(User).filter(User.email == admin_with_password["email"]).first()
        
        board = Board(
            name="Private Board",
            description="Admin only",
            created_by=admin.id
        )
        db.add(board)
        db.flush()
        
        # Add admin as member
        board_member = BoardMember(
            user_id=admin.id,
            board_id=board.id
        )
        db.add(board_member)
        db.commit()
        board_id = board.id
        db.close()
        
        # Act - Employee (not a member) tries to get board members
        response = employee_client.get(f"/api/members/{board_id}")
        
        # Assert
        assert response.status_code == 403
        assert "access" in response.json()["detail"].lower()
    
    def test_get_board_members_board_not_found(self, admin_client):
        """Test that requesting members for non-existent board returns 404."""
        # Act
        response = admin_client.get("/api/members/99999")
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_board_members_unauthenticated(self, test_client, admin_with_password):
        """Test that unauthenticated users cannot access board members."""
        # Arrange - Create a board
        db = TestingSessionLocal()
        admin = db.query(User).filter(User.email == admin_with_password["email"]).first()
        
        board = Board(
            name="Test Board",
            description="Testing auth",
            created_by=admin.id
        )
        db.add(board)
        db.flush()
        
        board_member = BoardMember(
            user_id=admin.id,
            board_id=board.id
        )
        db.add(board_member)
        db.commit()
        board_id = board.id
        db.close()
        
        # Act - Unauthenticated request
        response = test_client.get(f"/api/members/{board_id}")
        
        # Assert
        assert response.status_code == 401
    
    def test_get_board_members_invalid_board_id(self, admin_client):
        """Test that invalid board ID returns appropriate error."""
        # Act
        response = admin_client.get("/api/members/invalid")
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_get_board_members_response_structure(self, admin_client, admin_with_password):
        """Test that response has correct structure."""
        # Arrange - Create a board
        board_data = {"name": "Structure Test", "description": "Testing response"}
        create_response = admin_client.post("/api/boards", json=board_data)
        assert create_response.status_code == 201
        board_id = create_response.json()["id"]
        
        # Act
        response = admin_client.get(f"/api/members/{board_id}")
        
        # Assert
        assert response.status_code == 200
        members = response.json()
        assert isinstance(members, list)
        
        for member in members:
            # Verify all required fields
            assert isinstance(member["id"], int)
            assert isinstance(member["name"], str)
            assert isinstance(member["email"], str)
            assert isinstance(member["role"], str)
            assert "created_at" in member
            
            # Verify role is valid
            assert member["role"] in ["admin", "employee"]
            
            # Verify no sensitive data
            assert "password" not in member
            assert "hashed_password" not in member
    
    def test_get_board_members_empty_board(self, admin_client, admin_with_password):
        """Test retrieval of board members when board has only creator."""
        # Arrange - Create a board
        board_data = {"name": "Single Member Board", "description": "Only creator"}
        create_response = admin_client.post("/api/boards", json=board_data)
        assert create_response.status_code == 201
        board_id = create_response.json()["id"]
        
        # Act
        response = admin_client.get(f"/api/members/{board_id}")
        
        # Assert
        assert response.status_code == 200
        members = response.json()
        assert len(members) == 1
        assert members[0]["id"] == admin_with_password["id"]
    
    def test_get_board_members_with_many_members(self, admin_client, admin_with_password):
        """Test retrieval of board with many members."""
        # Arrange - Create a board
        board_data = {"name": "Large Team Board", "description": "Many members"}
        create_response = admin_client.post("/api/boards", json=board_data)
        assert create_response.status_code == 201
        board_id = create_response.json()["id"]
        
        # Create multiple users and add them as members
        db = TestingSessionLocal()
        user_ids = []
        
        for i in range(5):
            user = User(
                name=f"User {i}",
                email=f"user{i}@example.com",
                password=get_password_hash("Password123"),
                role=UserRole.EMPLOYEE
            )
            db.add(user)
            db.flush()
            user_ids.append(user.id)
            
            board_member = BoardMember(
                user_id=user.id,
                board_id=board_id
            )
            db.add(board_member)
        
        db.commit()
        db.close()
        
        # Act
        response = admin_client.get(f"/api/members/{board_id}")
        
        # Assert
        assert response.status_code == 200
        members = response.json()
        assert len(members) == 6  # 5 new users + admin
        
        member_ids = [m["id"] for m in members]
        assert admin_with_password["id"] in member_ids
        for user_id in user_ids:
            assert user_id in member_ids
    
    def test_get_board_members_different_roles(self, admin_client, admin_with_password):
        """Test that members with different roles are all returned."""
        # Arrange - Create a board
        board_data = {"name": "Mixed Roles Board", "description": "Admin and employees"}
        create_response = admin_client.post("/api/boards", json=board_data)
        assert create_response.status_code == 201
        board_id = create_response.json()["id"]
        
        # Create another admin and an employee
        db = TestingSessionLocal()
        
        admin2 = User(
            name="Second Admin",
            email="admin2@example.com",
            password=get_password_hash("Password123"),
            role=UserRole.ADMIN
        )
        db.add(admin2)
        db.flush()
        
        employee = User(
            name="Employee",
            email="employee2@example.com",
            password=get_password_hash("Password123"),
            role=UserRole.EMPLOYEE
        )
        db.add(employee)
        db.flush()
        
        # Add both as members
        for user in [admin2, employee]:
            board_member = BoardMember(
                user_id=user.id,
                board_id=board_id
            )
            db.add(board_member)
        
        db.commit()
        db.close()
        
        # Act
        response = admin_client.get(f"/api/members/{board_id}")
        
        # Assert
        assert response.status_code == 200
        members = response.json()
        assert len(members) == 3
        
        # Verify roles are correct
        roles = [m["role"] for m in members]
        assert roles.count("admin") == 2
        assert roles.count("employee") == 1



class TestAddBoardMember:
    """Tests for POST /api/members endpoint."""
    
    def test_add_board_member_success(self, admin_client, admin_with_password, employee_with_password):
        """Test successful addition of a member to a board."""
        # Arrange - Create a board
        board_data = {"name": "Test Board", "description": "Testing member addition"}
        create_response = admin_client.post("/api/boards", json=board_data)
        assert create_response.status_code == 201
        board_id = create_response.json()["id"]
        
        # Act - Add employee to board
        response = admin_client.post("/api/members", json={
            "user_id": employee_with_password["id"],
            "board_id": board_id
        })
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "User successfully added to board"
        assert data["user_id"] == employee_with_password["id"]
        assert data["board_id"] == board_id
        
        # Verify member was actually added
        members_response = admin_client.get(f"/api/members/{board_id}")
        assert members_response.status_code == 200
        members = members_response.json()
        member_ids = [m["id"] for m in members]
        assert employee_with_password["id"] in member_ids
    
    def test_add_board_member_duplicate_graceful(self, admin_client, admin_with_password):
        """Test that adding a duplicate member is handled gracefully."""
        # Arrange - Create a board (admin is automatically added as member)
        board_data = {"name": "Test Board", "description": "Testing duplicate"}
        create_response = admin_client.post("/api/boards", json=board_data)
        assert create_response.status_code == 201
        board_id = create_response.json()["id"]
        
        # Act - Try to add admin again (already a member)
        response = admin_client.post("/api/members", json={
            "user_id": admin_with_password["id"],
            "board_id": board_id
        })
        
        # Assert - Should succeed with appropriate message
        assert response.status_code == 201
        data = response.json()
        assert "already a member" in data["message"].lower()
        assert data["user_id"] == admin_with_password["id"]
        assert data["board_id"] == board_id
        
        # Verify no duplicate was created
        members_response = admin_client.get(f"/api/members/{board_id}")
        assert members_response.status_code == 200
        members = members_response.json()
        admin_count = sum(1 for m in members if m["id"] == admin_with_password["id"])
        assert admin_count == 1
    
    def test_add_board_member_employee_forbidden(self, employee_client, admin_with_password):
        """Test that employees cannot add members to boards."""
        # Arrange - Create a board as admin
        db = TestingSessionLocal()
        admin = db.query(User).filter(User.email == admin_with_password["email"]).first()
        
        board = Board(
            name="Test Board",
            description="Testing auth",
            created_by=admin.id
        )
        db.add(board)
        db.flush()
        
        board_member = BoardMember(
            user_id=admin.id,
            board_id=board.id
        )
        db.add(board_member)
        db.commit()
        board_id = board.id
        
        # Create another user to add
        user = User(
            name="Test User",
            email="testuser@example.com",
            password=get_password_hash("Password123"),
            role=UserRole.EMPLOYEE
        )
        db.add(user)
        db.commit()
        user_id = user.id
        db.close()
        
        # Act - Employee tries to add member
        response = employee_client.post("/api/members", json={
            "user_id": user_id,
            "board_id": board_id
        })
        
        # Assert
        assert response.status_code == 403
    
    def test_add_board_member_user_not_found(self, admin_client):
        """Test that adding non-existent user returns 404."""
        # Arrange - Create a board
        board_data = {"name": "Test Board", "description": "Testing validation"}
        create_response = admin_client.post("/api/boards", json=board_data)
        assert create_response.status_code == 201
        board_id = create_response.json()["id"]
        
        # Act - Try to add non-existent user
        response = admin_client.post("/api/members", json={
            "user_id": 99999,
            "board_id": board_id
        })
        
        # Assert
        assert response.status_code == 404
        assert "user" in response.json()["detail"].lower()
    
    def test_add_board_member_board_not_found(self, admin_client, employee_with_password):
        """Test that adding member to non-existent board returns 404."""
        # Act - Try to add member to non-existent board
        response = admin_client.post("/api/members", json={
            "user_id": employee_with_password["id"],
            "board_id": 99999
        })
        
        # Assert
        assert response.status_code == 404
        assert "board" in response.json()["detail"].lower()
    
    def test_add_board_member_unauthenticated(self, test_client, admin_with_password, employee_with_password):
        """Test that unauthenticated users cannot add members."""
        # Arrange - Create a board
        db = TestingSessionLocal()
        admin = db.query(User).filter(User.email == admin_with_password["email"]).first()
        
        board = Board(
            name="Test Board",
            description="Testing auth",
            created_by=admin.id
        )
        db.add(board)
        db.flush()
        board_id = board.id
        db.commit()
        db.close()
        
        # Act - Unauthenticated request
        response = test_client.post("/api/members", json={
            "user_id": employee_with_password["id"],
            "board_id": board_id
        })
        
        # Assert
        assert response.status_code == 401
    
    def test_add_board_member_invalid_request(self, admin_client):
        """Test that invalid request data returns validation error."""
        # Act - Missing required fields
        response = admin_client.post("/api/members", json={})
        
        # Assert
        assert response.status_code == 422
        
        # Act - Invalid data types
        response = admin_client.post("/api/members", json={
            "user_id": "invalid",
            "board_id": "invalid"
        })
        
        # Assert
        assert response.status_code == 422
    
    def test_add_board_member_multiple_users(self, admin_client, admin_with_password):
        """Test adding multiple users to the same board."""
        # Arrange - Create a board
        board_data = {"name": "Multi-User Board", "description": "Testing multiple additions"}
        create_response = admin_client.post("/api/boards", json=board_data)
        assert create_response.status_code == 201
        board_id = create_response.json()["id"]
        
        # Create multiple users
        db = TestingSessionLocal()
        user_ids = []
        
        for i in range(3):
            user = User(
                name=f"User {i}",
                email=f"user{i}@test.com",
                password=get_password_hash("Password123"),
                role=UserRole.EMPLOYEE
            )
            db.add(user)
            db.flush()
            user_ids.append(user.id)
        
        db.commit()
        db.close()
        
        # Act - Add all users to board
        for user_id in user_ids:
            response = admin_client.post("/api/members", json={
                "user_id": user_id,
                "board_id": board_id
            })
            assert response.status_code == 201
        
        # Assert - All users are members
        members_response = admin_client.get(f"/api/members/{board_id}")
        assert members_response.status_code == 200
        members = members_response.json()
        member_ids = [m["id"] for m in members]
        
        for user_id in user_ids:
            assert user_id in member_ids
    
    def test_add_board_member_admin_to_board(self, admin_client, admin_with_password):
        """Test adding an admin user as a board member."""
        # Arrange - Create a board
        board_data = {"name": "Admin Member Board", "description": "Testing admin as member"}
        create_response = admin_client.post("/api/boards", json=board_data)
        assert create_response.status_code == 201
        board_id = create_response.json()["id"]
        
        # Create another admin user
        db = TestingSessionLocal()
        admin2 = User(
            name="Second Admin",
            email="admin2@test.com",
            password=get_password_hash("Password123"),
            role=UserRole.ADMIN
        )
        db.add(admin2)
        db.commit()
        admin2_id = admin2.id
        db.close()
        
        # Act - Add admin as member
        response = admin_client.post("/api/members", json={
            "user_id": admin2_id,
            "board_id": board_id
        })
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "User successfully added to board"
        
        # Verify admin was added
        members_response = admin_client.get(f"/api/members/{board_id}")
        assert members_response.status_code == 200
        members = members_response.json()
        member_ids = [m["id"] for m in members]
        assert admin2_id in member_ids
    
    def test_add_board_member_response_structure(self, admin_client, admin_with_password, employee_with_password):
        """Test that response has correct structure."""
        # Arrange - Create a board
        board_data = {"name": "Structure Test", "description": "Testing response"}
        create_response = admin_client.post("/api/boards", json=board_data)
        assert create_response.status_code == 201
        board_id = create_response.json()["id"]
        
        # Act
        response = admin_client.post("/api/members", json={
            "user_id": employee_with_password["id"],
            "board_id": board_id
        })
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        
        # Verify required fields
        assert "message" in data
        assert "user_id" in data
        assert "board_id" in data
        
        # Verify data types
        assert isinstance(data["message"], str)
        assert isinstance(data["user_id"], int)
        assert isinstance(data["board_id"], int)
        
        # Verify values
        assert data["user_id"] == employee_with_password["id"]
        assert data["board_id"] == board_id


class TestRemoveBoardMember:
    """Tests for DELETE /api/members endpoint."""

    def test_remove_board_member_success(self, admin_client, admin_with_password, employee_with_password):
        """Test successful removal of board member."""
        # Arrange - Create a board and add employee as member
        board_data = {"name": "Test Board", "description": "Testing member removal"}
        create_response = admin_client.post("/api/boards", json=board_data)
        assert create_response.status_code == 201
        board_id = create_response.json()["id"]

        # Add employee as member
        add_response = admin_client.post("/api/members", json={
            "user_id": employee_with_password["id"],
            "board_id": board_id
        })
        assert add_response.status_code == 201

        # Act - Remove the member
        import json
        response = admin_client.request(
            "DELETE", 
            "/api/members", 
            content=json.dumps({
                "user_id": employee_with_password["id"],
                "board_id": board_id
            }),
            headers={"Content-Type": "application/json"}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User successfully removed from board"
        assert data["user_id"] == employee_with_password["id"]
        assert data["board_id"] == board_id

        # Verify member was removed
        members_response = admin_client.get(f"/api/members/{board_id}")
        assert members_response.status_code == 200
        members = members_response.json()
        member_ids = [m["id"] for m in members]
        assert employee_with_password["id"] not in member_ids

    def test_remove_board_member_not_found(self, admin_client, employee_with_password):
        """Test removing non-existent board member."""
        # Arrange - Create a board
        board_data = {"name": "Test Board", "description": "Testing removal"}
        create_response = admin_client.post("/api/boards", json=board_data)
        assert create_response.status_code == 201
        board_id = create_response.json()["id"]

        # Act - Try to remove member who isn't on the board
        import json
        response = admin_client.request(
            "DELETE", 
            "/api/members", 
            content=json.dumps({
                "user_id": employee_with_password["id"],
                "board_id": board_id
            }),
            headers={"Content-Type": "application/json"}
        )

        # Assert
        assert response.status_code == 404
        assert "not a member" in response.json()["detail"]

    def test_remove_board_member_employee_forbidden(self, employee_client, admin_with_password, employee_with_password):
        """Test that employees cannot remove board members."""
        # Arrange - Create a board as admin
        db = TestingSessionLocal()
        admin = db.query(User).filter(User.email == admin_with_password["email"]).first()
        
        board = Board(
            name="Test Board",
            description="Testing auth",
            created_by=admin.id
        )
        db.add(board)
        db.flush()
        
        # Add both admin and employee as members
        for user_id in [admin.id, employee_with_password["id"]]:
            board_member = BoardMember(
                user_id=user_id,
                board_id=board.id
            )
            db.add(board_member)
        
        db.commit()
        board_id = board.id
        db.close()

        # Act - Employee tries to remove member
        import json
        response = employee_client.request(
            "DELETE", 
            "/api/members", 
            content=json.dumps({
                "user_id": admin_with_password["id"],
                "board_id": board_id
            }),
            headers={"Content-Type": "application/json"}
        )

        # Assert
        assert response.status_code == 403

    def test_remove_board_member_user_not_found(self, admin_client):
        """Test removing member with non-existent user."""
        # Arrange - Create a board
        board_data = {"name": "Test Board", "description": "Testing validation"}
        create_response = admin_client.post("/api/boards", json=board_data)
        assert create_response.status_code == 201
        board_id = create_response.json()["id"]

        # Act - Try to remove non-existent user
        import json
        response = admin_client.request(
            "DELETE", 
            "/api/members", 
            content=json.dumps({
                "user_id": 99999,
                "board_id": board_id
            }),
            headers={"Content-Type": "application/json"}
        )

        # Assert
        assert response.status_code == 404
        assert "User with id 99999 not found" in response.json()["detail"]

    def test_remove_board_member_board_not_found(self, admin_client, employee_with_password):
        """Test removing member from non-existent board."""
        # Act - Try to remove member from non-existent board
        import json
        response = admin_client.request(
            "DELETE", 
            "/api/members", 
            content=json.dumps({
                "user_id": employee_with_password["id"],
                "board_id": 99999
            }),
            headers={"Content-Type": "application/json"}
        )

        # Assert
        assert response.status_code == 404
        assert "Board with id 99999 not found" in response.json()["detail"]