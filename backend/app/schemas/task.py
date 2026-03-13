"""
Task Pydantic schemas for request/response validation.

These schemas define the structure for task-related API requests and responses,
including task creation, updates, and movement operations.
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class TaskCreate(BaseModel):
    """
    Schema for task creation requests.
    
    Validates:
        - title: Required, non-empty string
        - description: Optional markdown content
        - due_date: Optional datetime
        - priority: Must be "low", "medium", or "high" (Requirement 7.5)
        - column_id: Required, references existing column
        - assignee_id: Optional, must reference existing user if provided (Requirement 8.2)
    """
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, description="Task description (supports Markdown)")
    due_date: Optional[datetime] = Field(None, description="Task due date")
    priority: str = Field(default="medium", pattern="^(low|medium|high)$", description="Task priority level")
    column_id: int = Field(..., description="ID of the column this task belongs to")
    assignee_id: Optional[int] = Field(None, description="ID of the user assigned to this task")


class TaskUpdate(BaseModel):
    """
    Schema for task update requests.
    
    All fields are optional to allow partial updates.
    Validates priority if provided (Requirement 7.5).
    Validates assignee_id if provided (Requirement 8.2).
    
    Includes column_id and order for employees to update task status (Requirement 24.11).
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, description="Task description (supports Markdown)")
    due_date: Optional[datetime] = Field(None, description="Task due date")
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$", description="Task priority level")
    assignee_id: Optional[int] = Field(None, description="ID of the user assigned to this task")
    column_id: Optional[int] = Field(None, description="ID of the column (status-related field)")
    order: Optional[int] = Field(None, ge=0, description="Order position within column (status-related field)")


class TaskMove(BaseModel):
    """
    Schema for task movement requests (drag-and-drop operations).
    
    Used when moving tasks between columns or reordering within a column.
    """
    column_id: int = Field(..., description="ID of the destination column")
    order: int = Field(..., ge=0, description="New order position within the column (0-indexed)")


class TaskResponse(BaseModel):
    """
    Schema for task data in API responses.
    
    Includes all task information with timestamps and blocker status.
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: str
    is_blocker: bool = False
    blocker_reason: Optional[str] = None
    order: int
    column_id: int
    assignee_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
