"""
Analytics API endpoints for member performance tracking and audit functionality.

This module provides endpoints for analyzing member task completion statistics,
performance metrics across boards, and audit functionality for overdue tasks.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_
from typing import Dict, Any, List
from datetime import datetime

from ..core.database import get_db
from ..core.deps import get_current_admin, get_current_user
from ..models.user import User
from ..models.task import Task
from ..models.column import Column
from ..models.board import Board
from ..models.board_member import BoardMember
from ..services.audit_service import AuditService

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


@router.post("/audit/run")
async def run_audit(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Run audit to check for overdue tasks and mark them as blockers (admin only).
    
    This endpoint:
    1. Finds all tasks with due dates within 3 days or overdue
    2. Excludes tasks in "done" columns
    3. Marks them as blockers with appropriate reasons
    4. Returns audit results and statistics
    
    Args:
        db: Database session
        admin: Current authenticated admin user
        
    Returns:
        Dict containing audit results and statistics
        
    Raises:
        HTTPException 403: If user is not an admin
    """
    audit_service = AuditService(db)
    results = audit_service.run_audit()
    
    return {
        "success": True,
        "message": f"Audit completed. Marked {results['tasks_marked_as_blockers']} tasks as blockers.",
        "results": results
    }


@router.get("/audit/pending-projects")
async def get_pending_projects(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Get all pending projects (tasks not in done columns) (admin only).
    
    Returns detailed information about all pending tasks including
    due dates, assignees, and blocker status.
    
    Args:
        db: Database session
        admin: Current authenticated admin user
        
    Returns:
        List of pending projects with details
        
    Raises:
        HTTPException 403: If user is not an admin
    """
    audit_service = AuditService(db)
    pending_projects = audit_service.get_pending_projects()
    
    return {
        "pending_projects": pending_projects,
        "total_pending": len(pending_projects)
    }


@router.post("/audit/clear-blockers")
async def clear_all_blockers(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Clear all blocker flags from tasks (admin only).
    
    Removes blocker status from all tasks. Useful for resetting
    the audit state or clearing false positives.
    
    Args:
        db: Database session
        admin: Current authenticated admin user
        
    Returns:
        Dict containing number of tasks cleared
        
    Raises:
        HTTPException 403: If user is not an admin
    """
    audit_service = AuditService(db)
    cleared_count = audit_service.clear_all_blockers()
    
    return {
        "success": True,
        "message": f"Cleared blocker status from {cleared_count} tasks.",
        "tasks_cleared": cleared_count
    }


@router.get("/user/{user_id}/blocked-tasks")
async def get_user_blocked_tasks(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get blocked tasks for a specific user.
    
    Users can only access their own blocked tasks unless they are admin.
    
    Args:
        user_id: ID of the user to get blocked tasks for
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Dict containing blocked tasks for the user
        
    Raises:
        HTTPException 403: If user tries to access another user's tasks (non-admin)
        HTTPException 404: If user not found
    """
    # Check permissions - users can only see their own blocked tasks, admins can see any
    if current_user.role != 'admin' and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own blocked tasks"
        )
    
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    # Get blocked tasks for the user
    blocked_tasks = db.query(Task).join(
        Column, Task.column_id == Column.id
    ).join(
        Board, Column.board_id == Board.id
    ).filter(
        and_(
            Task.assignee_id == user_id,
            Task.is_blocker == True
        )
    ).all()
    
    # Format blocked tasks
    blocked_tasks_data = []
    for task in blocked_tasks:
        days_until_due = None
        if task.due_date:
            days_until_due = (task.due_date - datetime.utcnow()).days
        
        blocked_tasks_data.append({
            'task_id': task.id,
            'title': task.title,
            'board_name': task.column.board.name,
            'column_name': task.column.name,
            'priority': task.priority.value,
            'due_date': task.due_date.isoformat() if task.due_date else None,
            'days_until_due': days_until_due,
            'blocker_reason': task.blocker_reason,
            'is_overdue': days_until_due is not None and days_until_due < 0
        })
    
    return {
        "blocked_tasks": blocked_tasks_data,
        "total_blocked": len(blocked_tasks_data),
        "last_checked": datetime.utcnow().isoformat()
    }