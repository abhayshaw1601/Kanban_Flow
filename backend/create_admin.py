#!/usr/bin/env python3
"""
Script to create an admin user for KanbanFlow application.
"""

import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models import User, UserRole

def create_admin_user():
    """Create admin user."""
    db = SessionLocal()
    
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.email == "admin@kanbanflow.com").first()
        if existing_admin:
            print("✓ Admin user already exists!")
            return True
        
        # Create admin user
        admin = User(
            name="Admin User",
            email="admin@kanbanflow.com",
            password=get_password_hash("Admin@123"),
            role=UserRole.ADMIN,
            avatar=None
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print("✓ Admin user created successfully!")
        print(f"  Email: admin@kanbanflow.com")
        print(f"  Password: Admin@123")
        print(f"  Role: {admin.role.value}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error creating admin user: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = create_admin_user()
    if not success:
        sys.exit(1)