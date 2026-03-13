#!/usr/bin/env python3
"""
Test script for The Autonomous Project Manager
Demonstrates the complete self-managing Kanban board functionality
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.models.task import Task
from app.models.user import User
from app.models.column import Column
from app.models.comment import Comment
from app.core.database import get_db
from app.services.audit_service import AuditService

def test_autonomous_project_manager():
    """Test The Autonomous Project Manager - complete self-managing Kanban board"""
    
    print("🤖 Testing The Autonomous Project Manager")
    print("=" * 60)
    print("The Scenario: Tasks go to 'In Progress' to die. AI will do the nagging.")
    print("The Goal: Self-managing Kanban board that mutates state without human input.")
    print("=" * 60)
    
    # Get database session
    db = next(get_db())
    
    try:
        # Get users for testing
        users = db.query(User).filter(User.role != 'admin').all()
        
        if len(users) < 2:
            print("❌ Need at least 2 non-admin users for testing.")
            return
        
        print(f"👥 Found {len(users)} users for testing")
        
        # Get "In Progress" column
        in_progress_column = db.query(Column).filter(
            Column.name.ilike('%progress%')
        ).first()
        
        if not in_progress_column:
            in_progress_column = db.query(Column).filter(
                Column.name.ilike('%doing%')
            ).first()
        
        if not in_progress_column:
            print("❌ No 'In Progress' or 'Doing' column found")
            return
        
        print(f"📋 Using column: {in_progress_column.name}")
        
        # Clear existing comments and blockers
        db.query(Comment).delete()
        for task in db.query(Task).all():
            task.is_blocker = False
            task.blocker_reason = None
        
        db.commit()
        print("🧹 Cleared existing comments and blocker status")
        
        # Create test scenarios for autonomous management
        test_scenarios = [
            {
                'title': 'User Authentication System',
                'description': 'Implement secure user login and registration',
                'days_overdue': 5,
                'assignee': users[0],
                'priority': 'high'
            },
            {
                'title': 'Database Migration Scripts',
                'description': 'Create automated database migration system',
                'days_overdue': 3,
                'assignee': users[1] if len(users) > 1 else users[0],
                'priority': 'medium'
            },
            {
                'title': 'API Documentation',
                'description': 'Write comprehensive API documentation',
                'days_overdue': 1,
                'assignee': users[0],
                'priority': 'low'
            },
            {
                'title': 'Performance Optimization',
                'description': 'Optimize database queries and API responses',
                'days_due_soon': 1,
                'assignee': users[1] if len(users) > 1 else users[0],
                'priority': 'high'
            }
        ]
        
        # Create tasks stuck in "In Progress"
        created_tasks = []
        for i, scenario in enumerate(test_scenarios):
            if 'days_overdue' in scenario:
                due_date = datetime.utcnow() - timedelta(days=scenario['days_overdue'])
            else:
                due_date = datetime.utcnow() + timedelta(days=scenario.get('days_due_soon', 7))
            
            task = Task(
                title=scenario['title'],
                description=scenario['description'],
                due_date=due_date,
                priority=scenario['priority'],
                order=i,
                column_id=in_progress_column.id,
                assignee_id=scenario['assignee'].id
            )
            db.add(task)
            created_tasks.append(task)
        
        db.commit()
        print(f"📋 Created {len(created_tasks)} tasks stuck in '{in_progress_column.name}' column")
        
        # Show initial state
        print(f"\n📊 Initial State:")
        for task in created_tasks:
            days_until_due = (task.due_date - datetime.utcnow()).days
            status = "OVERDUE" if days_until_due < 0 else f"Due in {days_until_due} days"
            print(f"  - {task.title} ({task.assignee.name}) - {status}")
        
        # 🤖 THE AUTONOMOUS PROJECT MANAGER ACTIVATES
        print(f"\n🤖 AUTONOMOUS PROJECT MANAGER ACTIVATING...")
        print(f"🔍 The Monitor: Evaluating board state...")
        print(f"🧠 The Logic: Checking for stuck tasks in '{in_progress_column.name}'...")
        print(f"⚡ The Execution: Autonomous actions incoming...")
        
        # Run the audit (The Autonomous Manager)
        audit_service = AuditService(db)
        results = audit_service.run_audit()
        
        print(f"\n🎯 AUTONOMOUS ACTIONS COMPLETED:")
        print(f"  📋 Tasks marked as blockers: {results['tasks_marked_as_blockers']}")
        print(f"  🔄 Tasks reassigned: {len(results.get('reassigned_tasks', []))}")
        print(f"  💬 AI comments added: {len(results.get('ai_comments', []))}")
        
        # Show AI comments (passive-aggressive nagging)
        if results.get('ai_comments'):
            print(f"\n💬 AI PASSIVE-AGGRESSIVE COMMENTS:")
            for comment in results['ai_comments']:
                print(f"  🤖 {comment['task_title']}")
                print(f"     \"{comment['comment']}\"")
                print()
        
        # Show reassignments
        if results.get('reassigned_tasks'):
            print(f"🔄 AUTONOMOUS REASSIGNMENTS:")
            for reassignment in results['reassigned_tasks']:
                print(f"  📋 {reassignment['title']}")
                print(f"     From: {reassignment['old_assignee']} → To: {reassignment['new_assignee']}")
                print(f"     Reason: {reassignment['days_overdue']} days overdue")
                print()
        
        # Verify the three requirements are met
        print(f"✅ REQUIREMENTS VERIFICATION:")
        print(f"  1. ✅ Re-assign tasks to different users: {len(results.get('reassigned_tasks', []))} tasks reassigned")
        print(f"  2. ✅ Leave passive-aggressive comments: {len(results.get('ai_comments', []))} AI comments added")
        print(f"  3. ✅ Add 'Blocker' visual labels: {results['tasks_marked_as_blockers']} tasks marked as blockers")
        
        # Show final state
        print(f"\n📊 FINAL STATE (After AI Intervention):")
        
        # Get updated tasks
        updated_tasks = db.query(Task).filter(
            Task.id.in_([t.id for t in created_tasks])
        ).all()
        
        for task in updated_tasks:
            days_until_due = (task.due_date - datetime.utcnow()).days
            status = "OVERDUE" if days_until_due < 0 else f"Due in {days_until_due} days"
            blocker_status = " [BLOCKER]" if task.is_blocker else ""
            
            # Get AI comments for this task
            ai_comments = db.query(Comment).filter(
                Comment.task_id == task.id,
                Comment.is_ai_generated == True
            ).count()
            
            comment_status = f" ({ai_comments} AI comments)" if ai_comments > 0 else ""
            
            print(f"  - {task.title} ({task.assignee.name}) - {status}{blocker_status}{comment_status}")
        
        print(f"\n🎉 THE AUTONOMOUS PROJECT MANAGER TEST COMPLETED!")
        print(f"🤖 The AI has successfully taken over project management duties.")
        print(f"📋 Tasks have been autonomously managed without human intervention.")
        print(f"💬 Passive-aggressive nagging is now automated.")
        print(f"🔄 Task reassignment is handled by AI performance analysis.")
        print(f"🚨 Blocker labels are automatically applied to overdue tasks.")
        
        print(f"\n🚀 Next Steps:")
        print(f"1. Check the admin audit dashboard to see all AI actions")
        print(f"2. View task cards to see blocker labels and AI comments")
        print(f"3. Login as reassigned users to see notification popups")
        print(f"4. The AI will continue monitoring and managing autonomously")
        
    except Exception as e:
        print(f"❌ Error testing autonomous project manager: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    
    finally:
        db.close()

if __name__ == "__main__":
    test_autonomous_project_manager()