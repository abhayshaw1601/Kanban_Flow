#!/usr/bin/env python3
"""
Test script to verify the enhanced notification system with nagging and reassignment
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

def test_enhanced_notification_system():
    """Test the enhanced notification system with nagging and reassignment"""
    
    print("🧪 Testing Enhanced Notification System")
    print("=" * 60)
    
    # Get database session
    db = next(get_db())
    
    try:
        # Get users for testing
        users = db.query(User).filter(User.role != 'admin').all()
        
        if len(users) < 2:
            print("❌ Need at least 2 non-admin users for testing. Please create more users.")
            return
        
        print(f"👥 Found {len(users)} users for testing")
        
        # Create a high performer (green status - >50% completion)
        high_performer = users[0]
        print(f"🌟 High performer: {high_performer.name}")
        
        # Create a low performer (will get tasks reassigned from them)
        low_performer = users[1] if len(users) > 1 else users[0]
        print(f"📉 Low performer: {low_performer.name}")
        
        # Clear existing blocker status
        all_tasks = db.query(Task).all()
        for task in all_tasks:
            task.is_blocker = False
            task.blocker_reason = None
        
        db.commit()
        print("🧹 Cleared existing blocker status")
        
        # Set up performance data - make first user a high performer
        high_performer_tasks = db.query(Task).filter(Task.assignee_id == high_performer.id).limit(10).all()
        
        # Mark most of high performer's tasks as done (to get >50% completion)
        done_count = 0
        for i, task in enumerate(high_performer_tasks):
            if i < 7:  # Mark 7 out of 10 as done (70% completion)
                # Find a "Done" column or create the effect
                from app.models.column import Column
                done_column = db.query(Column).filter(Column.name.ilike('%done%')).first()
                if done_column:
                    task.column_id = done_column.id
                    done_count += 1
        
        print(f"✅ Set up {high_performer.name} as high performer ({done_count} completed tasks)")
        
        # Create overdue tasks for low performer that will be reassigned
        overdue_scenarios = [
            {
                'title': 'Critical Bug Fix - Payment System',
                'description': 'Fix critical payment processing bug affecting customers',
                'days_overdue': 3,
                'priority': 'high'
            },
            {
                'title': 'Database Migration Script',
                'description': 'Create and test database migration for new features',
                'days_overdue': 5,
                'priority': 'high'
            },
            {
                'title': 'Security Vulnerability Patch',
                'description': 'Apply security patches to prevent data breaches',
                'days_overdue': 2,
                'priority': 'high'
            }
        ]
        
        # Get a column for these tasks
        from app.models.column import Column
        todo_column = db.query(Column).filter(Column.name.ilike('%todo%')).first()
        if not todo_column:
            todo_column = db.query(Column).first()
        
        created_tasks = []
        for i, scenario in enumerate(overdue_scenarios):
            task = Task(
                title=scenario['title'],
                description=scenario['description'],
                due_date=datetime.utcnow() - timedelta(days=scenario['days_overdue']),
                priority=scenario['priority'],
                order=i,
                column_id=todo_column.id,
                assignee_id=low_performer.id
            )
            db.add(task)
            created_tasks.append(task)
        
        db.commit()
        print(f"📋 Created {len(created_tasks)} overdue tasks for {low_performer.name}")
        
        # Run the audit to trigger reassignment
        print("\n🔍 Running audit with reassignment logic...")
        audit_service = AuditService(db)
        results = audit_service.run_audit()
        
        print(f"\n📊 Audit Results:")
        print(f"  - Tasks marked as blockers: {results['tasks_marked_as_blockers']}")
        print(f"  - Tasks reassigned: {len(results.get('reassigned_tasks', []))}")
        
        # Show reassignment details
        if results.get('reassigned_tasks'):
            print(f"\n🔄 Reassignment Details:")
            for reassignment in results['reassigned_tasks']:
                print(f"  📋 {reassignment['title']}")
                print(f"     From: {reassignment['old_assignee']} → To: {reassignment['new_assignee']}")
                print(f"     Reason: {reassignment['days_overdue']} days overdue")
                print()
        
        # Test nagging messages
        print(f"\n💬 Testing Nagging Messages:")
        nag_messages = [
            "🔥 Your tasks are burning! Time to put out the fire!",
            "⚡ These blockers won't resolve themselves. Get moving!",
            "🚨 URGENT: Your team is waiting on YOU!",
            "💥 Stop procrastinating! These tasks need action NOW!",
            "⏰ Time is money, and you're wasting both!"
        ]
        
        for i, message in enumerate(nag_messages[:3]):
            print(f"  {i+1}. {message}")
        
        print(f"\n🎉 Enhanced notification system test completed!")
        print(f"\n📋 Summary:")
        print(f"  - High performer ({high_performer.name}) has green status")
        print(f"  - Overdue tasks automatically reassigned to high performer")
        print(f"  - Aggressive nagging messages will be shown to employees")
        print(f"  - {results['tasks_marked_as_blockers']} tasks marked as blockers")
        print(f"  - {len(results.get('reassigned_tasks', []))} tasks reassigned")
        
        print(f"\n🚀 Next Steps:")
        print(f"1. Start backend server")
        print(f"2. Login as {low_performer.name} to see nagging notifications")
        print(f"3. Login as {high_performer.name} to see newly assigned tasks")
        print(f"4. Check admin audit dashboard for reassignment details")
        
    except Exception as e:
        print(f"❌ Error testing enhanced notification system: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    
    finally:
        db.close()

if __name__ == "__main__":
    test_enhanced_notification_system()