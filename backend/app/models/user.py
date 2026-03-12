from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..core.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration for role-based access control."""
    ADMIN = "admin"
    EMPLOYEE = "employee"


class User(Base):
    """
    User model representing system users with authentication and authorization.
    
    Attributes:
        id: Primary key
        name: User's full name
        email: Unique email address for authentication
        password: Bcrypt hashed password (never stored as plaintext)
        avatar: Optional URL to user's avatar image
        role: User role (admin or employee) for authorization
        company_id: Foreign key to the company this user belongs to
        created_at: Timestamp of user account creation
        
    Relationships:
        company: Company this user belongs to (many-to-one)
        created_boards: Boards created by this user (one-to-many)
        board_memberships: Board membership records (one-to-many)
        assigned_tasks: Tasks assigned to this user (one-to-many)
    """
    __tablename__ = "users"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # User information
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)  # bcrypt hashed
    avatar = Column(String, nullable=True)
    
    # Authorization
    role = Column(Enum(UserRole), default=UserRole.EMPLOYEE, nullable=False)
    
    # Company relationship
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships (will be fully defined when related models are created)
    # Using string references for forward declarations
    # These relationships will be properly configured once Board, BoardMember, and Task models are created
    company = relationship("Company", back_populates="users", lazy="select")
    created_boards = relationship("Board", back_populates="creator", lazy="select")
    board_memberships = relationship("BoardMember", back_populates="user", lazy="select")
    assigned_tasks = relationship("Task", back_populates="assignee", lazy="select")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role.value}')>"
