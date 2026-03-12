from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


class Board(Base):
    """
    Board model representing a Kanban project board.
    
    Attributes:
        id: Primary key
        name: Board name/title
        description: Optional board description
        created_at: Timestamp of board creation
        created_by: Foreign key to User who created the board
        
    Relationships:
        creator: User who created this board (many-to-one)
        columns: Columns belonging to this board (one-to-many)
        members: Board membership records (one-to-many)
    """
    __tablename__ = "boards"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Board information
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Foreign keys
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    creator = relationship("User", back_populates="created_boards")
    columns = relationship("Column", back_populates="board", cascade="all, delete-orphan")
    members = relationship("BoardMember", back_populates="board", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Board(id={self.id}, name='{self.name}')>"
