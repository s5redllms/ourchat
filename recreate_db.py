#!/usr/bin/env python3
"""
Force recreate the database with new schema
"""

import os
from app import app
from database import db

if __name__ == "__main__":
    # Remove existing database
    db_files = ['ourchat.db', 'instance/ourchat.db']
    for db_file in db_files:
        try:
            if os.path.exists(db_file):
                os.remove(db_file)
                print(f"Removed {db_file}")
        except PermissionError:
            print(f"Could not remove {db_file} - file is in use")
    
    # Create new database with updated schema
    with app.app_context():
        try:
            db.drop_all()
            print("Dropped all tables")
        except:
            print("Could not drop tables (may not exist)")
        
        db.create_all()
        print("Database recreated with new schema!")
