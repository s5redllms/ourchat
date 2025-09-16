#!/usr/bin/env python3
from app import app
from database import db

with app.app_context():
    # Drop all tables and recreate
    db.drop_all()
    db.create_all()
    print("Database initialized with current schema!")
    
    # Verify tables were created
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"Created tables: {tables}")
    
    # Check user table schema
    if 'user' in tables:
        columns = inspector.get_columns('user')
        print(f"User table columns: {[col['name'] for col in columns]}")
