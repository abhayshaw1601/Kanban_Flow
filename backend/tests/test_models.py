"""
Unit tests for Board, BoardMember, Column, and Task models.

Tests model structure, attributes, relationships, and constraints.
"""
import pytest
from app.models import Board, BoardMember, Column, Task, TaskPriority


class TestBoardModel:
    """Tests for Board model."""
    
    def test_board_table_name(self):
        """Test that Board model has correct table name."""
        assert Board.__tablename__ == "boards"
    
    def test_board_columns_exist(self):
        """Test that Board model has all required columns."""
        columns = {col.name for col in Board.__table__.columns}
        required_columns = {'id', 'name', 'description', 'created_at', 'created_by'}
        assert required_columns.issubset(columns), f"Missing columns: {required_columns - columns}"
    
    def test_board_column_constraints(self):
        """Test that Board model columns have correct constraints."""
        columns_dict = {col.name: col for col in Board.__table__.columns}
        
        # Check primary key
        pk_columns = [col.name for col in Board.__table__.primary_key.columns]
        assert 'id' in pk_columns
        
        # Check nullable constraints
        assert columns_dict['name'].nullable == False
        assert columns_dict['description'].nullable == True
        assert columns_dict['created_at'].nullable == False
        assert columns_dict['created_by'].nullable == False
    
    def test_board_foreign_keys(self):
        """Test that Board model has correct foreign keys."""
        fk_columns = {fk.parent.name: fk.column.table.name for fk in Board.__table__.foreign_keys}
        assert 'created_by' in fk_columns
        assert fk_columns['created_by'] == 'users'
    
    def test_board_relationships_defined(self):
        """Test that Board model has required relationships."""
        assert hasattr(Board, 'creator'), "Board should have 'creator' relationship"
        assert hasattr(Board, 'columns'), "Board should have 'columns' relationship"
        assert hasattr(Board, 'members'), "Board should have 'members' relationship"
    
    def test_board_created_at_default(self):
        """Test that created_at column has default value."""
        created_at_column = Board.__table__.columns['created_at']
        assert created_at_column.default is not None


class TestBoardMemberModel:
    """Tests for BoardMember model."""
    
    def test_board_member_table_name(self):
        """Test that BoardMember model has correct table name."""
        assert BoardMember.__tablename__ == "board_members"
    
    def test_board_member_columns_exist(self):
        """Test that BoardMember model has all required columns."""
        columns = {col.name for col in BoardMember.__table__.columns}
        required_columns = {'id', 'user_id', 'board_id'}
        assert required_columns.issubset(columns), f"Missing columns: {required_columns - columns}"
    
    def test_board_member_column_constraints(self):
        """Test that BoardMember model columns have correct constraints."""
        columns_dict = {col.name: col for col in BoardMember.__table__.columns}
        
        # Check primary key
        pk_columns = [col.name for col in BoardMember.__table__.primary_key.columns]
        assert 'id' in pk_columns
        
        # Check nullable constraints
        assert columns_dict['user_id'].nullable == False
        assert columns_dict['board_id'].nullable == False
    
    def test_board_member_foreign_keys(self):
        """Test that BoardMember model has correct foreign keys."""
        fk_columns = {fk.parent.name: fk.column.table.name for fk in BoardMember.__table__.foreign_keys}
        assert 'user_id' in fk_columns
        assert 'board_id' in fk_columns
        assert fk_columns['user_id'] == 'users'
        assert fk_columns['board_id'] == 'boards'
    
    def test_board_member_unique_constraint(self):
        """Test that BoardMember has unique constraint on user_id and board_id."""
        # Check for unique constraint
        unique_constraints = [c for c in BoardMember.__table__.constraints 
                            if hasattr(c, 'columns') and len(c.columns) > 1]
        assert len(unique_constraints) > 0, "BoardMember should have a unique constraint"
        
        # Verify the constraint includes both user_id and board_id
        constraint_columns = {col.name for c in unique_constraints for col in c.columns}
        assert 'user_id' in constraint_columns
        assert 'board_id' in constraint_columns
    
    def test_board_member_relationships_defined(self):
        """Test that BoardMember model has required relationships."""
        assert hasattr(BoardMember, 'user'), "BoardMember should have 'user' relationship"
        assert hasattr(BoardMember, 'board'), "BoardMember should have 'board' relationship"


