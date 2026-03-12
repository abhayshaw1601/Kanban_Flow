"""
Unit tests for User model.

Tests basic User model functionality including:
- Model structure and attributes
- UserRole enum values
- Field constraints

Note: These tests verify the model structure without instantiating User objects
because the relationships reference models (Board, BoardMember, Task) that don't exist yet.
Full integration tests will be added after all models are implemented.
"""
import pytest
from app.models.user import User, UserRole
from sqlalchemy import inspect


def test_user_role_enum_values():
    """Test that UserRole enum has correct values."""
    assert UserRole.ADMIN.value == "admin"
    assert UserRole.EMPLOYEE.value == "employee"
    assert len(list(UserRole)) == 2


def test_user_table_name():
    """Test that User model has correct table name."""
    assert User.__tablename__ == "users"


def test_user_columns_exist():
    """Test that User model has all required columns."""
    # Get the table columns
    columns = {col.name for col in User.__table__.columns}
    
    # Verify all required columns exist
    required_columns = {'id', 'name', 'email', 'password', 'avatar', 'role', 'created_at'}
    assert required_columns.issubset(columns), f"Missing columns: {required_columns - columns}"


def test_user_column_types():
    """Test that User model columns have correct types."""
    columns = {col.name: col.type.__class__.__name__ for col in User.__table__.columns}
    
    assert 'Integer' in columns['id']
    assert 'String' in columns['name'] or 'VARCHAR' in columns['name']
    assert 'String' in columns['email'] or 'VARCHAR' in columns['email']
    assert 'String' in columns['password'] or 'VARCHAR' in columns['password']
    assert 'Enum' in columns['role']


def test_user_column_constraints():
    """Test that User model columns have correct constraints."""
    # Check primary key
    pk_columns = [col.name for col in User.__table__.primary_key.columns]
    assert 'id' in pk_columns
    
    # Check nullable constraints
    columns_dict = {col.name: col for col in User.__table__.columns}
    assert columns_dict['name'].nullable == False
    assert columns_dict['email'].nullable == False
    assert columns_dict['password'].nullable == False
    assert columns_dict['avatar'].nullable == True
    assert columns_dict['role'].nullable == False
    assert columns_dict['created_at'].nullable == False


def test_user_email_unique_constraint():
    """Test that email column has unique constraint."""
    email_column = User.__table__.columns['email']
    assert email_column.unique == True


def test_user_relationships_defined():
    """Test that User model has required relationships defined."""
    # Check that relationship attributes are defined on the class
    # We can't inspect them yet because the related models don't exist
    # but we can verify the attributes are present
    assert hasattr(User, 'created_boards'), "User model should have 'created_boards' relationship"
    assert hasattr(User, 'board_memberships'), "User model should have 'board_memberships' relationship"
    assert hasattr(User, 'assigned_tasks'), "User model should have 'assigned_tasks' relationship"


def test_user_role_default():
    """Test that role column has default value."""
    role_column = User.__table__.columns['role']
    assert role_column.default is not None


def test_user_created_at_default():
    """Test that created_at column has default value."""
    created_at_column = User.__table__.columns['created_at']
    assert created_at_column.default is not None


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
