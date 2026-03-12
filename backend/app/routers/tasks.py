"""
Task management API endpoints.

This module provides endpoints for creating, updating, moving, and deleting tasks
on Kanban boards. Tasks can be assigned to users, prioritized, and moved between columns.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from ..core.database import get_db
from ..core.deps import get_current_user, get_current_admin
from ..models.user import User, UserRole
from ..models.task import Task, TaskPriority
from ..models.column import Column
from ..models.board_member import BoardMember
from ..schemas.task import TaskCreate, TaskUpdate, TaskMove, TaskResponse


router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Create a new task (admin only).
    
    This endpoint:
    1. Validates that the column exists
    2. Validates that the assignee exists (if provided)
    3. Validates that the priority is low/medium/high (handled by schema)
    4. Calculates the appropriate order value (appends to end of column)
    5. Creates the task with all fields
    6. Sets created_at and updated_at timestamps
    7. Returns the created task
    
    Requirements:
        - 7.1: Store title, description, dueDate, priority, columnId, assigneeId
        - 7.2: Generate timestamps for createdAt and updatedAt
        - 7.5: Validate priority values as low, medium, or high
        - 8.2: Validate assigneeId references existing user
        - 24.10: POST /api/tasks endpoint for task creation (admin only)
    
    Args:
        task_data: Task creation data (title, description, due_date, priority, column_id, assignee_id)
        db: Database session
        admin: Current authenticated admin user
        
    Returns:
        TaskResponse: Created task with all fields including id and timestamps
        
    Raises:
        HTTPException 400: If validation fails (invalid priority, non-existent column/assignee)
        HTTPException 403: If user is not an admin (handled by get_current_admin)
    """
    # Validate column exists
    column = db.query(Column).filter(Column.id == task_data.column_id).first()
    if not column:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Column with id {task_data.column_id} does not exist"
        )
    
    # Validate assignee exists (if provided)
    if task_data.assignee_id is not None:
        assignee = db.query(User).filter(User.id == task_data.assignee_id).first()
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with id {task_data.assignee_id} does not exist"
            )
    
    # Calculate order value (append to end of column)
    # Find the maximum order value in the column
    max_order = db.query(Task).filter(
        Task.column_id == task_data.column_id
    ).count()
    
    # Convert priority string to enum
    priority_enum = TaskPriority(task_data.priority)
    
    # Create the task
    new_task = Task(
        title=task_data.title,
        description=task_data.description,
        due_date=task_data.due_date,
        priority=priority_enum,
        column_id=task_data.column_id,
        assignee_id=task_data.assignee_id,
        order=max_order  # Append to end
    )
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    return new_task


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a task (role-based permissions).
    
    This endpoint:
    1. Validates that the task exists
    2. Allows admins to update all fields (title, description, due_date, priority, assignee_id)
    3. Allows employees to update only status-related fields (columnId, order)
    4. Validates priority if provided (handled by schema)
    5. Validates assignee_id if provided
    6. Updates the updated_at timestamp automatically
    7. Returns the updated task
    
    Requirements:
        - 7.3: Update updated_at timestamp when task is updated
        - 24.11: PATCH /api/tasks/:id endpoint for task updates
    
    Args:
        task_id: ID of the task to update
        task_data: Task update data (all fields optional)
        db: Database session
        current_user: Current authenticated user (admin or employee)
        
    Returns:
        TaskResponse: Updated task with all fields including updated timestamp
        
    Raises:
        HTTPException 404: If task does not exist
        HTTPException 400: If validation fails (invalid priority, non-existent assignee)
        HTTPException 403: If employee attempts to update non-status fields
    """
    # Fetch the task
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} does not exist"
        )
    
    # Check if any fields are being updated
    update_data = task_data.model_dump(exclude_unset=True)
    if not update_data:
        # No fields to update, return task as-is
        return task
    
    # Role-based authorization
    if current_user.role == UserRole.ADMIN:
        # Admins can update all fields
        # Validate assignee_id if provided
        if "assignee_id" in update_data and update_data["assignee_id"] is not None:
            assignee = db.query(User).filter(User.id == update_data["assignee_id"]).first()
            if not assignee:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User with id {update_data['assignee_id']} does not exist"
                )
        
        # Update all provided fields
        for field, value in update_data.items():
            if field == "priority" and value is not None:
                # Convert priority string to enum
                setattr(task, field, TaskPriority(value))
            else:
                setattr(task, field, value)
    else:
        # Employees can only update status-related fields (columnId, order)
        # Check if any non-status fields are being updated
        allowed_fields = {"column_id", "order"}
        attempted_fields = set(update_data.keys())
        forbidden_fields = attempted_fields - allowed_fields
        
        if forbidden_fields:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Employees can only update status-related fields (column_id, order). Attempted to update: {', '.join(forbidden_fields)}"
            )
        
        # Update only allowed fields
        for field in allowed_fields:
            if field in update_data:
                setattr(task, field, update_data[field])
    
    # The updated_at timestamp is automatically updated by SQLAlchemy's onupdate
    # But we need to ensure the session knows the object was modified
    db.add(task)
    db.commit()
    db.refresh(task)
    
    return task



@router.patch("/{task_id}/move", response_model=TaskResponse)
async def move_task(
    task_id: int,
    move_data: TaskMove,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Move a task to a different column or reorder within the same column.
    
    This endpoint handles drag-and-drop operations by:
    1. Validating that the task exists
    2. Validating that the destination column exists
    3. Updating the task's column_id and order
    4. Recalculating order values for affected tasks:
       - If moving to a different column: recalculate both source and destination columns
       - If reordering within same column: recalculate only that column
    5. Updating the updated_at timestamp
    6. Returning the updated task
    
    Requirements:
        - 9.1: Update task's columnId and order when moved to different column
        - 9.2: Update task's order when reordered within column
        - 9.5: Update updated_at timestamp when task is moved
        - 24.12: PATCH /api/tasks/:id/move endpoint for task movement
    
    Args:
        task_id: ID of the task to move
        move_data: Movement data (column_id, order)
        db: Database session
        current_user: Current authenticated user (admin or employee)
        
    Returns:
        TaskResponse: Updated task with new column_id and order
        
    Raises:
        HTTPException 404: If task does not exist
        HTTPException 400: If destination column does not exist
    """
    # Fetch the task
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} does not exist"
        )
    
    # Validate destination column exists
    destination_column = db.query(Column).filter(Column.id == move_data.column_id).first()
    if not destination_column:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Column with id {move_data.column_id} does not exist"
        )
    
    # Store original column_id and order
    source_column_id = task.column_id
    source_order = task.order
    destination_column_id = move_data.column_id
    destination_order = move_data.order
    
    # Check if moving to a different column or reordering within same column
    if source_column_id != destination_column_id:
        # Moving to a different column - need to recalculate both columns
        
        # 1. Remove task from source column by decrementing order of tasks after it
        db.query(Task).filter(
            Task.column_id == source_column_id,
            Task.order > source_order
        ).update(
            {Task.order: Task.order - 1},
            synchronize_session=False
        )
        
        # 2. Make space in destination column by incrementing order of tasks at or after destination
        db.query(Task).filter(
            Task.column_id == destination_column_id,
            Task.order >= destination_order
        ).update(
            {Task.order: Task.order + 1},
            synchronize_session=False
        )
        
        # 3. Update the task with new column and order
        task.column_id = destination_column_id
        task.order = destination_order
    else:
        # Reordering within the same column
        if source_order != destination_order:
            if source_order < destination_order:
                # Moving down: decrement order of tasks between source and destination
                db.query(Task).filter(
                    Task.column_id == source_column_id,
                    Task.order > source_order,
                    Task.order <= destination_order
                ).update(
                    {Task.order: Task.order - 1},
                    synchronize_session=False
                )
            else:
                # Moving up: increment order of tasks between destination and source
                db.query(Task).filter(
                    Task.column_id == source_column_id,
                    Task.order >= destination_order,
                    Task.order < source_order
                ).update(
                    {Task.order: Task.order + 1},
                    synchronize_session=False
                )
            
            # Update the task's order
            task.order = destination_order
    
    # The updated_at timestamp is automatically updated by SQLAlchemy's onupdate
    db.add(task)
    db.commit()
    db.refresh(task)
    
    return task


@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    Delete a task (admin only).
    
    This endpoint:
    1. Validates that the task exists
    2. Deletes the task from the database
    3. Returns a success response
    4. After deletion, subsequent attempts to retrieve the task should return 404
    
    Requirements:
        - 7.6: Admin can delete tasks
        - 7.7: Employee cannot delete tasks (enforced by get_current_admin)
        - 24.13: DELETE /api/tasks/:id endpoint for task deletion (admin only)
    
    Args:
        task_id: ID of the task to delete
        db: Database session
        admin: Current authenticated admin user
        
    Returns:
        dict: Success message with deleted task ID
        
    Raises:
        HTTPException 404: If task does not exist
        HTTPException 403: If user is not an admin (handled by get_current_admin)
    """
    # Fetch the task
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} does not exist"
        )
    
    # Delete the task
    db.delete(task)
    db.commit()
    
    return {"message": "Task deleted successfully", "id": task_id}
