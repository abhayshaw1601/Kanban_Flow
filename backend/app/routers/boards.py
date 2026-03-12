"""
Board management API endpoints.

This module provides endpoints for creating and managing Kanban boards,
including board creation with automatic column setup and member management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..core.deps import get_current_user, get_current_admin
from ..models.user import User
from ..models.board import Board
from ..models.column import Column
from ..models.board_member import BoardMember
from ..schemas.board import BoardCreate, BoardResponse, BoardDetail, BoardUpdate


router = APIRouter(prefix="/api/boards", tags=["boards"])


@router.get("", response_model=List[BoardResponse])
async def get_user_boards(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all boards where the current user is a member.
    
    This endpoint returns a list of boards that the authenticated user has access to
    through board membership. Only boards where the user is explicitly a board member
    are returned.
    
    Requirements:
        - 4.2: Return only boards where user is a Board_Member
        - 24.7: GET /api/boards endpoint for user's boards
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List[BoardResponse]: List of boards with basic info (id, name, description, created_at, created_by)
        
    Raises:
        HTTPException 401: If user is not authenticated (handled by get_current_user)
    """
    # Query boards where user is a member
    # Join Board with BoardMember to filter by user_id
    boards = db.query(Board).join(
        BoardMember, Board.id == BoardMember.board_id
    ).filter(
        BoardMember.user_id == current_user.id
    ).all()
    
    return boards


@router.post("", response_model=BoardResponse, status_code=status.HTTP_201_CREATED)
async def create_board(
    board_data: BoardCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Create a new board (admin only).
    
    This endpoint:
    1. Creates a new board with the provided name and description
    2. Automatically creates 3 default columns: "To-Do", "In Progress", "Done"
    3. Adds the creator as a board member
    4. Returns the created board
    
    Requirements:
        - 4.1: Admin creates board with name, description, created_by, created_at
        - 6.1: Automatically create default columns
        - 24.8: POST /api/boards endpoint
    
    Args:
        board_data: Board creation data (name, description)
        db: Database session
        admin: Current authenticated admin user
        
    Returns:
        BoardResponse: Created board with id, name, description, created_at, created_by
        
    Raises:
        HTTPException 403: If user is not an admin (handled by get_current_admin)
    """
    # Create the board
    new_board = Board(
        name=board_data.name,
        description=board_data.description,
        created_by=admin.id
    )
    
    db.add(new_board)
    db.flush()  # Flush to get the board ID without committing
    
    # Create default columns: To-Do, In Progress, Done
    default_columns = [
        Column(name="To-Do", order=0, board_id=new_board.id),
        Column(name="In Progress", order=1, board_id=new_board.id),
        Column(name="Done", order=2, board_id=new_board.id)
    ]
    
    for column in default_columns:
        db.add(column)
    
    # Add creator as board member
    board_member = BoardMember(
        user_id=admin.id,
        board_id=new_board.id
    )
    db.add(board_member)
    
    # Commit all changes
    db.commit()
    db.refresh(new_board)
    
    return new_board


@router.get("/{board_id}", response_model=BoardDetail)
async def get_board_detail(
    board_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed board information with columns, tasks, and members.
    
    This endpoint returns complete board information including:
    - All columns (ordered by order field)
    - All tasks within each column (ordered by order field)
    - Assignee information for each task
    - All board members
    
    Requirements:
        - 4.3: Return board with all columns, tasks, and assignees if user is Board_Member
        - 4.4: Reject request if user is not a board member
        - 24.9: GET /api/boards/:id endpoint for board details
    
    Args:
        board_id: ID of the board to retrieve
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        BoardDetail: Complete board information with columns, tasks, and members
        
    Raises:
        HTTPException 401: If user is not authenticated (handled by get_current_user)
        HTTPException 403: If user is not a board member
        HTTPException 404: If board does not exist
    """
    # Query the board
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
    
    # Query columns with tasks (ordered)
    from sqlalchemy.orm import joinedload
    from ..models.task import Task
    
    columns = db.query(Column).filter(
        Column.board_id == board_id
    ).order_by(Column.order).all()
    
    # Build response with columns and tasks
    columns_with_tasks = []
    for column in columns:
        # Query tasks for this column, ordered by order field
        tasks = db.query(Task).filter(
            Task.column_id == column.id
        ).order_by(Task.order).all()
        
        # Convert column to dict and add tasks
        column_dict = {
            "id": column.id,
            "name": column.name,
            "order": column.order,
            "board_id": column.board_id,
            "tasks": tasks
        }
        columns_with_tasks.append(column_dict)
    
    # Query board members
    from ..models.user import User as UserModel
    members = db.query(UserModel).join(
        BoardMember, UserModel.id == BoardMember.user_id
    ).filter(
        BoardMember.board_id == board_id
    ).all()
    
    # Build response
    board_detail = {
        "id": board.id,
        "name": board.name,
        "description": board.description,
        "created_at": board.created_at,
        "created_by": board.created_by,
        "columns": columns_with_tasks,
        "members": members
    }
    
    return board_detail


@router.patch("/{board_id}", response_model=BoardResponse)
async def update_board(
    board_id: int,
    board_data: BoardUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Update board information (admin only).
    
    This endpoint allows administrators to update board name and description.
    
    Args:
        board_id: ID of the board to update
        board_data: Board update data (name, description)
        db: Database session
        admin: Current authenticated admin user
        
    Returns:
        BoardResponse: Updated board information
        
    Raises:
        HTTPException 401: If user is not authenticated (handled by get_current_admin)
        HTTPException 403: If user is not an admin (handled by get_current_admin)
        HTTPException 404: If board does not exist
    """
    # Query the board
    board = db.query(Board).filter(Board.id == board_id).first()
    
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Board with id {board_id} not found"
        )
    
    # Update board fields
    if board_data.name is not None:
        board.name = board_data.name
    if board_data.description is not None:
        board.description = board_data.description
    
    db.commit()
    db.refresh(board)
    
    return board


@router.delete("/{board_id}", status_code=status.HTTP_200_OK)
async def delete_board(
    board_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Delete a board (admin only).
    
    This endpoint allows administrators to delete boards. All associated
    columns, tasks, and board memberships are automatically deleted due
    to foreign key constraints.
    
    Args:
        board_id: ID of the board to delete
        db: Database session
        admin: Current authenticated admin user
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException 401: If user is not authenticated (handled by get_current_admin)
        HTTPException 403: If user is not an admin (handled by get_current_admin)
        HTTPException 404: If board does not exist
    """
    # Query the board
    board = db.query(Board).filter(Board.id == board_id).first()
    
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Board with id {board_id} not found"
        )
    
    # Delete the board (cascading deletes will handle related records)
    db.delete(board)
    db.commit()
    
    return {
        "message": "Board successfully deleted",
        "board_id": board_id
    }
