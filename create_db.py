#!/usr/bin/env python3
import os
import sqlite3

# Remove existing database
if os.path.exists('ourchat.db'):
    os.remove('ourchat.db')
    print("Deleted existing database")

# Create new database with tables
conn = sqlite3.connect('ourchat.db')
cursor = conn.cursor()

# Create User table
cursor.execute('''
CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(120) NOT NULL,
    user_code VARCHAR(6) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Create Contact table
cursor.execute('''
CREATE TABLE contact (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'Offline',
    last_seen VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id)
)
''')

# Create Message table
cursor.execute('''
CREATE TABLE message (
    id INTEGER PRIMARY KEY,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES user(id),
    FOREIGN KEY (receiver_id) REFERENCES user(id)
)
''')

conn.commit()
conn.close()

print("Created database with tables: user, contact, message")
print("Database setup complete!")
