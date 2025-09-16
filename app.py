from flask import Flask, jsonify, render_template, request, session, redirect, url_for, send_from_directory
from database import db, User, Contact, Message, init_db
from sqlalchemy import inspect, func
from werkzeug.utils import secure_filename
from PIL import Image
import os
import uuid
from datetime import datetime

app = Flask(__name__)

# Configuration
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///ourchat.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# File upload configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm', 'mov', 'avi', 'pdf', 'doc', 'docx', 'txt', 'zip', 'rar'}
IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
VIDEO_EXTENSIONS = {'mp4', 'webm', 'mov', 'avi'}

# For ngrok deployment
if os.environ.get('FLASK_ENV') == 'production':
    app.config['SERVER_NAME'] = None  # Allow any host

# File upload helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_type(filename):
    extension = filename.rsplit('.', 1)[1].lower()
    if extension in IMAGE_EXTENSIONS:
        return 'image' if extension != 'gif' else 'gif'
    elif extension in VIDEO_EXTENSIONS:
        return 'video'
    else:
        return 'file'

def resize_image(image_path, max_size=(800, 800)):
    """Resize image while maintaining aspect ratio"""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Resize image
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            img.save(image_path, 'JPEG', quality=85, optimize=True)
    except Exception as e:
        print(f"Error resizing image: {e}")

# Initialize database
init_db(app)

@app.route('/')
def index():
    # Check if user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login')
def login():
    # If already logged in, redirect to main page
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('index.html')

@app.route('/test-encryption')
def test_encryption():
    """Serve the encryption test page"""
    return send_from_directory('.', 'test_encryption.html')

@app.route('/debug/messages')
def debug_messages():
    """Debug endpoint to see messages in database"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    messages = db.session.query(Message).order_by(Message.timestamp.desc()).limit(10).all()
    result = []
    for msg in messages:
        result.append({
            'id': msg.id,
            'sender_id': msg.sender_id,
            'receiver_id': msg.receiver_id,
            'content': msg.content[:100] + '...' if len(msg.content) > 100 else msg.content,
            'content_length': len(msg.content),
            'message_type': msg.message_type,
            'timestamp': msg.timestamp.isoformat() if msg.timestamp else None
        })
    
    return jsonify({'messages': result})

@app.route('/api/auth/check')
def check_auth():
    """Check if user is authenticated"""
    if 'user_id' in session:
        # FIXED: Use Session.get() instead of User.query.get()
        user = db.session.get(User, session['user_id'])
        if user:
            return jsonify({
                'authenticated': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'user_code': user.user_code,
                    'display_name': user.display_name,
                    'profile_picture': user.profile_picture,
                    'encryption_key': user.encryption_key,
                    'is_admin': user.email == 'admin@ourchat.org'  # Check if admin
                }
            })
    return jsonify({'authenticated': False})

@app.route('/api/auth/login', methods=['POST'])
def login_api():
    """Login endpoint"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    # FIXED: Use db.session.query() instead of User.query
    user = db.session.query(User).filter_by(username=username).first()
    if user and user.check_password(password):
        session['user_id'] = user.id
        session['username'] = user.username
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'user_code': user.user_code,
                'display_name': user.display_name,
                'profile_picture': user.profile_picture,
                'encryption_key': user.encryption_key,
                'is_admin': user.email == 'admin@ourchat.org'  # Check if admin
            }
        })
    
    return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/api/auth/register', methods=['POST'])
def register_api():
    """Register endpoint"""
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400
    
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    # Check if user already exists
    # FIXED: Use db.session.query() instead of User.query
    if db.session.query(User).filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if db.session.query(User).filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # Create new user with unique code and encryption key
    user_code = User.generate_unique_code()
    encryption_key = User.generate_encryption_key()
    user = User(username=username, email=email, user_code=user_code, encryption_key=encryption_key)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    # Auto-login
    session['user_id'] = user.id
    session['username'] = user.username
    
    return jsonify({
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'user_code': user.user_code,
            'display_name': user.display_name,
            'profile_picture': user.profile_picture,
            'encryption_key': user.encryption_key,
            'is_admin': user.email == 'admin@ourchat.org'  # Check if admin
        }
    }), 201

