#!/usr/bin/env python3
import sqlite3
import base64

def inspect_database():
    conn = sqlite3.connect('ourchat.db')
    cursor = conn.cursor()
    
    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Tables in database:")
    for table in tables:
        print(f"  {table[0]}")
    
    # Check users table and their encryption keys
    try:
        cursor.execute("SELECT id, username, email, user_code, encryption_key FROM user LIMIT 5")
        users = cursor.fetchall()
        print("\nUsers and their encryption keys:")
        for user in users:
            print(f"  User {user[0]} ({user[1]}): key={user[4][:20] if user[4] else 'None'}...")
    except Exception as e:
        print(f"\nError checking users table: {e}")
    
    # Check messages table schema
    try:
        cursor.execute("PRAGMA table_info(message)")
        columns = cursor.fetchall()
        print("\nMessage table schema:")
        for col in columns:
            print(f"  {col}")
    except Exception as e:
        print(f"\nError checking message table: {e}")
    
    # Check sample messages
    try:
        cursor.execute("""
            SELECT m.id, m.sender_id, m.receiver_id, m.content, m.message_type, 
                   u1.username as sender, u2.username as receiver
            FROM message m
            JOIN user u1 ON m.sender_id = u1.id
            JOIN user u2 ON m.receiver_id = u2.id
            LIMIT 10
        """)
        messages = cursor.fetchall()
        print(f"\nSample messages ({len(messages)} found):")
        for msg in messages:
            content_preview = msg[3][:50] if msg[3] else 'None'
            print(f"  ID {msg[0]}: {msg[5]} -> {msg[6]}")
            print(f"    Type: {msg[4]}, Content: {content_preview}...")
            
            # Check if content looks like encrypted data (base64)
            if msg[3]:
                try:
                    base64.b64decode(msg[3])
                    print(f"    ✓ Content appears to be base64 encoded (likely encrypted)")
                except:
                    print(f"    ✗ Content doesn't appear to be base64 encoded")
            print()
    except Exception as e:
        print(f"\nError checking messages: {e}")
    
    conn.close()

if __name__ == "__main__":
    inspect_database()
