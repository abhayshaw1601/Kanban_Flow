"""
AI Task Analyzer Router
Provides endpoints for AI-powered task analysis
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_current_user, get_db
from app.services.ai_analyzer import ai_analyzer, AnalyzeTaskRequest, TaskAnalysis
from app.models.user import User

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