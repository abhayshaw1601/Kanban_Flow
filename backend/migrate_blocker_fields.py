#!/usr/bin/env python3
"""
Database migration script to add blocker fields to tasks table
Works with both SQLite and PostgreSQL
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import text
from app.core.database import engine, get_db
from app.models.task import Task

def migrate_blocker_fields():
    """Add is_blocker and blocker_reason columns to tasks table"""
    
    try:
        # Create a connection
        with engine.connect() as connection:
            # Check if columns already exist
            if 'sqlite' in str(engine.url):
                # SQLite
                result = connection.execute(text("PRAGMA table_info(tasks)"))
                columns = [row[1] for row in result.fetchall()]
            else:
                # PostgreSQL
                result = connection.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'tasks'
                """))
                columns = [row[0] for row in result.fetchall()]
            
            if 'is_blocker' in columns:
                print("✅ Blocker fields already exist in tasks table")
                return True
            
            print("🔄 Adding blocker fields to tasks table...")
            
            # Add is_blocker column
            if 'sqlite' in str(engine.url):
                connection.execute(text("""
                    ALTER TABLE tasks 
                    ADD COLUMN is_blocker BOOLEAN DEFAULT FALSE NOT NULL
                """))
                connection.execute(text("""
                    ALTER TABLE tasks 
                    ADD COLUMN blocker_reason VARCHAR(255) NULL
                """))
            else:
                # PostgreSQL
                connection.execute(text("""
                    ALTER TABLE tasks 
                    ADD COLUMN is_blocker BOOLEAN DEFAULT FALSE NOT NULL,
                    ADD COLUMN blocker_reason VARCHAR(255) NULL
                """))
            
            # Commit changes
            connection.commit()
            
            print("✅ Successfully added blocker fields to tasks table")
            return True
            
    except Exception as e:
        print(f"❌ Error adding blocker fields: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Database Migration: Adding Blocker Fields")
    print("=" * 50)
    
    success = migrate_blocker_fields()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("You can now use the audit feature to mark overdue tasks as blockers.")
    else:
        print("\n💥 Migration failed. Please check the error messages above.")