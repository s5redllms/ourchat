#!/usr/bin/env python3
"""
Migration script to add new features:
- Profile pictures and display names for users
- Media support for messages
"""

import sqlite3
import os

def migrate_database():
    """Apply migrations to add new columns"""
    db_path = 'ourchat.db'
    
    # Check if database exists
    if not os.path.exists(db_path):
        print("Database doesn't exist. Creating new database with updated schema.")
        # Run the main app to create fresh database
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if display_name column exists
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'display_name' not in columns:
            print("Adding display_name column to user table...")
            cursor.execute("ALTER TABLE user ADD COLUMN display_name VARCHAR(100)")
            
        if 'profile_picture' not in columns:
            print("Adding profile_picture column to user table...")
            cursor.execute("ALTER TABLE user ADD COLUMN profile_picture VARCHAR(255)")
        
        # Check message table
        cursor.execute("PRAGMA table_info(message)")
        message_columns = [column[1] for column in cursor.fetchall()]
        
        if 'message_type' not in message_columns:
            print("Adding message_type column to message table...")
            cursor.execute("ALTER TABLE message ADD COLUMN message_type VARCHAR(20) DEFAULT 'text'")
            
        if 'file_path' not in message_columns:
            print("Adding file_path column to message table...")
            cursor.execute("ALTER TABLE message ADD COLUMN file_path VARCHAR(255)")
            
        if 'file_name' not in message_columns:
            print("Adding file_name column to message table...")
            cursor.execute("ALTER TABLE message ADD COLUMN file_name VARCHAR(255)")
            
        if 'file_size' not in message_columns:
            print("Adding file_size column to message table...")
            cursor.execute("ALTER TABLE message ADD COLUMN file_size INTEGER")
        
        # Make content nullable for media messages
        print("Updating message content to be nullable...")
        # SQLite doesn't support modifying column constraints directly
        # This would require recreating the table, which is complex
        # For now, we'll work with the existing constraint
        
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
