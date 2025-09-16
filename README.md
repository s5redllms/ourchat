# OurChat - Encrypted Messaging Platform

A self-hosted, un-monitored encrypted chat platform with AI capabilities and secure file sharing.

## 🔥 Features

- **End-to-End Encryption** - All messages encrypted client-side
- **User Authentication** - Secure login/registration system
- **Contact Management** - Add contacts via unique 6-digit codes
- **File Sharing** - Images, videos, documents with compression
- **Admin Dashboard** - User and system management
- **Responsive Design** - Works on desktop and mobile
- **SEO Optimized** - Ready for search engine indexing

## 🚀 Quick Deploy

### Deploy to Render (Free)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)

1. Fork this repository
2. Create account at [render.com](https://render.com)
3. Connect your GitHub account
4. Create new Web Service from your fork
5. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --host 0.0.0.0 --port $PORT`

### Environment Variables
```
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///ourchat.db
```

## 🏠 Local Development

### Prerequisites
- Python 3.8+
- SQLite

### Setup
```bash
# Clone repository
git clone https://github.com/s5redllms/ourchat.git
cd ourchat

# Install dependencies
pip install -r requirements.txt

# Create database
python create_db.py

# Run application
python app.py
```

Access at: `http://localhost:5000`

## 📁 Project Structure

```
ourchat/
├── app.py              # Main Flask application
├── database.py         # Database models and setup
├── requirements.txt    # Python dependencies
├── Procfile           # Deployment configuration
├── static/
│   ├── script.js      # Frontend JavaScript
│   ├── crypto.js      # Encryption functions
│   ├── styles.css     # Styling
│   ├── sitemap.xml    # SEO sitemap
│   └── uploads/       # User uploaded files (not in git)
├── templates/
│   └── index.html     # Main HTML template
└── instance/
    └── ourchat.db     # SQLite database (not in git)
```

## 🔐 Security Features

- **Client-Side Encryption**: Messages encrypted before sending
- **Unique User Codes**: 6-digit codes for adding contacts
- **Secure File Upload**: File type validation and size limits
- **Session Management**: Secure user authentication
- **Password Hashing**: BCrypt for password storage

## 🌐 Custom Domain Setup

### Using FreeDNS (ourchat.strangled.net)
1. Create account at [freedns.afraid.org](https://freedns.afraid.org)
2. Add subdomain: `ourchat.strangled.net`
3. Point A record to your hosting service's IP
4. Configure custom domain in your hosting dashboard

## 📊 SEO & Analytics

- **Meta Tags**: Optimized for search engines
- **Sitemap**: Available at `/sitemap.xml`
- **Robots.txt**: Available at `/robots.txt`
- **Google Search Console Ready**

## 🛠️ Development

### Database Management
```bash
# Create fresh database
python create_db.py

# Migrate existing database
python migrate_db.py

# Inspect database
python inspect_db.py
```

### Testing
```bash
# Run production readiness tests
python production_readiness_test.py
```

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📞 Support

For support, create an issue in this repository.

---

**Live Demo:** https://ourchat.strangled.net (coming soon)
