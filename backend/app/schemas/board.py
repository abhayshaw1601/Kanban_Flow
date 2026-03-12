"""
Board Pydantic schemas for request/response validation.

These schemas define the structure for board-related API requests and responses,
including basic board info and detailed board views with columns and tasks.
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List
from .column import ColumnResponse
from .task import TaskResponse
from .user import UserResponse


class BoardCreate(BaseModel):
    """
    Schema for board creation requests.
    
    Validates:
        - name: Required, non-empty string
        - description: Optional string
    """
    name: str = Field(..., min_length=1, max_length=200, description="Board name")
    description: Optional[str] = Field(None, max_length=1000, description="Board description")


class BoardUpdate(BaseModel):
    """
    Schema for board update requests.
    
    Validates:
        - name: Optional, non-empty string
        - description: Optional string
    """
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Board name")
    description: Optional[str] = Field(None, max_length=1000, description="Board description")


class BoardResponse(BaseModel):
    """
    Schema for basic board data in API responses.
    
    Used for board lists and simple board information.
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    created_by: int


class ColumnWithTasks(ColumnResponse):
    """
    Extended column schema that includes tasks.
    
    Used in BoardDetail to show complete board structure.
    """
    tasks: List[TaskResponse] = Field(default_factory=list, description="Tasks in this column")


class BoardDetail(BaseModel):
    """
    Schema for detailed board data in API responses.
    
    Includes complete board information with all columns, tasks, and assignee details.
    Used when viewing a specific board (Requirement 4.3).
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    created_by: int
    columns: List[ColumnWithTasks] = Field(default_factory=list, description="Columns with their tasks")
    members: List[UserResponse] = Field(default_factory=list, description="Board members")
