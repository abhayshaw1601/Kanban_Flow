from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from ..core.database import Base


class BoardMember(Base):
    """
    BoardMember junction table model for many-to-many relationship between Users and Boards.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to User
        board_id: Foreign key to Board
        
    Relationships:
        user: User associated with this membership (many-to-one)
        board: Board associated with this membership (many-to-one)
        
    Constraints:
        Unique constraint on (user_id, board_id) to prevent duplicate memberships
    """
    __tablename__ = "board_members"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="board_memberships")
    board = relationship("Board", back_populates="members")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'board_id', name='_user_board_uc'),
    )
    
    def __repr__(self):
        return f"<BoardMember(user_id={self.user_id}, board_id={self.board_id})>"
