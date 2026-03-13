"""
Comments API endpoints for task comments and AI-generated messages.

This module provides endpoints for managing task comments, including
AI-generated passive-aggressive status updates.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from ..core.database import get_db
from ..core.deps import get_current_user
from ..models.user import User
from ..models.task import Task
from ..models.comment import Comment

router = APIRouter(prefix="/api/comments", tags=["comments"])


@router.get("/task/{task_id}")
async def get_task_comments(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all comments for a specific task.
    
    Args:
        task_id: ID of the task to get comments for
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of comments for the task
        
    Raises:
        HTTPException 404: If task not found
    """
    # Verify task exists
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    
    # Get all comments for the task, ordered by creation date
    comments = db.query(Comment).filter(
        Comment.task_id == task_id
    ).order_by(Comment.created_at.asc()).all()
    
    # Format comments
    comments_data = []
    for comment in comments:
        comments_data.append({
            'id': comment.id,
            'content': comment.content,
            'is_ai_generated': comment.is_ai_generated,
            'author': {
                'id': comment.author.id,
                'name': comment.author.name,
                'email': comment.author.email
            } if comment.author else {
                'id': None,
                'name': 'AI Assistant',
                'email': 'ai@kanbanflow.com'
            },
            'created_at': comment.created_at.isoformat(),
            'updated_at': comment.updated_at.isoformat()
        })
    
    return {
        "comments": comments_data,
        "total_comments": len(comments_data),
        "ai_comments": len([c for c in comments_data if c['is_ai_generated']])
    }


@router.post("/task/{task_id}")
async def create_task_comment(
    task_id: int,
    comment_data: Dict[str, str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new comment on a task.
    
    Args:
        task_id: ID of the task to comment on
        comment_data: Dictionary containing 'content' field
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Created comment data
        
    Raises:
        HTTPException 404: If task not found
        HTTPException 400: If comment content is missing or empty
    """
    # Verify task exists
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    
    # Validate comment content
    content = comment_data.get('content', '').strip()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment content cannot be empty"
        )
    
    # Create comment
    comment = Comment(
        content=content,
        is_ai_generated=False,
        task_id=task_id,
        author_id=current_user.id
    )
    
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    return {
        'id': comment.id,
        'content': comment.content,
        'is_ai_generated': comment.is_ai_generated,
        'author': {
            'id': current_user.id,
            'name': current_user.name,
            'email': current_user.email
        },
        'created_at': comment.created_at.isoformat(),
        'updated_at': comment.updated_at.isoformat()
    }