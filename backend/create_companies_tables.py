"""
Create companies table and update users table with company_id.

This script creates the companies table and adds the company_id foreign key
to the users table for multi-tenant support.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.database import Base
from app.models.company import Company
from app.models.user import User

def create_companies_tables():
    """Create companies table and update users table."""
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    print("Creating companies table and updating users table...")
    
    try:
        # Create companies table
        Company.__table__.create(engine, checkfirst=True)
        print("✓ Companies table created")
        
        # Check if company_id column exists in users table
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'company_id'
            """))
            
            if not result.fetchone():
                # Add company_id column to users table
                conn.execute(text("ALTER TABLE users ADD COLUMN company_id INTEGER"))
                print("✓ Added company_id column to users table")
                
                # Create a default company for existing users
                conn.execute(text("""
                    INSERT INTO companies (name, company_id, description, created_at)
                    VALUES ('Default Company', 'default', 'Default company for existing users', NOW())
                """))
                
                # Get the default company ID
                result = conn.execute(text("SELECT id FROM companies WHERE company_id = 'default'"))
                default_company_id = result.fetchone()[0]
                
                # Update all existing users to belong to the default company
                conn.execute(text(f"UPDATE users SET company_id = {default_company_id}"))
                print("✓ Updated existing users with default company")
                
                # Add foreign key constraint
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD CONSTRAINT fk_users_company_id 
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                """))
                print("✓ Added foreign key constraint")
                
                # Make company_id NOT NULL
                conn.execute(text("ALTER TABLE users ALTER COLUMN company_id SET NOT NULL"))
                print("✓ Set company_id as NOT NULL")
                
                conn.commit()
            else:
                print("✓ company_id column already exists in users table")
        
        print("\n🎉 Database migration completed successfully!")
        print("\nNext steps:")
        print("1. Restart your backend server")
        print("2. Test the new company functionality")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        raise

if __name__ == "__main__":
    create_companies_tables()