class TestColumnModel:
    """Tests for Column model."""
    
    def test_column_table_name(self):
        """Test that Column model has correct table name."""
        assert Column.__tablename__ == "columns"
    
    def test_column_columns_exist(self):
        """Test that Column model has all required columns."""
        columns = {col.name for col in Column.__table__.columns}
        required_columns = {'id', 'name', 'order', 'board_id'}
        assert required_columns.issubset(columns), f"Missing columns: {required_columns - columns}"
    
    def test_column_column_constraints(self):
        """Test that Column model columns have correct constraints."""
        columns_dict = {col.name: col for col in Column.__table__.columns}
        
        # Check primary key
        pk_columns = [col.name for col in Column.__table__.primary_key.columns]
        assert 'id' in pk_columns
        
        # Check nullable constraints
        assert columns_dict['name'].nullable == False
        assert columns_dict['order'].nullable == False
        assert columns_dict['board_id'].nullable == False
    
    def test_column_foreign_keys(self):
        """Test that Column model has correct foreign keys."""
        fk_columns = {fk.parent.name: fk.column.table.name for fk in Column.__table__.foreign_keys}
        assert 'board_id' in fk_columns
        assert fk_columns['board_id'] == 'boards'
    
    def test_column_relationships_defined(self):
        """Test that Column model has required relationships."""
        assert hasattr(Column, 'board'), "Column should have 'board' relationship"
        assert hasattr(Column, 'tasks'), "Column should have 'tasks' relationship"


class TestTaskModel:
    """Tests for Task model."""
    
    def test_task_priority_enum_values(self):
        """Test that TaskPriority enum has correct values."""
        assert TaskPriority.LOW.value == "low"
        assert TaskPriority.MEDIUM.value == "medium"
        assert TaskPriority.HIGH.value == "high"
        assert len(list(TaskPriority)) == 3
    
    def test_task_table_name(self):
        """Test that Task model has correct table name."""
        assert Task.__tablename__ == "tasks"
    
    def test_task_columns_exist(self):
        """Test that Task model has all required columns."""
        columns = {col.name for col in Task.__table__.columns}
        required_columns = {
            'id', 'title', 'description', 'due_date', 'priority', 
            'order', 'column_id', 'assignee_id', 'created_at', 'updated_at'
        }
        assert required_columns.issubset(columns), f"Missing columns: {required_columns - columns}"
    
    def test_task_column_types(self):
        """Test that Task model columns have correct types."""
        columns = {col.name: col.type.__class__.__name__ for col in Task.__table__.columns}
        
        assert 'Integer' in columns['id']
        assert 'String' in columns['title'] or 'VARCHAR' in columns['title']
        assert 'Text' in columns['description'] or 'TEXT' in columns['description']
        assert 'Enum' in columns['priority']
    
    def test_task_column_constraints(self):
        """Test that Task model columns have correct constraints."""
        columns_dict = {col.name: col for col in Task.__table__.columns}
        
        # Check primary key
        pk_columns = [col.name for col in Task.__table__.primary_key.columns]
        assert 'id' in pk_columns
        
        # Check nullable constraints
        assert columns_dict['title'].nullable == False
        assert columns_dict['description'].nullable == True
        assert columns_dict['due_date'].nullable == True
        assert columns_dict['priority'].nullable == False
        assert columns_dict['order'].nullable == False
        assert columns_dict['column_id'].nullable == False
        assert columns_dict['assignee_id'].nullable == True
        assert columns_dict['created_at'].nullable == False
        assert columns_dict['updated_at'].nullable == False
    
    def test_task_foreign_keys(self):
        """Test that Task model has correct foreign keys."""
        fk_columns = {fk.parent.name: fk.column.table.name for fk in Task.__table__.foreign_keys}
        assert 'column_id' in fk_columns
        assert 'assignee_id' in fk_columns
        assert fk_columns['column_id'] == 'columns'
        assert fk_columns['assignee_id'] == 'users'
    
    def test_task_relationships_defined(self):
        """Test that Task model has required relationships."""
        assert hasattr(Task, 'column'), "Task should have 'column' relationship"
        assert hasattr(Task, 'assignee'), "Task should have 'assignee' relationship"
    
    def test_task_priority_default(self):
        """Test that priority column has default value."""
        priority_column = Task.__table__.columns['priority']
        assert priority_column.default is not None
    
    def test_task_timestamps_default(self):
        """Test that timestamp columns have default values."""
        created_at_column = Task.__table__.columns['created_at']
        updated_at_column = Task.__table__.columns['updated_at']
        assert created_at_column.default is not None
        assert updated_at_column.default is not None
        assert updated_at_column.onupdate is not None


class TestCascadeDeleteRules:
    """Tests for cascade delete rules on relationships."""
    
    def test_board_columns_cascade_delete(self):
        """Test that Board.columns relationship has cascade delete."""
        # Get the relationship property
        board_columns_rel = Board.columns.property
        assert 'delete-orphan' in board_columns_rel.cascade
        assert 'all' in board_columns_rel.cascade or 'delete' in board_columns_rel.cascade
    
    def test_board_members_cascade_delete(self):
        """Test that Board.members relationship has cascade delete."""
        board_members_rel = Board.members.property
        assert 'delete-orphan' in board_members_rel.cascade
        assert 'all' in board_members_rel.cascade or 'delete' in board_members_rel.cascade
    
    def test_column_tasks_cascade_delete(self):
        """Test that Column.tasks relationship has cascade delete."""
        column_tasks_rel = Column.tasks.property
        assert 'delete-orphan' in column_tasks_rel.cascade
        assert 'all' in column_tasks_rel.cascade or 'delete' in column_tasks_rel.cascade


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
