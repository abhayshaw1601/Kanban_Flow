"""
Authentication and authorization dependencies for FastAPI routes.

This module provides dependency functions for:
- Extracting and validating JWT tokens from cookies
- Getting the current authenticated user
- Verifying admin role for protected endpoints
"""

from typing import Optional
from fastapi import Depends, HTTPException, status, Cookie
from sqlalchemy.orm import Session
from jose import JWTError

from .database import get_db
from .security import decode_token
from ..models.user import User, UserRole


async def get_current_user(
    access_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from the access_token cookie.
    
    Extracts the JWT token from the httpOnly cookie, validates it, and retrieves
    the corresponding user from the database.
    
    Args:
        access_token: JWT access token from httpOnly cookie
        db: Database session dependency
        
    Returns:
        User object for the authenticated user
        
    Raises:
        HTTPException 401: If token is missing, invalid, expired, or user not found
        
    Example:
        @app.get("/api/users/me")
        async def get_profile(current_user: User = Depends(get_current_user)):
            return current_user
            
    Validates: Requirements 29.1, 29.2
    """
    # Check if token is present
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    try:
        # Decode and validate the JWT token
        payload = decode_token(access_token)
        
        # Extract user ID from token payload (JWT sub claim is a string)
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )
        
        # Convert user ID to integer
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: invalid user ID format"
            )
            
        # Verify token type is "access"
        token_type: str = payload.get("type")
        if token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
            
    except JWTError as e:
        # Handle JWT validation errors (expired, invalid signature, etc.)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
    
    # Retrieve user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to verify the current user has admin role.
    
    This dependency chains with get_current_user to first authenticate the user,
    then verify they have admin privileges.
    
    Args:
        current_user: Authenticated user from get_current_user dependency
        
    Returns:
        User object if user is an admin
        
    Raises:
        HTTPException 403: If user is not an admin
        
    Example:
        @app.post("/api/boards")
        async def create_board(
            board_data: BoardCreate,
            admin: User = Depends(get_current_admin)
        ):
            # Only admins can reach this code
            return create_board_logic(board_data, admin)
            
    Validates: Requirements 29.4
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user
