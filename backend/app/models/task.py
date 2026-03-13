from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..core.database import Base


class TaskPriority(str, enum.Enum):
    """Task priority enumeration for task urgency levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Task(Base):
    """
    Task model representing a work item on a Kanban board.
    
    Attributes:
        id: Primary key
        title: Task title/summary
        description: Optional detailed description (supports Markdown)
        due_date: Optional due date for the task
        priority: Task priority level (low, medium, high)
        is_blocker: Boolean flag indicating if task is marked as a blocker
        blocker_reason: Optional reason why task is marked as blocker
        order: Integer defining the display order within a column (0-indexed)
        column_id: Foreign key to the Column this task belongs to
        assignee_id: Optional foreign key to User assigned to this task
        created_at: Timestamp of task creation
        updated_at: Timestamp of last task update
        
    Relationships:
        column: Column this task belongs to (many-to-one)
        assignee: User assigned to this task (many-to-one, optional)
    """
    __tablename__ = "tasks"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Task information
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)  # Markdown content
    due_date = Column(DateTime, nullable=True)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    is_blocker = Column(Boolean, default=False, nullable=False)
    blocker_reason = Column(String, nullable=True)
    order = Column(Integer, nullable=False)
    
    # Foreign keys
    column_id = Column(Integer, ForeignKey("columns.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    column = relationship("Column", back_populates="tasks")
    assignee = relationship("User", back_populates="assigned_tasks")
    
    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', priority='{self.priority.value}', is_blocker={self.is_blocker})>"
