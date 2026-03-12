"""
Board membership API endpoints.

This module provides endpoints for managing board members,
including listing members and adding new members to boards.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..core.deps import get_current_user, get_current_admin
from ..models.user import User
from ..models.board import Board
from ..models.board_member import BoardMember
from ..schemas.user import UserResponse, AddBoardMemberRequest, RemoveBoardMemberRequest


router = APIRouter(prefix="/api/members", tags=["members"])


@router.get("/{board_id}", response_model=List[UserResponse])
async def get_board_members(
    board_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all members of a specific board.
    
    This endpoint returns a list of all users who are members of the specified board.
    The requesting user must be a member of the board to access this information.
    
    Requirements:
        - 5.2: Return all users associated with the board
        - 24.14: GET /api/members/:boardId endpoint for board members
    
    Args:
        board_id: ID of the board to get members for
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List[UserResponse]: List of board members with user info (id, name, email, avatar, role, created_at)
        
    Raises:
        HTTPException 401: If user is not authenticated (handled by get_current_user)
        HTTPException 403: If user is not a board member
        HTTPException 404: If board does not exist
    """
    # Verify board exists
    board = db.query(Board).filter(Board.id == board_id).first()
    
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Board with id {board_id} not found"
        )
    
    # Verify user is a board member
    is_member = db.query(BoardMember).filter(
        BoardMember.board_id == board_id,
        BoardMember.user_id == current_user.id
    ).first()
    
    if not is_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this board"
        )
    
    # Query all board members
    members = db.query(User).join(
        BoardMember, User.id == BoardMember.user_id
    ).filter(
        BoardMember.board_id == board_id
    ).all()
    
    return [UserResponse.model_validate(member) for member in members]


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_board_member(
    request: AddBoardMemberRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Add a member to a board (admin only).
    
    This endpoint allows administrators to add users to boards, creating a board_members
    relationship. Duplicate member attempts are handled gracefully by returning success
    if the user is already a member.
    
    Requirements:
        - 5.1: Create board_member relationship when admin adds user to board
        - 24.15: POST /api/members endpoint for adding board members (admin only)
    
    Args:
        request: AddBoardMemberRequest containing user_id and board_id
        db: Database session
        current_user: Current authenticated admin user
        
    Returns:
        dict: Success message with member details
        
    Raises:
        HTTPException 401: If user is not authenticated (handled by get_current_admin)
        HTTPException 403: If user is not an admin (handled by get_current_admin)
        HTTPException 404: If user or board does not exist
    """
    # Verify user exists
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {request.user_id} not found"
        )
    
    # Verify board exists
    board = db.query(Board).filter(Board.id == request.board_id).first()
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Board with id {request.board_id} not found"
        )
    
    # Check if user is already a member (handle duplicates gracefully)
    existing_member = db.query(BoardMember).filter(
        BoardMember.user_id == request.user_id,
        BoardMember.board_id == request.board_id
    ).first()
    
    if existing_member:
        # User is already a member, return success
        return {
            "message": "User is already a member of this board",
            "user_id": request.user_id,
            "board_id": request.board_id
        }
    
    # Create new board member relationship
    board_member = BoardMember(
        user_id=request.user_id,
        board_id=request.board_id
    )
    db.add(board_member)
    db.commit()
    
    return {
        "message": "User successfully added to board",
        "user_id": request.user_id,
        "board_id": request.board_id
    }


@router.delete("", status_code=status.HTTP_200_OK)
async def remove_board_member(
    request: RemoveBoardMemberRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Remove a member from a board (admin only).
    
    This endpoint allows administrators to remove users from boards by deleting
    the board_members relationship.
    
    Args:
        request: RemoveBoardMemberRequest containing user_id and board_id
        db: Database session
        current_user: Current authenticated admin user
        
    Returns:
        dict: Success message with member details
        
    Raises:
        HTTPException 401: If user is not authenticated (handled by get_current_admin)
        HTTPException 403: If user is not an admin (handled by get_current_admin)
        HTTPException 404: If user, board, or membership does not exist
    """
    # Verify user exists
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {request.user_id} not found"
        )
    
    # Verify board exists
    board = db.query(Board).filter(Board.id == request.board_id).first()
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Board with id {request.board_id} not found"
        )
    
    # Find the board member relationship
    board_member = db.query(BoardMember).filter(
        BoardMember.user_id == request.user_id,
        BoardMember.board_id == request.board_id
    ).first()
    
    if not board_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not a member of this board"
        )
    
    # Remove the board member relationship
    db.delete(board_member)
    db.commit()
    
    return {
        "message": "User successfully removed from board",
        "user_id": request.user_id,
        "board_id": request.board_id
    }
