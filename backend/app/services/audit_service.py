"""
Audit Service for checking overdue tasks and marking blockers
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Dict, Any

from ..models.task import Task
from ..models.column import Column
from ..models.board import Board
from ..models.user import User


class AuditService:
    """Service for auditing tasks and marking blockers"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def run_audit(self) -> Dict[str, Any]:
        """
        Run complete audit to check for overdue tasks and mark blockers
        
        Returns:
            Dict containing audit results and statistics
        """
        print("🔍 Starting audit process...")
        
        try:
            # Calculate cutoff date (3 days from now)
            cutoff_date = datetime.utcnow() + timedelta(days=3)
            
            # Find tasks that are:
            # 1. Have due dates
            # 2. Due date is within 3 days or overdue
            # 3. Not in "done" columns
            # 4. Not already marked as blockers (if field exists)
            
            query = self.db.query(Task).join(
                Column, Task.column_id == Column.id
            ).filter(
                and_(
                    Task.due_date.isnot(None),
                    Task.due_date <= cutoff_date,
                    ~Column.name.in_(['Done', 'Complete', 'Finished', 'Completed'])
                )
            )
            
            # Add blocker filter only if the field exists
            try:
                query = query.filter(Task.is_blocker == False)
            except Exception:
                # is_blocker field doesn't exist yet, skip this filter
                pass
            
            overdue_tasks = query.all()
            
            print(f"📋 Found {len(overdue_tasks)} tasks requiring blocker status")
            
            # Mark tasks as blockers
            blocked_tasks = []
            for task in overdue_tasks:
                days_until_due = (task.due_date - datetime.utcnow()).days
                
                if days_until_due < 0:
                    reason = f"Task is {abs(days_until_due)} days overdue"
                else:
                    reason = f"Task due in {days_until_due} days"
                
                # Safely set blocker fields
                try:
                    task.is_blocker = True
                    task.blocker_reason = reason
                except Exception as e:
                    print(f"Warning: Could not set blocker fields for task {task.id}: {e}")
                    continue
                
                blocked_tasks.append({
                    'task_id': task.id,
                    'title': task.title,
                    'assignee': task.assignee.name if task.assignee else 'Unassigned',
                    'due_date': task.due_date.isoformat(),
                    'days_until_due': days_until_due,
                    'reason': reason
                })
            
            # Commit changes
            self.db.commit()
            
            # Get statistics
            stats = self._get_audit_statistics()
            
            print(f"✅ Audit completed. Marked {len(blocked_tasks)} tasks as blockers")
            
            return {
                'audit_completed_at': datetime.utcnow().isoformat(),
                'tasks_marked_as_blockers': len(blocked_tasks),
                'blocked_tasks': blocked_tasks,
                'statistics': stats
            }
            
        except Exception as e:
            print(f"Error during audit: {e}")
            self.db.rollback()
            raise
    
    def get_pending_projects(self) -> List[Dict[str, Any]]:
        """
        Get all pending projects (tasks not in done columns)
        
        Returns:
            List of pending tasks with details
        """
        try:
            pending_tasks = self.db.query(Task).join(
                Column, Task.column_id == Column.id
            ).join(
                Board, Column.board_id == Board.id
            ).filter(
                ~Column.name.in_(['Done', 'Complete', 'Finished', 'Completed'])
            ).all()
            
            pending_projects = []
            for task in pending_tasks:
                days_until_due = None
                if task.due_date:
                    days_until_due = (task.due_date - datetime.utcnow()).days
                
                # Safely get blocker fields (in case migration hasn't run)
                is_blocker = getattr(task, 'is_blocker', False)
                blocker_reason = getattr(task, 'blocker_reason', None)
                
                pending_projects.append({
                    'task_id': task.id,
                    'title': task.title,
                    'board_name': task.column.board.name,
                    'column_name': task.column.name,
                    'assignee': task.assignee.name if task.assignee else 'Unassigned',
                    'priority': task.priority.value,
                    'due_date': task.due_date.isoformat() if task.due_date else None,
                    'days_until_due': days_until_due,
                    'is_blocker': is_blocker,
                    'blocker_reason': blocker_reason,
                    'is_overdue': days_until_due is not None and days_until_due < 0
                })
            
            return pending_projects
            
        except Exception as e:
            print(f"Error getting pending projects: {e}")
            return []
    
    def clear_all_blockers(self) -> int:
        """
        Clear all blocker flags from tasks
        
        Returns:
            Number of tasks cleared
        """
        try:
            blocked_tasks = self.db.query(Task).filter(Task.is_blocker == True).all()
            
            for task in blocked_tasks:
                task.is_blocker = False
                task.blocker_reason = None
            
            self.db.commit()
            
            return len(blocked_tasks)
            
        except Exception as e:
            print(f"Error clearing blockers: {e}")
            self.db.rollback()
            return 0
    
    def _get_audit_statistics(self) -> Dict[str, Any]:
        """Get comprehensive audit statistics"""
        
        try:
            # Total tasks
            total_tasks = self.db.query(Task).count()
            
            # Tasks with due dates
            tasks_with_due_dates = self.db.query(Task).filter(Task.due_date.isnot(None)).count()
            
            # Overdue tasks
            overdue_tasks = self.db.query(Task).filter(
                and_(
                    Task.due_date.isnot(None),
                    Task.due_date < datetime.utcnow()
                )
            ).count()
            
            # Tasks due within 3 days
            cutoff_date = datetime.utcnow() + timedelta(days=3)
            due_soon_tasks = self.db.query(Task).filter(
                and_(
                    Task.due_date.isnot(None),
                    Task.due_date <= cutoff_date,
                    Task.due_date >= datetime.utcnow()
                )
            ).count()
            
            # Blocked tasks (safely handle missing field)
            blocked_tasks = 0
            try:
                blocked_tasks = self.db.query(Task).filter(Task.is_blocker == True).count()
            except Exception:
                # is_blocker field doesn't exist yet
                pass
            
            # Completed tasks
            completed_tasks = self.db.query(Task).join(
                Column, Task.column_id == Column.id
            ).filter(
                Column.name.in_(['Done', 'Complete', 'Finished', 'Completed'])
            ).count()
            
            return {
                'total_tasks': total_tasks,
                'tasks_with_due_dates': tasks_with_due_dates,
                'overdue_tasks': overdue_tasks,
                'due_soon_tasks': due_soon_tasks,
                'blocked_tasks': blocked_tasks,
                'completed_tasks': completed_tasks,
                'pending_tasks': total_tasks - completed_tasks
            }
            
        except Exception as e:
            print(f"Error getting audit statistics: {e}")
            return {
                'total_tasks': 0,
                'tasks_with_due_dates': 0,
                'overdue_tasks': 0,
                'due_soon_tasks': 0,
                'blocked_tasks': 0,
                'completed_tasks': 0,
                'pending_tasks': 0
            }