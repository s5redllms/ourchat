#!/usr/bin/env python3
"""
Database migration script to recreate the database with the new Contact schema.
This will delete all existing data and create fresh tables.
"""

import os
from flask import Flask
from database import db, User, Contact, Message

# Create Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ourchat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Remove existing database
db_path = 'ourchat.db'
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"Deleted existing database: {db_path}")

# Initialize new database
db.init_app(app)
with app.app_context():
    db.create_all()
    print("Created new database with updated schema")
    print("Migration complete!")