@app.route('/api/auth/logout', methods=['POST'])
def logout_api():
    """Logout endpoint"""
    session.clear()
    return jsonify({'success': True})

@app.route('/api/user/<int:user_id>/encryption-key')
def get_user_encryption_key(user_id):
    """Get encryption key for a specific user (for E2E encryption)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Get the user's encryption key
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'encryption_key': user.encryption_key})

@app.route('/api/contacts')
def get_contacts():
    """API endpoint to get contacts for logged in user"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    search = request.args.get('search', '').lower()
    
    # Get contacts for the current user
    query = db.session.query(Contact).filter_by(user_id=user_id)
    
    if search:
        query = query.filter(Contact.name.ilike(f'%{search}%'))
    
    contacts = query.all()
    
    return jsonify([{
        'id': contact.contact_user_id,  # Use the actual user ID for messaging
        'contact_id': contact.id,  # The contact record ID for deletion
        'name': contact.display_name,
        'username': contact.contact_user.username,  # Real username
        'display_name': contact.contact_user.display_name,  # User's display name
        'profile_picture': contact.contact_user.profile_picture,  # User's profile picture
        'user_code': contact.contact_user.user_code,  # User's code
        'status': contact.status,
        'last_seen': contact.last_seen
    } for contact in contacts])

@app.route('/api/contacts', methods=['POST'])
def add_contact():
    """API endpoint to add a new contact using their user code"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    display_name = data.get('display_name', '').strip()
    user_code = data.get('user_code', '').strip()
    
    if not display_name or not user_code:
        return jsonify({'error': 'Both display name and user code are required'}), 400
    
    if len(user_code) != 6 or not user_code.isdigit():
        return jsonify({'error': 'User code must be exactly 6 digits'}), 400
    
    # Find the user to add as contact by their code
    contact_user = db.session.query(User).filter_by(user_code=user_code).first()
    if not contact_user:
        return jsonify({'error': 'User not found with that code'}), 404
    
    # Don't allow adding yourself
    if contact_user.id == session['user_id']:
        return jsonify({'error': 'Cannot add yourself as a contact'}), 400
    
    # Check if contact already exists
    existing_contact = db.session.query(Contact).filter_by(
        user_id=session['user_id'], 
        contact_user_id=contact_user.id
    ).first()
    
    if existing_contact:
        return jsonify({'error': 'This user is already in your contacts'}), 400
    
    current_user = db.session.get(User, session['user_id'])
    
    # Create contact for current user
    contact = Contact(
        user_id=session['user_id'],
        contact_user_id=contact_user.id,
        display_name=display_name,
        status="Offline"
    )
    db.session.add(contact)
    
    # Create mutual contact (add current user to the other user's contacts)
    # Use the other user's username as the default display name
    mutual_contact = Contact(
        user_id=contact_user.id,
        contact_user_id=session['user_id'],
        display_name=current_user.username,
        status="Offline"
    )
    db.session.add(mutual_contact)
    
    db.session.commit()
    
    return jsonify({
        'id': contact.contact_user_id,
        'contact_id': contact.id,
        'name': contact.display_name,
        'username': contact.contact_user.username,
        'user_code': contact.contact_user.user_code,
        'status': contact.status,
        'last_seen': contact.last_seen,
        'created_at': contact.created_at.isoformat() if contact.created_at else None
    }), 201

@app.route('/api/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    """API endpoint to delete a contact and its mutual relationship"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Find the contact record
    contact = db.session.query(Contact).filter_by(
        id=contact_id,
        user_id=session['user_id']
    ).first()
    
    if not contact:
        return jsonify({'error': 'Contact not found'}), 404
    
    # Find and delete the mutual contact relationship
    mutual_contact = db.session.query(Contact).filter_by(
        user_id=contact.contact_user_id,
        contact_user_id=session['user_id']
    ).first()
    
    if mutual_contact:
        db.session.delete(mutual_contact)
    
    db.session.delete(contact)
    db.session.commit()
    
    return jsonify({'success': True}), 200

