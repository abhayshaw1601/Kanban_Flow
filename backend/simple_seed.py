"""
Simple seed script to create companies and users for testing.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.company import Company

def create_test_data():
    """Create test companies and users."""
    db = SessionLocal()
    
    try:
        print("Creating test companies and users...")
        
        # Create companies
        techcorp = Company(
            name="TechCorp Solutions",
            company_id="techcorp",
            description="Leading technology solutions provider"
        )
        db.add(techcorp)
        
        creative = Company(
            name="Creative Agency",
            company_id="creative-agency", 
            description="Full-service digital marketing agency"
        )
        db.add(creative)
        
        db.commit()
        db.refresh(techcorp)
        db.refresh(creative)
        
        # Create TechCorp users
        techcorp_admin = User(
            name="Admin User",
            email="admin@kanbanflow.com",
            password=get_password_hash("Admin@123"),
            role=UserRole.ADMIN,
            company_id=techcorp.id
        )
        db.add(techcorp_admin)
        
        alice = User(
            name="Alice Johnson",
            email="alice@kanbanflow.com",
            password=get_password_hash("Pass@123"),
            role=UserRole.EMPLOYEE,
            company_id=techcorp.id
        )
        db.add(alice)
        
        # Create Creative Agency users
        creative_admin = User(
            name="Creative Admin",
            email="admin@creative.com",
            password=get_password_hash("Admin@123"),
            role=UserRole.ADMIN,
            company_id=creative.id
        )
        db.add(creative_admin)
        
        dave = User(
            name="Dave Brown",
            email="dave@creative.com",
            password=get_password_hash("Pass@123"),
            role=UserRole.EMPLOYEE,
            company_id=creative.id
        )
        db.add(dave)
        
        db.commit()
        
        print("✅ Test data created successfully!")
        print("\nTest Accounts:")
        print("TechCorp Solutions:")
        print("  Admin: admin@kanbanflow.com / Admin@123")
        print("  Employee: alice@kanbanflow.com / Pass@123")
        print("\nCreative Agency:")
        print("  Admin: admin@creative.com / Admin@123")
        print("  Employee: dave@creative.com / Pass@123")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data()