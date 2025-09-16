# E2E Encryption Fix

## Problem Identified
The current implementation gives each user their own encryption key, but messages encrypted by User A with their key cannot be decrypted by User B with their different key.

## Solution Options

### Option 1: Shared Conversation Keys (Recommended)
Generate a shared key for each conversation pair and store it for both users.

### Option 2: Key Exchange Protocol
Implement a proper key exchange when users first connect.

### Option 3: Simple Fix - Use Receiver's Key
Encrypt messages with the receiver's key instead of sender's key.

## Implementing Option 3 (Quick Fix)

1. Modify message encryption to use receiver's encryption key
2. Update the database to store which key was used
3. Ensure both sender and receiver can decrypt messages

## Code Changes Needed

1. **Backend (app.py)**: Modify message sending to encrypt with receiver's key
2. **Frontend (script.js)**: Update encryption logic in sendMessage function
3. **Database**: Add optional key_used field to messages table

This approach allows:
- Sender encrypts with receiver's key
- Receiver decrypts with their own key  
- Messages remain encrypted in transit and storage
- Simple implementation with minimal changes
