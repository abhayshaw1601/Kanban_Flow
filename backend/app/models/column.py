from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..core.database import Base


class Column(Base):
    """
    Column model representing a vertical section of a Kanban board.
    
    Attributes:
        id: Primary key
        name: Column name (e.g., "To-Do", "In Progress", "Done")
        order: Integer defining the display order of columns (0-indexed)
        board_id: Foreign key to the Board this column belongs to
        
    Relationships:
        board: Board this column belongs to (many-to-one)
        tasks: Tasks in this column (one-to-many)
    """
    __tablename__ = "columns"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Column information
    name = Column(String, nullable=False)
    order = Column(Integer, nullable=False)
    
    # Foreign keys
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=False)
    
    # Relationships
    board = relationship("Board", back_populates="columns")
    tasks = relationship("Task", back_populates="column", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Column(id={self.id}, name='{self.name}', order={self.order})>"
