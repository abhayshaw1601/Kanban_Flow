"""
Pydantic schemas for request/response validation.

This module exports all schema classes for use throughout the application.
Schemas ensure data validation and proper serialization/deserialization.
"""

# User schemas
from .user import UserCreate, UserResponse

# Authentication schemas
from .auth import LoginRequest, TokenResponse

# Board schemas
from .board import BoardCreate, BoardResponse, BoardDetail, ColumnWithTasks

# Column schemas
from .column import ColumnResponse

# Task schemas
from .task import TaskCreate, TaskUpdate, TaskMove, TaskResponse

__all__ = [
    # User
    "UserCreate",
    "UserResponse",
    # Auth
    "LoginRequest",
    "TokenResponse",
    # Board
    "BoardCreate",
    "BoardResponse",
    "BoardDetail",
    "ColumnWithTasks",
    # Column
    "ColumnResponse",
    # Task
    "TaskCreate",
    "TaskUpdate",
    "TaskMove",
    "TaskResponse",
]
