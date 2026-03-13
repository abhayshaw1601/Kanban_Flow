#!/usr/bin/env python3
"""
Database migration script to add comments table
Works with both SQLite and PostgreSQL
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import text
from app.core.database import engine, get_db
from app.models.comment import Comment

def migrate_comments_table():
    """Create comments table for AI-generated passive-aggressive comments"""
    
    try:
        # Create a connection
        with engine.connect() as connection:
            # Check if table already exists
            if 'sqlite' in str(engine.url):
                # SQLite
                result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='comments'"))
                table_exists = result.fetchone() is not None
            else:
                # PostgreSQL
                result = connection.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_name = 'comments'
                """))
                table_exists = result.fetchone() is not None
            
            if table_exists:
                print("✅ Comments table already exists")
                return True
            
            print("🔄 Creating comments table...")
            
            # Create comments table
            if 'sqlite' in str(engine.url):
                connection.execute(text("""
                    CREATE TABLE comments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        content TEXT NOT NULL,
                        is_ai_generated BOOLEAN DEFAULT FALSE NOT NULL,
                        task_id INTEGER NOT NULL,
                        author_id INTEGER NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                        FOREIGN KEY (task_id) REFERENCES tasks (id),
                        FOREIGN KEY (author_id) REFERENCES users (id)
                    )
                """))
            else:
                # PostgreSQL
                connection.execute(text("""
                    CREATE TABLE comments (
                        id SERIAL PRIMARY KEY,
                        content TEXT NOT NULL,
                        is_ai_generated BOOLEAN DEFAULT FALSE NOT NULL,
                        task_id INTEGER NOT NULL,
                        author_id INTEGER NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                        FOREIGN KEY (task_id) REFERENCES tasks (id),
                        FOREIGN KEY (author_id) REFERENCES users (id)
                    )
                """))
            
            # Commit changes
            connection.commit()
            
            print("✅ Successfully created comments table")
            return True
            
    except Exception as e:
        print(f"❌ Error creating comments table: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Database Migration: Creating Comments Table")
    print("=" * 50)
    
    success = migrate_comments_table()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("The AI can now leave passive-aggressive comments on tasks.")
    else:
        print("\n💥 Migration failed. Please check the error messages above.")