#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('ourchat.db')
cursor = conn.cursor()

# List tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables in database:")
for table in tables:
    print(f"  {table[0]}")

# Check contact table schema if it exists
try:
    cursor.execute("PRAGMA table_info(contact)")
    columns = cursor.fetchall()
    print("\nContact table schema:")
    for col in columns:
        print(f"  {col}")
except Exception as e:
    print(f"\nError checking contact table: {e}")

conn.close()
