"""
User Pydantic schemas for request/response validation.

These schemas define the structure for user-related API requests and responses,
ensuring data validation and excluding sensitive fields like passwords from responses.
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional
from .company import CompanyResponse


class UserCreate(BaseModel):
    """
    Schema for user registration requests.
    
    Validates:
        - name: Required, non-empty string
        - email: Valid email format
        - password: Required, minimum 8 characters
        - role: User role (admin or employee)
        - company_id: ID of existing company or None for new company
        - company_name: Name for new company (required if company_id is None)
        - company_identifier: Identifier for new company (required if company_id is None)
        - company_description: Optional description for new company
    """
    name: str = Field(..., min_length=1, max_length=100, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, max_length=100, description="User's password (min 8 characters)")
    role: str = Field(..., description="User role: admin or employee")
    
    # Company selection - either existing or new
    company_id: Optional[int] = Field(None, description="ID of existing company")
    company_name: Optional[str] = Field(None, min_length=1, max_length=200, description="Name for new company")
    company_identifier: Optional[str] = Field(None, min_length=1, max_length=50, description="Identifier for new company")
    company_description: Optional[str] = Field(None, max_length=1000, description="Description for new company")


class UserResponse(BaseModel):
    """
    Schema for user data in API responses.
    
    Excludes password field for security (Requirement 3.4).
    Includes all user profile information and company details.
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    email: EmailStr
    avatar: Optional[str] = None
    role: str
    company_id: int
    created_at: datetime
    company: Optional[CompanyResponse] = None


class AddBoardMemberRequest(BaseModel):
    """
    Schema for adding a member to a board.
    
    Validates:
        - user_id: Required, must be a valid user ID
        - board_id: Required, must be a valid board ID
    """
    user_id: int = Field(..., description="ID of the user to add to the board")
    board_id: int = Field(..., description="ID of the board to add the user to")


class RemoveBoardMemberRequest(BaseModel):
    """
    Schema for removing a member from a board.
    
    Validates:
        - user_id: Required, must be a valid user ID
        - board_id: Required, must be a valid board ID
    """
    user_id: int = Field(..., description="ID of the user to remove from the board")
    board_id: int = Field(..., description="ID of the board to remove the user from")
