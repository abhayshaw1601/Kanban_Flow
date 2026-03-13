#!/usr/bin/env python3
"""
Test script to verify the notification system works correctly
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.models.task import Task
from app.models.user import User
from app.core.database import get_db
from app.services.audit_service import AuditService

def test_notification_system():
    """Test the notification system by creating blocked tasks for a specific user"""
    
    print("🧪 Testing Notification System")
    print("=" * 50)
    
    # Get database session
    db = next(get_db())
    
    try:
        # Get a non-admin user for testing
        regular_user = db.query(User).filter(User.role != 'admin').first()
        
        if not regular_user:
            print("❌ No regular users found. Please create a non-admin user first.")
            return
        
        print(f"👤 Testing with user: {regular_user.name} (ID: {regular_user.id})")
        
        # Get some tasks assigned to this user
        user_tasks = db.query(Task).filter(Task.assignee_id == regular_user.id).limit(3).all()
        
        if not user_tasks:
            print("❌ No tasks found for this user. Please assign some tasks first.")
            return
        
        print(f"📋 Found {len(user_tasks)} tasks for user")
        
        # Clear any existing blocker status
        for task in user_tasks:
            task.is_blocker = False
            task.blocker_reason = None
        
        db.commit()
        print("🧹 Cleared existing blocker status")
        
        # Mark tasks as blockers with different scenarios
        scenarios = [
            {
                'task': user_tasks[0],
                'reason': 'Task is 3 days overdue - requires immediate attention',
                'due_date': datetime.utcnow() - timedelta(days=3)
            },
            {
                'task': user_tasks[1] if len(user_tasks) > 1 else None,
                'reason': 'Task due tomorrow - needs completion',
                'due_date': datetime.utcnow() + timedelta(days=1)
            },
            {
                'task': user_tasks[2] if len(user_tasks) > 2 else None,
                'reason': 'High priority task blocking other work',
                'due_date': datetime.utcnow() + timedelta(days=2)
            }
        ]
        
        blocked_count = 0
        for scenario in scenarios:
            if scenario['task']:
                task = scenario['task']
                task.is_blocker = True
                task.blocker_reason = scenario['reason']
                task.due_date = scenario['due_date']
                task.priority = 'high'  # Make it high priority
                blocked_count += 1
                
                print(f"🚨 Marked task '{task.title}' as blocker")
                print(f"   Reason: {scenario['reason']}")
        
        db.commit()
        
        print(f"\n✅ Successfully marked {blocked_count} tasks as blockers for {regular_user.name}")
        print(f"📱 User should now see notification popup when they log in")
        
        # Test the API endpoint
        print("\n🔍 Testing API endpoint...")
        
        # Simulate API call to get blocked tasks
        blocked_tasks = db.query(Task).filter(
            Task.assignee_id == regular_user.id,
            Task.is_blocker == True
        ).all()
        
        print(f"📊 API would return {len(blocked_tasks)} blocked tasks:")
        for task in blocked_tasks:
            days_until_due = (task.due_date - datetime.utcnow()).days if task.due_date else None
            is_overdue = days_until_due is not None and days_until_due < 0
            
            print(f"  - {task.title}")
            print(f"    Priority: {task.priority.value}")
            print(f"    Due: {task.due_date.strftime('%Y-%m-%d') if task.due_date else 'No due date'}")
            print(f"    Overdue: {is_overdue}")
            print(f"    Reason: {task.blocker_reason}")
            print()
        
        print("🎉 Notification system test completed!")
        print("\n📋 Next steps:")
        print(f"1. Start the backend server")
        print(f"2. Login as user: {regular_user.email}")
        print(f"3. You should see a popup notification about {blocked_count} blocked tasks")
        print(f"4. Check the topbar for blocker indicator")
        
    except Exception as e:
        print(f"❌ Error testing notification system: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    
    finally:
        db.close()

if __name__ == "__main__":
    test_notification_system()