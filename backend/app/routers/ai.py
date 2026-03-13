"""
AI Task Analyzer Router
Provides endpoints for AI-powered task analysis and diagram processing
"""

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from sqlalchemy.orm import Session
from app.core.deps import get_current_user, get_db
from app.services.ai_analyzer import ai_analyzer, AnalyzeTaskRequest, TaskAnalysis
from app.models.user import User
import base64
from typing import Dict, Any

router = APIRouter()


@router.post("/analyze", response_model=TaskAnalysis)
async def analyze_task(
    request: AnalyzeTaskRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze a task prompt using AI and return structured breakdown
    """
    try:
        print(f"AI Analysis request from user {current_user.id}: {request.prompt}")
        analysis = await ai_analyzer.analyze_prompt(request)
        print(f"AI Analysis completed successfully for user {current_user.id}")
        return analysis
    except Exception as e:
        print(f"AI analysis failed for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"AI analysis failed: {str(e)}"
        )


@router.get("/health")
async def check_ai_health():
    """
    Check if the AI service is healthy and available
    No authentication required for health checks
    """
    try:
        is_healthy = await ai_analyzer.check_health()
        return {
            "status": "healthy" if is_healthy else "degraded",
            "ai_service": "connected" if is_healthy else "unavailable"
        }
    except Exception as e:
        return {
            "status": "unavailable",
            "ai_service": "disconnected",
            "error": str(e)
        }


@router.post("/enhance-task/{task_id}")
async def enhance_task_with_ai(
    task_id: int,
    request: AnalyzeTaskRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Enhance an existing task with AI analysis
    """
    from app.models.task import Task
    from app.models.board_member import BoardMember
    
    print(f"Enhance task request from user {current_user.id} for task {task_id}")
    
    # Get the task
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check permissions - user must be a member of the board that contains this task
    board_id = task.column.board_id
    is_member = db.query(BoardMember).filter(
        BoardMember.board_id == board_id,
        BoardMember.user_id == current_user.id
    ).first()
    
    if not is_member:
        raise HTTPException(
            status_code=403, 
            detail="You do not have access to this board"
        )
    
    try:
        print(f"Starting AI analysis for task: {request.prompt}")
        # Analyze the task
        analysis = await ai_analyzer.analyze_prompt(request)
        
        # Format as markdown and update task description
        enhanced_description = ai_analyzer.format_analysis_as_markdown(analysis, task.title)
        task.description = enhanced_description
        
        db.commit()
        db.refresh(task)
        
        print(f"Task {task_id} enhanced successfully")
        
        return {
            "success": True,
            "message": "Task enhanced with AI analysis",
            "analysis": analysis,
            "task_id": task_id
        }
        
    except Exception as e:
        print(f"Failed to enhance task {task_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to enhance task: {str(e)}"
        )


@router.post("/analyze-diagram")
async def analyze_diagram(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze architecture/flow diagram and convert to structured JSON format
    Only admins can use this feature
    """
    # Check if user is admin
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=403,
            detail="Only administrators can analyze diagrams"
        )
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="Only image files are supported (PNG, JPEG, GIF, WebP)"
        )
    
    try:
        print(f"Diagram analysis request from admin {current_user.id}: {file.filename}")
        
        # Read and encode the image
        image_data = await file.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Analyze the diagram using AI
        analysis_result = await ai_analyzer.analyze_diagram(image_base64, file.content_type)
        
        print(f"Diagram analysis completed successfully for admin {current_user.id}")
        
        return {
            "success": True,
            "message": "Diagram analyzed successfully",
            "filename": file.filename,
            "content_type": file.content_type,
            "analysis": analysis_result
        }
        
    except Exception as e:
        print(f"Diagram analysis failed for admin {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Diagram analysis failed: {str(e)}"
        )


@router.post("/create-tasks-from-diagram/{board_id}")
async def create_tasks_from_diagram(
    board_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze diagram and create tasks on a specific board
    Only admins can use this feature
    """
    from ..models.board import Board
    from ..models.board_member import BoardMember
    from ..models.column import Column
    from ..models.task import Task, TaskPriority
    
    # Check if user is admin
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=403,
            detail="Only administrators can create tasks from diagrams"
        )
    
    # Verify board exists and user has access
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(
            status_code=404,
            detail="Board not found"
        )
    
    # Check if user is a member of the board
    is_member = db.query(BoardMember).filter(
        BoardMember.board_id == board_id,
        BoardMember.user_id == current_user.id
    ).first()
    
    if not is_member:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this board"
        )
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="Only image files are supported (PNG, JPEG, GIF, WebP)"
        )
    
    try:
        print(f"Creating tasks from diagram for board {board_id} by admin {current_user.id}")
        
        # Read and encode the image
        image_data = await file.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Analyze the diagram using AI
        analysis_result = await ai_analyzer.analyze_diagram(image_base64, file.content_type)
        
        # Get the first column (usually "To Do" or "Backlog")
        first_column = db.query(Column).filter(
            Column.board_id == board_id
        ).order_by(Column.order.asc()).first()
        
        if not first_column:
            raise HTTPException(
                status_code=400,
                detail="Board has no columns. Please create columns first."
            )
        
        # Extract suggested tasks from analysis
        suggested_tasks = analysis_result.get('project_breakdown', {}).get('suggested_tasks', [])
        
        if not suggested_tasks:
            raise HTTPException(
                status_code=400,
                detail="No tasks could be extracted from the diagram"
            )
        
        # Create tasks from the analysis
        created_tasks = []
        for i, task_data in enumerate(suggested_tasks):
            # Map priority
            priority_map = {
                'high': TaskPriority.HIGH,
                'medium': TaskPriority.MEDIUM,
                'low': TaskPriority.LOW
            }
            priority = priority_map.get(task_data.get('priority', 'medium'), TaskPriority.MEDIUM)
            
            # Create task description with AI analysis context
            description = f"""**Generated from Architecture Diagram Analysis**

{task_data.get('description', '')}

**Component**: {task_data.get('component', 'N/A')}
**Estimated Effort**: {task_data.get('estimated_effort', 'Not specified')}

**Dependencies**: {', '.join(task_data.get('dependencies', [])) if task_data.get('dependencies') else 'None'}

---
*This task was automatically generated from diagram analysis using AI.*
"""
            
            # Create the task
            task = Task(
                title=task_data.get('title', f'Task {i+1}'),
                description=description,
                priority=priority,
                column_id=first_column.id,
                order=i,  # Order tasks sequentially
                assignee_id=None  # Will be assigned by admin later
            )
            
            db.add(task)
            created_tasks.append({
                'title': task.title,
                'description': task.description,
                'priority': task.priority.value,
                'component': task_data.get('component', 'N/A'),
                'estimated_effort': task_data.get('estimated_effort', 'Not specified'),
                'dependencies': task_data.get('dependencies', [])
            })
        
        # Commit all tasks
        db.commit()
        
        print(f"Created {len(created_tasks)} tasks from diagram analysis")
        
        return {
            "success": True,
            "message": f"Successfully created {len(created_tasks)} tasks from diagram analysis",
            "board_id": board_id,
            "board_name": board.name,
            "column_name": first_column.name,
            "tasks_created": len(created_tasks),
            "created_tasks": created_tasks,
            "analysis_summary": {
                "diagram_type": analysis_result.get('diagram_type', 'unknown'),
                "title": analysis_result.get('title', 'Untitled Diagram'),
                "description": analysis_result.get('description', ''),
                "components_found": len(analysis_result.get('components', [])),
                "connections_found": len(analysis_result.get('connections', []))
            }
        }
        
    except Exception as e:
        print(f"Failed to create tasks from diagram: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create tasks from diagram: {str(e)}"
        )