@app.route('/api/messages/<int:contact_id>')
def get_messages(contact_id):
    """API endpoint to get messages between current user and contact"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    
    # Get messages between current user and contact (both directions)
    messages = db.session.query(Message).filter(
        ((Message.sender_id == user_id) & (Message.receiver_id == contact_id)) |
        ((Message.sender_id == contact_id) & (Message.receiver_id == user_id))
    ).order_by(Message.timestamp).all()
    
    return jsonify([{
        'id': msg.id,
        'sender_id': msg.sender_id,
        'receiver_id': msg.receiver_id,
        'content': msg.content,
        'message_type': msg.message_type,
        'file_path': msg.file_path,
        'file_name': msg.file_name,
        'file_size': msg.file_size,
        'timestamp': msg.timestamp.isoformat() if msg.timestamp else None
    } for msg in messages])

@app.route('/api/messages', methods=['POST'])
def send_message():
    """API endpoint to send a message"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    receiver_id = data.get('receiver_id')
    content = data.get('content')
    
    if not receiver_id or not content:
        return jsonify({'error': 'Receiver and content are required'}), 400
    
    # Create new message
    message = Message(
        sender_id=session['user_id'],
        receiver_id=receiver_id,
        content=content
    )
    db.session.add(message)
    db.session.commit()
    
    return jsonify({
        'id': message.id,
        'sender_id': message.sender_id,
        'receiver_id': message.receiver_id,
        'content': message.content,
        'timestamp': message.timestamp.isoformat() if message.timestamp else None
    }), 201

# Admin Dashboard API Endpoints
@app.route('/api/admin/stats')
def get_admin_stats():
    """API endpoint to get admin dashboard statistics"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Check if user is admin
    user = db.session.get(User, session['user_id'])
    if not user or user.email != 'admin@ourchat.org':
        return jsonify({'error': 'Access denied'}), 403
    
    # Get statistics
    total_users = db.session.query(User).count()
    total_messages = db.session.query(Message).count()
    total_contacts = db.session.query(Contact).count()
    
    return jsonify({
        'total_users': total_users,
        'total_messages': total_messages,
        'total_contacts': total_contacts
    })

@app.route('/api/admin/users')
def get_all_users():
    """API endpoint to get all users (admin only)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Check if user is admin
    user = db.session.get(User, session['user_id'])
    if not user or user.email != 'admin@ourchat.org':
        return jsonify({'error': 'Access denied'}), 403
    
    users = db.session.query(User).all()
    
    return jsonify([{
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'created_at': user.created_at.isoformat() if user.created_at else None
    } for user in users])

