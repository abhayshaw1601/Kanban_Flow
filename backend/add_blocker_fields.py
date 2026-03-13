#!/usr/bin/env python3
"""
Database migration script to add blocker fields to tasks table
"""

import sqlite3
import os
from pathlib import Path

def add_blocker_fields():
    """Add is_blocker and blocker_reason columns to tasks table"""
    
    # Get database path
    db_path = Path("kanban.db")
    if not db_path.exists():
        print("❌ Database file not found. Please run the application first to create the database.")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(tasks)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_blocker' in columns:
            print("✅ Blocker fields already exist in tasks table")
            conn.close()
            return True
        
        print("🔄 Adding blocker fields to tasks table...")
        
        # Add is_blocker column
        cursor.execute("""
            ALTER TABLE tasks 
            ADD COLUMN is_blocker BOOLEAN DEFAULT FALSE NOT NULL
        """)
        
        # Add blocker_reason column
        cursor.execute("""
            ALTER TABLE tasks 
            ADD COLUMN blocker_reason VARCHAR(255) NULL
        """)
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("✅ Successfully added blocker fields to tasks table")
        return True
        
    except Exception as e:
        print(f"❌ Error adding blocker fields: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Database Migration: Adding Blocker Fields")
    print("=" * 50)
    
    success = add_blocker_fields()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("You can now use the audit feature to mark overdue tasks as blockers.")
    else:
        print("\n💥 Migration failed. Please check the error messages above.")