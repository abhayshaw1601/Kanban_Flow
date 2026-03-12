#!/usr/bin/env python3
"""
Fix script to move seed users to the Default Company
"""

import sys
import os
sys.path.append('.')

from app.core.database import SessionLocal
from app.models.user import User
from app.models.company import Company

def fix_user_companies():
    """Move seed users to Default Company"""
    print("🔧 Fixing user company assignments...")
    
    db = SessionLocal()
    
    try:
        # Get Default Company
        default_company = db.query(Company).filter(Company.company_id == "default").first()
        if not default_company:
            print("❌ Default Company not found!")
            return
        
        print(f"✅ Found Default Company: {default_company.name} (ID: {default_company.id})")
        
        # Get seed users from KanbanFlow Demo Company
        seed_emails = [
            "alice@kanbanflow.com",
            "bob@kanbanflow.com", 
            "carol@kanbanflow.com",
            "dave@kanbanflow.com",
            "eve@kanbanflow.com"
        ]
        
        moved_count = 0
        for email in seed_emails:
            user = db.query(User).filter(User.email == email).first()
            if user:
                old_company_id = user.company_id
                user.company_id = default_company.id
                print(f"✅ Moved {user.name} ({email}) from company {old_company_id} to {default_company.id}")
                moved_count += 1
            else:
                print(f"⚠️ User not found: {email}")
        
        db.commit()
        
        print(f"\n🎉 Successfully moved {moved_count} users to Default Company!")
        print("\nNow all seed users should appear in your Team Management page.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    fix_user_companies()