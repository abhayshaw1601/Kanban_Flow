"""
User management API endpoints.

This module provides endpoints for:
- Getting current user profile
- Listing all users (admin only)
- Deleting user profile
"""

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.deps import get_current_user, get_current_admin
from ..models.user import User
from ..models.task import Task
from ..models.board_member import BoardMember
from ..schemas.user import UserResponse


router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Get the current authenticated user's profile.
    
    Returns the user's profile information including id, name, email, avatar,
    role, and createdAt. Password hash is excluded from the response for security.
    
    Args:
        current_user: Authenticated user from JWT token (dependency)
        db: Database session (dependency)
        
    Returns:
        UserResponse: User profile data without password
        
    Raises:
        HTTPException 401: If user is not authenticated
        
    Example Response:
        {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "avatar": null,
            "role": "admin",
            "created_at": "2024-01-15T10:30:00"
        }
        
    Validates: Requirements 3.1, 24.5
    """
    return UserResponse.model_validate(current_user)


@router.get("", response_model=list[UserResponse])
async def get_all_users(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
) -> list[UserResponse]:
    """
    Get list of all users in the same company (admin only).
    
    Returns all users from the same company as the requesting admin.
    Password hashes are excluded from the response for security.
    Only accessible by admin users.
    
    Args:
        admin: Authenticated admin user (dependency)
        db: Database session (dependency)
        
    Returns:
        list[UserResponse]: List of users from the same company without passwords
        
    Raises:
        HTTPException 401: If user is not authenticated
        HTTPException 403: If user is not an admin
        
    Example Response:
        [
            {
                "id": 1,
                "name": "Admin User",
                "email": "admin@kanbanflow.com",
                "avatar": null,
                "role": "admin",
                "company_id": 1,
                "created_at": "2024-01-15T10:30:00"
            },
            {
                "id": 2,
                "name": "Alice Employee",
                "email": "alice@kanbanflow.com",
                "avatar": null,
                "role": "employee",
                "company_id": 1,
                "created_at": "2024-01-15T11:00:00"
            }
        ]
        
    Validates: Requirements 3.2, 24.6
    """
    # Query users from the same company only
    users = db.query(User).filter(User.company_id == admin.company_id).all()
    
    # Convert to response models (automatically excludes passwords)
    return [UserResponse.model_validate(user) for user in users]


@router.delete("/me")
async def delete_current_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    Delete the current authenticated user's profile.
    
    This endpoint allows users to delete their own profile. When a user is deleted:
    - All tasks assigned to the user are unassigned (assignee_id set to None)
    - User is removed from all board memberships
    - User record is deleted from the database
    - User is automatically logged out (cookies cleared)
    
    Args:
        current_user: Authenticated user from JWT token (dependency)
        db: Database session (dependency)
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException 401: If user is not authenticated
        HTTPException 500: If deletion fails
        
    Example Response:
        {
            "message": "User profile deleted successfully"
        }
    """
    try:
        # Unassign all tasks assigned to this user
        db.query(Task).filter(Task.assignee_id == current_user.id).update(
            {"assignee_id": None}, synchronize_session=False
        )
        
        # Remove user from all board memberships
        db.query(BoardMember).filter(BoardMember.user_id == current_user.id).delete(
            synchronize_session=False
        )
        
        # Delete the user
        db.delete(current_user)
        db.commit()
        
        # Clear authentication cookies
        response = Response(content='{"message": "User profile deleted successfully"}')
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        
        return {"message": "User profile deleted successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to delete user profile"
        )
