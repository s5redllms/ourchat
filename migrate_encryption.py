#!/usr/bin/env python3
"""
Migration script to add encryption_key column to existing users
and generate encryption keys for all existing users.
"""

import sqlite3
import os
import sys
from database import User

def migrate_encryption_keys():
    """Add encryption_key column and generate keys for existing users"""
    
    # Try multiple possible database locations
    possible_paths = ['ourchat.db', 'instance/ourchat.db', 'instance\\ourchat.db']
    db_path = None
    
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("Database file not found. Nothing to migrate.")
        return
    
    print(f"Found database at: {db_path}")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if encryption_key column already exists
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'encryption_key' in columns:
            print("encryption_key column already exists.")
        else:
            print("Adding encryption_key column to user table...")
            # Add the new column (allowing NULL temporarily)
            cursor.execute("ALTER TABLE user ADD COLUMN encryption_key VARCHAR(64)")
            conn.commit()
            print("Column added successfully.")
        
        # Generate encryption keys for users who don't have one
        cursor.execute("SELECT id, username FROM user WHERE encryption_key IS NULL OR encryption_key = ''")
        users_without_keys = cursor.fetchall()
        
        if users_without_keys:
            print(f"Generating encryption keys for {len(users_without_keys)} users...")
            
            for user_id, username in users_without_keys:
                # Generate encryption key using the User model method
                encryption_key = User.generate_encryption_key()
                
                # Update the user with the new encryption key
                cursor.execute("UPDATE user SET encryption_key = ? WHERE id = ?", (encryption_key, user_id))
                print(f"Generated key for user: {username}")
            
            conn.commit()
            print("All encryption keys generated successfully!")
        else:
            print("All users already have encryption keys.")
        
        # Verify the migration
        cursor.execute("SELECT COUNT(*) FROM user WHERE encryption_key IS NULL OR encryption_key = ''")
        users_without_keys_count = cursor.fetchone()[0]
        
        if users_without_keys_count == 0:
            print("✓ Migration completed successfully - all users have encryption keys")
        else:
            print(f"⚠ Warning: {users_without_keys_count} users still don't have encryption keys")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
    
    return True

if __name__ == "__main__":
    print("Starting encryption key migration...")
    success = migrate_encryption_keys()
    if success:
        print("Migration completed!")
        sys.exit(0)
    else:
        print("Migration failed!")
        sys.exit(1)
