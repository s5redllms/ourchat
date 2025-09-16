from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from werkzeug.security import generate_password_hash, check_password_hash
import os
import random

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(120), nullable=False)
    user_code = db.Column(db.String(6), unique=True, nullable=False, index=True)  # 6-digit unique code
    display_name = db.Column(db.String(100), nullable=True)  # Optional display name
    profile_picture = db.Column(db.String(255), nullable=True)  # Path to profile picture
    encryption_key = db.Column(db.String(64), nullable=False)  # Mid-entropy passphrase for E2E encryption
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), index=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def generate_unique_code():
        """Generate a unique 6-digit code for the user"""
        while True:
            code = f"{random.randint(100000, 999999)}"
            # Check if code already exists
            existing_user = db.session.query(User).filter_by(user_code=code).first()
            if not existing_user:
                return code
    
    @staticmethod
    def generate_encryption_key():
        """Generate a mid-entropy encryption key using words and numbers"""
        import string
        import secrets
        
        # Word list for mid-entropy passphrase
        words = [
            'alpha', 'bravo', 'charlie', 'delta', 'echo', 'foxtrot', 'golf', 'hotel',
            'india', 'juliet', 'kilo', 'lima', 'mike', 'november', 'oscar', 'papa',
            'quebec', 'romeo', 'sierra', 'tango', 'uniform', 'victor', 'whiskey', 'xray',
            'yankee', 'zulu', 'ocean', 'river', 'mountain', 'forest', 'desert', 'valley',
            'castle', 'bridge', 'tower', 'garden', 'island', 'harbor', 'meadow', 'canyon',
            'storm', 'thunder', 'lightning', 'rainbow', 'sunrise', 'sunset', 'moonlight',
            'starlight', 'comet', 'galaxy', 'planet', 'asteroid', 'nebula', 'cosmic'
        ]
        
        # Generate key: 3 random words + 4 random digits
        selected_words = secrets.SystemRandom().choices(words, k=3)
        random_digits = ''.join(secrets.SystemRandom().choices(string.digits, k=4))
        
        # Combine with separators
        encryption_key = '-'.join(selected_words) + '-' + random_digits
        return encryption_key
    
    def __repr__(self):
        return f'<User {self.username}>'

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)  # Owner of the contact list
    contact_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)  # The actual user being contacted
    display_name = db.Column(db.String(100), nullable=False)  # Custom display name for the contact
    status = db.Column(db.String(50), default='Offline')
    last_seen = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), index=True)
    
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('contacts', lazy=True))
    contact_user = db.relationship('User', foreign_keys=[contact_user_id])
    
    def __repr__(self):
        return f'<Contact {self.display_name}>'

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=True)  # Text content (nullable for media-only messages)
    message_type = db.Column(db.String(20), default='text', nullable=False, index=True)  # text, image, video, gif, file
    file_path = db.Column(db.String(255), nullable=True)  # Path to uploaded file
    file_name = db.Column(db.String(255), nullable=True)  # Original filename
    file_size = db.Column(db.Integer, nullable=True)  # File size in bytes
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp(), index=True)
    
    # Composite index for efficient message queries between users
    __table_args__ = (
        db.Index('idx_sender_receiver_timestamp', 'sender_id', 'receiver_id', 'timestamp'),
        db.Index('idx_receiver_sender_timestamp', 'receiver_id', 'sender_id', 'timestamp'),
    )
    
    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])

    def __repr__(self):
        return f'<Message {self.id}>'

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
        # Database tables created, no sample data added
