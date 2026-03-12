"""
Authentication Pydantic schemas for request/response validation.

These schemas define the structure for authentication-related API requests and responses.
"""
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """
    Schema for user login requests.
    
    Validates:
        - email: Valid email format
        - password: Required string
    """
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class TokenResponse(BaseModel):
    """
    Schema for authentication token responses.
    
    Note: In practice, tokens are set as httpOnly cookies,
    but this schema can be used for API responses if needed.
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