@app.route('/api/admin/messages')
def get_all_messages():
    """API endpoint to get all messages (admin only)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Check if user is admin
    user = db.session.get(User, session['user_id'])
    if not user or user.email != 'admin@ourchat.org':
        return jsonify({'error': 'Access denied'}), 403
    
    # Get all messages with user info
    messages = db.session.query(Message, User).join(User, Message.sender_id == User.id).order_by(Message.timestamp.desc()).limit(100).all()
    
    return jsonify([{
        'id': msg.id,
        'sender_username': sender.username,
        'sender_id': msg.sender_id,
        'receiver_id': msg.receiver_id,
        'content': msg.content,
        'timestamp': msg.timestamp.isoformat() if msg.timestamp else None
    } for msg, sender in messages])

@app.route('/api/user/change-password', methods=['POST'])
def change_password():
    """API endpoint to change user password"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({'error': 'Both current and new passwords are required'}), 400
    
    if len(new_password) < 6:
        return jsonify({'error': 'New password must be at least 6 characters'}), 400
    
    # Get current user
    user = db.session.get(User, session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check current password
    if not user.check_password(current_password):
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    # Update password
    user.set_password(new_password)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Password changed successfully'})

# File serving routes
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Profile picture upload
@app.route('/api/user/profile-picture', methods=['POST'])
def upload_profile_picture():
    """Upload and set user profile picture"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename) or get_file_type(file.filename) != 'image':
        return jsonify({'error': 'Only image files are allowed'}), 400
    
    # Generate unique filename
    filename = secure_filename(file.filename)
    extension = filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{extension}"
    
    # Save file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'profiles', unique_filename)
    file.save(file_path)
    
    # Resize image
    resize_image(file_path, (200, 200))
    
    # Update user profile
    user = db.session.get(User, session['user_id'])
    
    # Remove old profile picture if exists
    if user.profile_picture:
        old_path = os.path.join(app.config['UPLOAD_FOLDER'], user.profile_picture)
        if os.path.exists(old_path):
            os.remove(old_path)
    
    user.profile_picture = f"profiles/{unique_filename}"
    db.session.commit()
    
    return jsonify({
        'success': True,
        'profile_picture': user.profile_picture
    })

# Display name update
@app.route('/api/user/display-name', methods=['POST'])
def update_display_name():
    """Update user display name"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    display_name = data.get('display_name', '').strip()
    
    if not display_name:
        return jsonify({'error': 'Display name is required'}), 400
    
    if len(display_name) > 100:
        return jsonify({'error': 'Display name must be 100 characters or less'}), 400
    
    user = db.session.get(User, session['user_id'])
    user.display_name = display_name
    db.session.commit()
    
    return jsonify({
        'success': True,
        'display_name': display_name
    })

# File upload for messages
@app.route('/api/upload/media', methods=['POST'])
def upload_media():
    """Upload media file for messaging"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    receiver_id = request.form.get('receiver_id')
    
    if not receiver_id:
        return jsonify({'error': 'Receiver ID is required'}), 400
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    # Generate unique filename
    filename = secure_filename(file.filename)
    extension = filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{extension}"
    
    # Determine file type and folder
    file_type = get_file_type(filename)
    if file_type in ['image', 'gif', 'video']:
        folder = 'media'
    else:
        folder = 'files'
    
    # Save file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], folder, unique_filename)
    file.save(file_path)
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    # Resize image if needed
    if file_type == 'image':
        resize_image(file_path)
    
    # Create message
    message = Message(
        sender_id=session['user_id'],
        receiver_id=receiver_id,
        message_type=file_type,
        file_path=f"{folder}/{unique_filename}",
        file_name=filename,
        file_size=file_size
    )
    db.session.add(message)
    db.session.commit()
    
    return jsonify({
        'id': message.id,
        'sender_id': message.sender_id,
        'receiver_id': message.receiver_id,
        'message_type': message.message_type,
        'file_path': message.file_path,
        'file_name': message.file_name,
        'file_size': message.file_size,
        'timestamp': message.timestamp.isoformat() if message.timestamp else None
    }), 201

@app.route('/api/admin/settings', methods=['GET', 'POST'])
def admin_settings():
    """API endpoint to get/set admin settings"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Check if user is admin
    user = db.session.get(User, session['user_id'])
    if not user or user.email != 'admin@ourchat.org':
        return jsonify({'error': 'Access denied'}), 403
    
    if request.method == 'GET':
        # Return current settings (in a real app, these would be stored in a settings table)
        return jsonify({
            'maintenance_mode': 'off',
            'max_users': 1000,
            'message_retention_days': 30
        })
    else:
        # Update settings (in a real app, these would be stored in a settings table)
        data = request.get_json()
        return jsonify({
            'success': True,
            'message': 'Settings updated successfully',
            'settings': data
        })

@app.route('/sitemap.xml')
def sitemap():
    """Serve sitemap.xml for SEO"""
    return send_from_directory('static', 'sitemap.xml', mimetype='application/xml')

@app.route('/robots.txt')
def robots():
    """Serve robots.txt for SEO"""
    robots_txt = """User-agent: *
Allow: /
Sitemap: https://ourchat.strangled.net/sitemap.xml"""
    return robots_txt, 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
