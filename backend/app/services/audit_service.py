"""
Audit Service for checking overdue tasks and marking blockers
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, case
from typing import List, Dict, Any

from ..models.task import Task
from ..models.column import Column
from ..models.board import Board
from ..models.user import User
from ..models.comment import Comment


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
            
            # Mark tasks as blockers and handle reassignment
            blocked_tasks = []
            reassigned_tasks = []
            ai_comments = []
            
            for task in overdue_tasks:
                days_until_due = (task.due_date - datetime.utcnow()).days
                
                # Generate passive-aggressive AI comment
                ai_comment = self._generate_passive_aggressive_comment(task, days_until_due)
                comment = Comment(
                    content=ai_comment,
                    is_ai_generated=True,
                    task_id=task.id,
                    author_id=None  # AI comments have no human author
                )
                self.db.add(comment)
                
                ai_comments.append({
                    'task_id': task.id,
                    'task_title': task.title,
                    'comment': ai_comment
                })
                
                print(f"💬 Added AI comment to task '{task.title}': {ai_comment}")
                
                if days_until_due < 0:
                    reason = f"Task is {abs(days_until_due)} days overdue"
                    
                    # Check if task should be reassigned (overdue by more than 1 day)
                    if abs(days_until_due) > 1:
                        new_assignee = self._find_best_performer_for_reassignment(task)
                        if new_assignee and new_assignee.id != task.assignee_id:
                            old_assignee_name = task.assignee.name if task.assignee else 'Unassigned'
                            task.assignee_id = new_assignee.id
                            reason += f" - Reassigned from {old_assignee_name} to {new_assignee.name}"
                            
                            reassigned_tasks.append({
                                'task_id': task.id,
                                'title': task.title,
                                'old_assignee': old_assignee_name,
                                'new_assignee': new_assignee.name,
                                'days_overdue': abs(days_until_due)
                            })
                            
                            print(f"🔄 Reassigned overdue task '{task.title}' from {old_assignee_name} to {new_assignee.name}")
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
            print(f"🔄 Reassigned {len(reassigned_tasks)} overdue tasks to better performers")
            print(f"💬 Added {len(ai_comments)} AI comments to tasks")
            
            return {
                'audit_completed_at': datetime.utcnow().isoformat(),
                'tasks_marked_as_blockers': len(blocked_tasks),
                'blocked_tasks': blocked_tasks,
                'reassigned_tasks': reassigned_tasks,
                'ai_comments': ai_comments,
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
    
    def _find_best_performer_for_reassignment(self, task: Task) -> User:
        """
        Find the best performing user to reassign an overdue task to.
        
        Looks for users with green performance status (>50% completion rate)
        and selects the one with the best performance and lowest current workload.
        
        Args:
            task: The task that needs reassignment
            
        Returns:
            User object of the best performer, or None if no suitable user found
        """
        try:
            # Get all users except the current assignee and admins
            potential_assignees = self.db.query(User).filter(
                and_(
                    User.role != 'admin',
                    User.id != task.assignee_id if task.assignee_id else True
                )
            ).all()
            
            if not potential_assignees:
                return None
            
            best_performer = None
            best_score = -1
            
            for user in potential_assignees:
                # Calculate user's performance metrics
                user_stats = self._calculate_user_performance(user.id)
                
                # Only consider users with green performance (>50% completion)
                if user_stats['completion_percentage'] > 50:
                    # Calculate score based on completion rate and current workload
                    # Higher completion rate = better, lower workload = better
                    completion_score = user_stats['completion_percentage'] / 100
                    workload_score = max(0, (20 - user_stats['pending_tasks']) / 20)  # Normalize to 0-1
                    
                    # Combined score (70% completion rate, 30% workload)
                    combined_score = (completion_score * 0.7) + (workload_score * 0.3)
                    
                    if combined_score > best_score:
                        best_score = combined_score
                        best_performer = user
            
            return best_performer
            
        except Exception as e:
            print(f"Error finding best performer: {e}")
            return None
    
    def _calculate_user_performance(self, user_id: int) -> Dict[str, Any]:
        """Calculate performance metrics for a specific user"""
        
        try:
            # Get task statistics by column type
            task_stats = self.db.query(
                func.count(Task.id).label('total_tasks'),
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
            
            total_tasks = task_stats.total_tasks or 0
            done_count = task_stats.done_count or 0
            pending_tasks = total_tasks - done_count
            
            completion_percentage = (done_count / total_tasks * 100) if total_tasks > 0 else 0
            
            return {
                'total_tasks': total_tasks,
                'done_tasks': done_count,
                'pending_tasks': pending_tasks,
                'completion_percentage': completion_percentage
            }
            
        except Exception as e:
            print(f"Error calculating user performance: {e}")
            return {
                'total_tasks': 0,
                'done_tasks': 0,
                'pending_tasks': 0,
                'completion_percentage': 0
            }
    
    def _generate_passive_aggressive_comment(self, task: Task, days_until_due: int) -> str:
        """
        Generate a passive-aggressive AI comment for overdue or stuck tasks.
        
        Args:
            task: The task that needs a comment
            days_until_due: Number of days until due (negative if overdue)
            
        Returns:
            A passive-aggressive comment string
        """
        
        # Pool of passive-aggressive comments
        if days_until_due < 0:
            # Overdue comments
            overdue_days = abs(days_until_due)
            overdue_comments = [
                f"🤔 Just checking in... this task was due {overdue_days} days ago. Everything okay?",
                f"⏰ Friendly reminder: this task is now {overdue_days} days overdue. No pressure though! 😅",
                f"📅 I hate to be that AI, but this task missed its deadline by {overdue_days} days. Just saying...",
                f"🚨 Status update needed! This task has been overdue for {overdue_days} days. Should I be worried?",
                f"💭 I'm sure you have a good reason for this task being {overdue_days} days late. Care to share?",
                f"🎯 This task was supposed to be done {overdue_days} days ago. Plot twist: it's still here!",
                f"⚡ Quick question: is this task stuck in a time loop? It's been overdue for {overdue_days} days.",
                f"🔍 Detective AI here: this task went missing {overdue_days} days ago. Any leads?",
                f"📢 Breaking news: Task still not done after {overdue_days} days past deadline!",
                f"🎪 Welcome to the overdue circus! This task has been the star performer for {overdue_days} days.",
                f"🏃‍♂️ This task is running {overdue_days} days behind schedule. Maybe it needs a GPS?",
                f"🎭 The suspense is killing me! Will this {overdue_days}-day overdue task ever be completed?",
                f"🌟 Congratulations! This task has achieved {overdue_days} days of overdue status. New record?",
                f"🔮 My crystal ball says this task was due {overdue_days} days ago. Magic isn't working here.",
                f"🎨 This task is becoming a masterpiece of procrastination - {overdue_days} days in the making!"
            ]
            return overdue_comments[hash(task.title) % len(overdue_comments)]
        
        elif days_until_due <= 1:
            # Due soon comments
            due_soon_comments = [
                "⏳ Tick tock... this task is due very soon. Just a gentle nudge from your friendly AI!",
                "🚀 T-minus 1 day until this task is due. Houston, do we have a problem?",
                "📋 Status check: this task is due tomorrow. Everything under control?",
                "⚠️ Yellow alert! This task is approaching its deadline. All hands on deck?",
                "🎯 Bullseye incoming! This task's deadline is tomorrow. Ready, aim, fire?",
                "🏁 Final lap! This task crosses the finish line tomorrow. Sprint time?",
                "⏰ Last call for this task! Deadline is tomorrow. No pressure... okay, maybe a little.",
                "🎪 The deadline circus is coming to town tomorrow! Is this task ready for the show?",
                "🌅 Tomorrow's sunrise brings this task's deadline. Will it see completion?",
                "🎬 Tomorrow is the premiere date for this task. Is it ready for the spotlight?"
            ]
            return due_soon_comments[hash(task.title) % len(due_soon_comments)]
        
        else:
            # General stuck in progress comments
            stuck_comments = [
                "🤖 AI wellness check: How's this task doing? It's been sitting here for a while...",
                "📊 Status report requested: This task seems to be taking a scenic route to completion.",
                "🔄 Just wondering... is this task stuck in an infinite loop? Asking for a friend (me).",
                "💭 Penny for your thoughts on this task's progress? The suspense is building!",
                "🎯 This task is playing hard to get with the 'Done' column. Any strategies?",
                "🌱 This task is growing roots in the 'In Progress' column. Time to transplant?",
                "🎪 This task is putting on quite a show in the 'In Progress' column. Encore performance?",
                "🔍 Mystery solver AI here: What's the secret to moving this task forward?",
                "⚡ Power-up needed? This task seems to be running low on momentum.",
                "🎨 This task is becoming a permanent art installation in 'In Progress'. Modern art?"
            ]
            return stuck_comments[hash(task.title) % len(stuck_comments)]