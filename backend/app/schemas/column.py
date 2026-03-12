"""
Column Pydantic schemas for request/response validation.

These schemas define the structure for column-related API responses.
"""
from pydantic import BaseModel, Field, ConfigDict


class ColumnResponse(BaseModel):
    """
    Schema for column data in API responses.
    
    Represents a vertical section of a Kanban board (e.g., "To-Do", "In Progress", "Done").
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str = Field(..., description="Column name")
    order: int = Field(..., description="Display order of the column (0-indexed)")
    board_id: int = Field(..., description="ID of the board this column belongs to")
