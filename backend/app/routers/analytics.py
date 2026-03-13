"""
Analytics API endpoints for member performance tracking.

This module provides endpoints for analyzing member task completion statistics
and performance metrics across boards.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import Dict, Any

from ..core.database import get_db
from ..core.deps import get_current_admin
from ..models.user import User
from ..models.task import Task
from ..models.column import Column
from ..models.board import Board
from ..models.board_member import BoardMember

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/member/{user_id}/stats")
async def get_member_statistics(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Get task completion statistics for a specific member (admin only).
    
    Returns task counts by status (todo, in progress, done) and performance metrics.
    Performance is calculated based on completion percentage:
    - Green: >50% tasks completed
    - Yellow: 30-50% tasks completed  
    - Red: <30% tasks completed
    
    Args:
        user_id: ID of the user to get statistics for
        db: Database session
        admin: Current authenticated admin user
        
    Returns:
        Dict containing task statistics and performance indicators
        
    Raises:
        HTTPException 403: If user is not an admin
        HTTPException 404: If user not found
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    # Get task statistics by column type
    # We'll categorize columns by name patterns:
    # - "To Do", "Todo", "Backlog" -> todo
    # - "In Progress", "Doing", "Development" -> in_progress  
    # - "Done", "Complete", "Finished" -> done
    
    task_stats = db.query(
        func.count(Task.id).label('total_tasks'),
        func.sum(
            case(
                (func.lower(Column.name).in_(['to do', 'todo', 'backlog', 'to-do']), 1),
                else_=0
            )
        ).label('todo_count'),
        func.sum(
            case(
                (func.lower(Column.name).in_(['in progress', 'doing', 'development', 'in-progress']), 1),
                else_=0
            )
        ).label('in_progress_count'),
        func.sum(
            case(
                (func.lower(Column.name).in_(['done', 'complete', 'finished', 'completed']), 1),
                else_=0
            )
        ).label('done_count')
    ).join(
        Column, Task.column_id == Column.id
    ).filter(
        Task.assignee_id == user_id
    ).first()
    
    # Handle case where user has no tasks
    total_tasks = task_stats.total_tasks or 0
    todo_count = task_stats.todo_count or 0
    in_progress_count = task_stats.in_progress_count or 0
    done_count = task_stats.done_count or 0
    
    # Calculate completion percentage
    completion_percentage = (done_count / total_tasks * 100) if total_tasks > 0 else 0
    
    # Determine performance status
    if completion_percentage > 50:
        performance_status = "excellent"
        performance_color = "green"
    elif completion_percentage >= 30:
        performance_status = "good"
        performance_color = "yellow"
    else:
        performance_status = "needs_improvement"
        performance_color = "red"
    
    # Get board-wise breakdown
    board_stats = db.query(
        Board.id,
        Board.name,
        func.count(Task.id).label('task_count'),
        func.sum(
            case(
                (func.lower(Column.name).in_(['done', 'complete', 'finished', 'completed']), 1),
                else_=0
            )
        ).label('completed_tasks')
    ).join(
        Column, Board.id == Column.board_id
    ).join(
        Task, Column.id == Task.column_id
    ).filter(
        Task.assignee_id == user_id
    ).group_by(
        Board.id, Board.name
    ).all()
    
    board_breakdown = []
    for board_stat in board_stats:
        board_completion = (board_stat.completed_tasks or 0) / board_stat.task_count * 100 if board_stat.task_count > 0 else 0
        board_breakdown.append({
            "board_id": board_stat.id,
            "board_name": board_stat.name,
            "total_tasks": board_stat.task_count,
            "completed_tasks": board_stat.completed_tasks or 0,
            "completion_percentage": round(board_completion, 1)
        })
    
    return {
        "user_id": user_id,
        "user_name": user.name,
        "user_email": user.email,
        "statistics": {
            "total_tasks": total_tasks,
            "todo_tasks": todo_count,
            "in_progress_tasks": in_progress_count,
            "done_tasks": done_count,
            "completion_percentage": round(completion_percentage, 1)
        },
        "performance": {
            "status": performance_status,
            "color": performance_color,
            "description": f"{completion_percentage:.1f}% completion rate"
        },
        "board_breakdown": board_breakdown
    }


@router.get("/team/overview")
async def get_team_overview(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Get overview statistics for all team members (admin only).
    
    Returns a summary of all users with their basic performance metrics.
    
    Args:
        db: Database session
        admin: Current authenticated admin user
        
    Returns:
        List of users with basic performance indicators
        
    Raises:
        HTTPException 403: If user is not an admin
    """
    # Get all users with their task completion stats
    users_stats = db.query(
        User.id,
        User.name,
        User.email,
        User.role,
        func.count(Task.id).label('total_tasks'),
        func.sum(
            case(
                (func.lower(Column.name).in_(['done', 'complete', 'finished', 'completed']), 1),
                else_=0
            )
        ).label('done_count')
    ).outerjoin(
        Task, User.id == Task.assignee_id
    ).outerjoin(
        Column, Task.column_id == Column.id
    ).group_by(
        User.id, User.name, User.email, User.role
    ).all()
    
    team_overview = []
    for user_stat in users_stats:
        total_tasks = user_stat.total_tasks or 0
        done_count = user_stat.done_count or 0
        completion_percentage = (done_count / total_tasks * 100) if total_tasks > 0 else 0
        
        # Determine performance color
        if completion_percentage > 50:
            performance_color = "green"
        elif completion_percentage >= 30:
            performance_color = "yellow"
        else:
            performance_color = "red"
        
        team_overview.append({
            "user_id": user_stat.id,
            "name": user_stat.name,
            "email": user_stat.email,
            "role": user_stat.role,
            "total_tasks": total_tasks,
            "completed_tasks": done_count,
            "completion_percentage": round(completion_percentage, 1),
            "performance_color": performance_color
        })
    
    return {
        "team_members": team_overview,
        "total_members": len(team_overview)
    }