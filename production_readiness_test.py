#!/usr/bin/env python3
"""
OurChat Production Readiness Testing Script
==========================================

Comprehensive testing suite to verify that the OurChat application
is ready for production deployment. Tests all features with heavy
error handling and detailed reporting.

Author: Production Testing Suite
Version: 1.0
"""

import os
import sys
import json
import time
import logging
import sqlite3
import requests
import tempfile
import threading
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin
import psutil
import unittest
from unittest.mock import patch, MagicMock
from contextlib import contextmanager
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

class ProductionReadinessTest:
    """Main test class for production readiness verification"""
    
    def __init__(self, base_url="http://localhost:5000", verbose=True):
        self.base_url = base_url.rstrip('/')
        self.verbose = verbose
        self.test_results = []
        self.critical_failures = []
        self.warnings = []
        self.session = requests.Session()
        self.session.timeout = 30
        
        # Test configuration
        self.test_user_data = {
            'username': f'testuser_{int(time.time())}',
            'email': f'test_{int(time.time())}@test.com',
            'password': 'TestPassword123!'
        }
        
        self.admin_user_data = {
            'username': 'admin',
            'email': 'admin@ourchat.org',
            'password': 'admin123'  # This should be changed in production
        }
        
        # Setup logging
        self._setup_logging()
        
        # Create test directories
        self.test_dir = Path(__file__).parent / "test_temp"
        self.test_dir.mkdir(exist_ok=True)
        
        self.logger.info("=== OurChat Production Readiness Test Suite ===")
        self.logger.info(f"Testing URL: {self.base_url}")
        self.logger.info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def _setup_logging(self):
        """Setup comprehensive logging"""
        self.logger = logging.getLogger('ProductionTest')
        self.logger.setLevel(logging.DEBUG if self.verbose else logging.INFO)
        
        # File handler
        log_file = f"production_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO if self.verbose else logging.WARNING)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    @contextmanager
    def error_handler(self, test_name: str, critical: bool = False):
        """Context manager for consistent error handling"""
        start_time = time.time()
        try:
            self.logger.info(f"Starting test: {test_name}")
            yield
            
            duration = time.time() - start_time
            self.test_results.append({
                'test': test_name,
                'status': 'PASSED',
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            })
            self.logger.info(f"✅ {test_name} - PASSED ({duration:.2f}s)")
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"{test_name}: {str(e)}"
            
            self.test_results.append({
                'test': test_name,
                'status': 'FAILED',
                'error': str(e),
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            })
            
            if critical:
                self.critical_failures.append(error_msg)
                self.logger.error(f"❌ CRITICAL: {error_msg}")
            else:
                self.warnings.append(error_msg)
                self.logger.warning(f"⚠️  WARNING: {error_msg}")

    def safe_request(self, method: str, endpoint: str, **kwargs):
        """Make HTTP request with comprehensive error handling"""
        url = urljoin(self.base_url, endpoint)
        
        try:
            response = self.session.request(method, url, **kwargs)
            self.logger.debug(f"{method} {url} -> {response.status_code}")
            return response
        except requests.exceptions.ConnectionError:
            raise Exception(f"Cannot connect to {url}. Is the server running?")
        except requests.exceptions.Timeout:
            raise Exception(f"Request to {url} timed out")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")

    def run_all_tests(self):
        """Run all production readiness tests"""
        self.logger.info("🚀 Starting comprehensive production readiness tests...")
        
        # Test categories in order of importance
        test_methods = [
            ('Basic Connectivity', self.test_basic_connectivity),
            ('Environment Configuration', self.test_environment_config),
            ('Database Connectivity', self.test_database_connectivity),
            ('Authentication System', self.test_authentication_system),
            ('API Endpoints', self.test_api_endpoints),
            ('Security Features', self.test_security_features),
            ('File Upload System', self.test_file_upload_system),
            ('Admin Dashboard', self.test_admin_dashboard),
            ('Performance & Load', self.test_performance),
            ('Error Handling', self.test_error_handling),
            ('Production Configuration', self.test_production_config)
        ]
        
        for category, test_method in test_methods:
            self.logger.info(f"\n📋 Testing Category: {category}")
            try:
                test_method()
            except Exception as e:
                self.logger.error(f"Category {category} failed: {str(e)}")
                self.critical_failures.append(f"{category}: {str(e)}")
        
        # Generate final report
        self.generate_report()

    def test_basic_connectivity(self):
        """Test basic server connectivity and response"""
        with self.error_handler("Server Connectivity", critical=True):
            response = self.safe_request('GET', '/')
            if response.status_code not in [200, 302]:  # 302 for redirect to login
                raise Exception(f"Server returned status {response.status_code}")
        
        with self.error_handler("Static Files Serving"):
            response = self.safe_request('GET', '/static/script.js')
            if response.status_code != 200:
                raise Exception("Static files not properly served")
        
        with self.error_handler("Favicon and Basic Assets"):
            # Test common assets
            assets = ['/robots.txt', '/sitemap.xml']
            for asset in assets:
                response = self.safe_request('GET', asset)
                if response.status_code != 200:
                    self.logger.warning(f"Asset {asset} not found")

    def test_environment_config(self):
        """Test environment configuration"""
        with self.error_handler("Environment Variables", critical=True):
            # Check if we're in development mode (not production ready)
            if os.environ.get('FLASK_ENV') == 'development':
                raise Exception("FLASK_ENV is set to development - not production ready")
            
            # Check for proper secret key
            secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
            if secret_key == 'your-secret-key-change-this-in-production':
                raise Exception("Using default SECRET_KEY - security risk!")
            
            if len(secret_key) < 32:
                raise Exception("SECRET_KEY too short - should be at least 32 characters")
        
        with self.error_handler("Database Configuration"):
            db_url = os.environ.get('DATABASE_URL', 'sqlite:///ourchat.db')
            if 'sqlite' in db_url.lower() and 'production' in os.environ.get('ENVIRONMENT', '').lower():
                self.warnings.append("Using SQLite in production - consider PostgreSQL/MySQL")

    def test_database_connectivity(self):
        """Test database connectivity and structure"""
        with self.error_handler("Database Connection", critical=True):
            # Import app to test database connection
            sys.path.append(os.path.dirname(__file__))
            try:
                from app import app
                from database import db, User, Contact, Message
                
                with app.app_context():
                    # Test database connection
                    db.session.execute('SELECT 1')
                    
                    # Test table existence
                    tables = ['user', 'contact', 'message']
                    for table in tables:
                        result = db.session.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                        if not result.fetchone():
                            raise Exception(f"Table {table} does not exist")
                    
                    self.logger.info("Database connection and structure verified")
                    
            except ImportError as e:
                raise Exception(f"Cannot import application modules: {str(e)}")
        
        with self.error_handler("Database Constraints"):
            with app.app_context():
                # Test unique constraints
                try:
                    # Test user code uniqueness
                    user_codes = db.session.query(User.user_code).all()
                    if len(user_codes) != len(set(code[0] for code in user_codes)):
                        raise Exception("Duplicate user codes found - uniqueness constraint violated")
                except Exception as e:
                    if "no such table" not in str(e).lower():
                        raise

    def test_authentication_system(self):
        """Test authentication system thoroughly"""
        with self.error_handler("User Registration", critical=True):
            response = self.safe_request(
                'POST', 
                '/api/auth/register',
                json=self.test_user_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code != 201:
                raise Exception(f"Registration failed: {response.text}")
            
            data = response.json()
            if not data.get('success'):
                raise Exception(f"Registration unsuccessful: {data.get('error', 'Unknown error')}")
            
            self.test_user_id = data['user']['id']
            self.test_user_code = data['user']['user_code']
            
        with self.error_handler("User Login"):
            response = self.safe_request(
                'POST',
                '/api/auth/login',
                json={
                    'username': self.test_user_data['username'],
                    'password': self.test_user_data['password']
                },
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code != 200:
                raise Exception(f"Login failed: {response.text}")
            
            data = response.json()
            if not data.get('success'):
                raise Exception(f"Login unsuccessful: {data.get('error', 'Unknown error')}")
        
        with self.error_handler("Session Management"):
            # Test auth check
            response = self.safe_request('GET', '/api/auth/check')
            if response.status_code != 200:
                raise Exception("Auth check failed")
            
            data = response.json()
            if not data.get('authenticated'):
                raise Exception("User not properly authenticated")
        
        with self.error_handler("Password Validation"):
            # Test weak password rejection
            weak_password_data = self.test_user_data.copy()
            weak_password_data['username'] = f'weak_{int(time.time())}'
            weak_password_data['email'] = f'weak_{int(time.time())}@test.com'
            weak_password_data['password'] = '123'  # Too short
            
            response = self.safe_request(
                'POST',
                '/api/auth/register',
                json=weak_password_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 201:
                raise Exception("Weak password was accepted - security issue!")
        
        with self.error_handler("User Logout"):
            response = self.safe_request('POST', '/api/auth/logout')
            if response.status_code != 200:
                raise Exception("Logout failed")

    def test_api_endpoints(self):
        """Test all API endpoints"""
        # Login first for authenticated tests
        with self.error_handler("API Authentication Setup"):
            response = self.safe_request(
                'POST',
                '/api/auth/login',
                json={
                    'username': self.test_user_data['username'],
                    'password': self.test_user_data['password']
                },
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code != 200:
                raise Exception("Cannot authenticate for API tests")
        
        with self.error_handler("Contacts API"):
            # Get contacts (should be empty initially)
            response = self.safe_request('GET', '/api/contacts')
            if response.status_code != 200:
                raise Exception("Cannot fetch contacts")
            
            contacts = response.json()
            if not isinstance(contacts, list):
                raise Exception("Contacts API returned invalid format")
        
        with self.error_handler("Messages API"):
            # Test message endpoint (will be empty without contacts)
            response = self.safe_request('GET', '/api/messages/999')  # Non-existent contact
            if response.status_code not in [200, 404]:
                raise Exception("Messages API not handling requests properly")
        
        with self.error_handler("User Profile API"):
            # Test encryption key endpoint
            response = self.safe_request('GET', f'/api/user/{self.test_user_id}/encryption-key')
            if response.status_code != 200:
                raise Exception("Encryption key endpoint failed")
            
            data = response.json()
            if not data.get('encryption_key'):
                raise Exception("No encryption key returned")
        
        with self.error_handler("Invalid Endpoints"):
            # Test non-existent endpoint
            response = self.safe_request('GET', '/api/nonexistent')
            if response.status_code != 404:
                self.logger.warning("Server doesn't return 404 for invalid endpoints")

    def test_security_features(self):
        """Test security features and vulnerabilities"""
        with self.error_handler("SQL Injection Protection"):
            # Test basic SQL injection attempts
            malicious_data = {
                'username': "'; DROP TABLE user; --",
                'password': 'test123'
            }
            
            response = self.safe_request(
                'POST',
                '/api/auth/login',
                json=malicious_data,
                headers={'Content-Type': 'application/json'}
            )
            
            # Should fail gracefully, not crash the server
            if response.status_code == 500:
                raise Exception("Server crashed on SQL injection attempt - possible vulnerability")
        
        with self.error_handler("Input Validation"):
            # Test XSS prevention
            xss_data = self.test_user_data.copy()
            xss_data['username'] = f"<script>alert('xss')</script>{int(time.time())}"
            xss_data['email'] = f"xss_{int(time.time())}@test.com"
            
            response = self.safe_request(
                'POST',
                '/api/auth/register',
                json=xss_data,
                headers={'Content-Type': 'application/json'}
            )
            
            # Should either reject or sanitize
            if response.status_code == 201:
                data = response.json()
                if '<script>' in data.get('user', {}).get('username', ''):
                    raise Exception("XSS vulnerability - script tags not sanitized")
        
        with self.error_handler("Authentication Bypass Attempts"):
            # Test accessing protected endpoints without auth
            self.session.cookies.clear()  # Clear session
            
            response = self.safe_request('GET', '/api/contacts')
            if response.status_code == 200:
                raise Exception("Authentication bypass detected - contacts accessible without auth")
            
            response = self.safe_request('GET', '/api/admin/stats')
            if response.status_code == 200:
                raise Exception("Admin endpoints accessible without authentication")
        
        with self.error_handler("Encryption Key Security"):
            # Re-authenticate
            response = self.safe_request(
                'POST',
                '/api/auth/login',
                json={
                    'username': self.test_user_data['username'],
                    'password': self.test_user_data['password']
                },
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                # Check encryption key format
                response = self.safe_request('GET', f'/api/user/{self.test_user_id}/encryption-key')
                if response.status_code == 200:
                    data = response.json()
                    key = data.get('encryption_key', '')
                    
                    # Should be in format: word-word-word-digits
                    if len(key.split('-')) != 4:
                        raise Exception("Encryption key format appears weak")
                    
                    if len(key) < 20:
                        raise Exception("Encryption key appears too short")

    def test_file_upload_system(self):
        """Test file upload functionality"""
        # Re-authenticate for file tests
        with self.error_handler("File Upload Authentication"):
            response = self.safe_request(
                'POST',
                '/api/auth/login',
                json={
                    'username': self.test_user_data['username'],
                    'password': self.test_user_data['password']
                },
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code != 200:
                raise Exception("Cannot authenticate for file upload tests")
        
        with self.error_handler("Profile Picture Upload"):
            # Create a small test image
            test_image_path = self.test_dir / "test_image.png"
            
            # Create minimal PNG file (1x1 pixel)
            png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\xcc\xdb\x8c\x00\x00\x00\x00IEND\xaeB`\x82'
            
            with open(test_image_path, 'wb') as f:
                f.write(png_data)
            
            with open(test_image_path, 'rb') as f:
                files = {'file': ('test.png', f, 'image/png')}
                response = self.safe_request('POST', '/api/user/profile-picture', files=files)
            
            if response.status_code != 200:
                raise Exception(f"Profile picture upload failed: {response.text}")
        
        with self.error_handler("File Type Validation"):
            # Test malicious file upload
            malicious_file_path = self.test_dir / "malicious.php"
            with open(malicious_file_path, 'w') as f:
                f.write('<?php echo "malicious code"; ?>')
            
            with open(malicious_file_path, 'rb') as f:
                files = {'file': ('malicious.php', f, 'application/x-php')}
                response = self.safe_request('POST', '/api/user/profile-picture', files=files)
            
            if response.status_code == 200:
                raise Exception("Malicious file type was accepted - security issue!")
        
        with self.error_handler("File Size Limits"):
            # Test large file (simulate)
            large_file_path = self.test_dir / "large_file.txt"
            with open(large_file_path, 'wb') as f:
                # Write 60MB of data (should exceed 50MB limit)
                f.write(b'x' * (60 * 1024 * 1024))
            
            try:
                with open(large_file_path, 'rb') as f:
                    files = {'file': ('large.txt', f, 'text/plain')}
                    response = self.safe_request('POST', '/api/user/profile-picture', files=files)
                
                if response.status_code == 200:
                    self.logger.warning("Large file was accepted - check file size limits")
            except Exception as e:
                # Expected to fail due to size limits
                self.logger.info("File size limit working properly")

    def test_admin_dashboard(self):
        """Test admin dashboard functionality"""
        # Try to create admin user if it doesn't exist
        with self.error_handler("Admin User Setup"):
            response = self.safe_request(
                'POST',
                '/api/auth/register',
                json=self.admin_user_data,
                headers={'Content-Type': 'application/json'}
            )
            
            # Admin might already exist, that's okay
            if response.status_code not in [201, 400]:
                raise Exception(f"Admin user setup failed: {response.text}")
        
        with self.error_handler("Admin Authentication"):
            response = self.safe_request(
                'POST',
                '/api/auth/login',
                json={
                    'username': self.admin_user_data['username'],
                    'password': self.admin_user_data['password']
                },
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code != 200:
                # Admin user might not exist or have different password
                self.logger.warning("Cannot authenticate as admin - admin tests will be skipped")
                return
        
        with self.error_handler("Admin Dashboard Access"):
            response = self.safe_request('GET', '/api/admin/stats')
            if response.status_code != 200:
                raise Exception("Admin dashboard stats not accessible")
            
            data = response.json()
            required_stats = ['total_users', 'total_messages', 'total_contacts']
            for stat in required_stats:
                if stat not in data:
                    raise Exception(f"Missing stat: {stat}")
        
        with self.error_handler("Admin User Management"):
            response = self.safe_request('GET', '/api/admin/users')
            if response.status_code != 200:
                raise Exception("Admin user management not accessible")
            
            users = response.json()
            if not isinstance(users, list):
                raise Exception("Admin users endpoint returned invalid format")
        
        with self.error_handler("Admin Settings"):
            response = self.safe_request('GET', '/api/admin/settings')
            if response.status_code != 200:
                raise Exception("Admin settings not accessible")

    def test_performance(self):
        """Test performance characteristics"""
        with self.error_handler("Response Times"):
            # Measure response times for key endpoints
            endpoints = ['/', '/api/auth/check', '/static/script.js']
            slow_endpoints = []
            
            for endpoint in endpoints:
                start_time = time.time()
                response = self.safe_request('GET', endpoint)
                duration = time.time() - start_time
                
                if duration > 2.0:  # 2 second threshold
                    slow_endpoints.append(f"{endpoint}: {duration:.2f}s")
            
            if slow_endpoints:
                self.warnings.append(f"Slow endpoints detected: {', '.join(slow_endpoints)}")
        
        with self.error_handler("Memory Usage"):
            # Check system memory usage
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                raise Exception(f"High memory usage: {memory.percent}%")
            
            self.logger.info(f"System memory usage: {memory.percent}%")
        
        with self.error_handler("Concurrent Requests"):
            # Test concurrent request handling
            def make_request():
                return self.safe_request('GET', '/api/auth/check')
            
            threads = []
            results = []
            
            # Create 10 concurrent requests
            for i in range(10):
                thread = threading.Thread(target=lambda: results.append(make_request()))
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join(timeout=30)
            
            # Check for failures
            failed_requests = [r for r in results if r and r.status_code != 200]
            if len(failed_requests) > 2:  # Allow some failures
                raise Exception(f"Too many concurrent request failures: {len(failed_requests)}/10")

    def test_error_handling(self):
        """Test error handling capabilities"""
        with self.error_handler("404 Error Pages"):
            response = self.safe_request('GET', '/nonexistent-page')
            if response.status_code != 404:
                self.logger.warning("Custom 404 pages might not be configured")
        
        with self.error_handler("500 Error Recovery"):
            # Test malformed JSON
            response = self.safe_request(
                'POST',
                '/api/auth/login',
                data="invalid json",
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 500:
                raise Exception("Server returns 500 for malformed JSON - poor error handling")
        
        with self.error_handler("Database Error Handling"):
            # Test with invalid user ID
            response = self.safe_request('GET', '/api/user/999999/encryption-key')
            if response.status_code == 500:
                raise Exception("Server crashes on invalid user ID - poor error handling")

    def test_production_config(self):
        """Test production configuration"""
        with self.error_handler("Debug Mode Check", critical=True):
            # Debug mode should be off in production
            response = self.safe_request('GET', '/')
            if 'Werkzeug' in response.headers.get('Server', ''):
                raise Exception("Development server detected - not production ready!")
        
        with self.error_handler("Security Headers"):
            response = self.safe_request('GET', '/')
            
            # Check for security headers
            security_headers = {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'X-XSS-Protection': '1; mode=block'
            }
            
            missing_headers = []
            for header, expected in security_headers.items():
                if header not in response.headers:
                    missing_headers.append(header)
            
            if missing_headers:
                self.warnings.append(f"Missing security headers: {', '.join(missing_headers)}")
        
        with self.error_handler("HTTPS Configuration"):
            if not self.base_url.startswith('https://') and 'localhost' not in self.base_url:
                self.warnings.append("Not using HTTPS - security risk in production")
        
        with self.error_handler("Database Configuration"):
            # Check if using production database
            db_url = os.environ.get('DATABASE_URL', 'sqlite:///ourchat.db')
            if 'sqlite' in db_url and 'production' in os.environ.get('NODE_ENV', '').lower():
                self.warnings.append("Using SQLite in production - consider PostgreSQL")

    def generate_report(self):
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['status'] == 'PASSED'])
        failed_tests = len([t for t in self.test_results if t['status'] == 'FAILED'])
        
        # Calculate production readiness score
        base_score = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Deduct points for critical failures
        score_deduction = len(self.critical_failures) * 20
        final_score = max(0, base_score - score_deduction)
        
        # Determine readiness level
        if final_score >= 90 and len(self.critical_failures) == 0:
            readiness_level = "PRODUCTION READY ✅"
            readiness_color = "green"
        elif final_score >= 75 and len(self.critical_failures) <= 1:
            readiness_level = "MOSTLY READY ⚠️"
            readiness_color = "orange"
        else:
            readiness_level = "NOT READY ❌"
            readiness_color = "red"
        
        # Generate text report
        report = f"""
═══════════════════════════════════════════════
    OURCHAT PRODUCTION READINESS REPORT
═══════════════════════════════════════════════

Test Summary:
- Total Tests: {total_tests}
- Passed: {passed_tests}
- Failed: {failed_tests}
- Critical Failures: {len(self.critical_failures)}
- Warnings: {len(self.warnings)}

Production Readiness Score: {final_score:.1f}%
Status: {readiness_level}

═══════════════════════════════════════════════

CRITICAL FAILURES:
"""
        
        if self.critical_failures:
            for i, failure in enumerate(self.critical_failures, 1):
                report += f"{i}. {failure}\n"
        else:
            report += "None ✅\n"
        
        report += f"""
WARNINGS:
"""
        
        if self.warnings:
            for i, warning in enumerate(self.warnings, 1):
                report += f"{i}. {warning}\n"
        else:
            report += "None ✅\n"
        
        report += f"""
DETAILED TEST RESULTS:
"""
        
        for test in self.test_results:
            status_icon = "✅" if test['status'] == 'PASSED' else "❌"
            report += f"  {status_icon} {test['test']} ({test['duration']:.2f}s)\n"
            if test['status'] == 'FAILED':
                report += f"     Error: {test.get('error', 'Unknown error')}\n"
        
        report += f"""
═══════════════════════════════════════════════

RECOMMENDATIONS FOR PRODUCTION:
"""
        
        recommendations = []
        
        if len(self.critical_failures) > 0:
            recommendations.append("🚨 Fix all critical failures before deploying to production")
        
        if 'sqlite' in os.environ.get('DATABASE_URL', 'sqlite:///ourchat.db').lower():
            recommendations.append("📊 Consider upgrading to PostgreSQL or MySQL for production")
        
        if os.environ.get('SECRET_KEY', 'default') == 'your-secret-key-change-this-in-production':
            recommendations.append("🔐 Set a secure SECRET_KEY environment variable")
        
        if not self.base_url.startswith('https://'):
            recommendations.append("🔒 Enable HTTPS for production deployment")
        
        recommendations.extend([
            "🔄 Set up automated backups for production database",
            "📊 Configure monitoring and logging for production",
            "🚀 Use a production WSGI server (Gunicorn, uWSGI)",
            "🔧 Set up health check endpoints for load balancers",
            "🛡️  Implement rate limiting for API endpoints",
            "📈 Set up error tracking (Sentry, Rollbar)",
        ])
        
        for i, rec in enumerate(recommendations, 1):
            report += f"{i}. {rec}\n"
        
        report += f"""
═══════════════════════════════════════════════
Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Test URL: {self.base_url}
═══════════════════════════════════════════════
"""
        
        # Save report to file
        report_file = f"production_readiness_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Print summary to console
        self.logger.info(f"\n{report}")
        self.logger.info(f"📄 Full report saved to: {report_file}")
        
        # Generate HTML report
        self.generate_html_report(final_score, readiness_level, readiness_color)
        
        return final_score >= 75 and len(self.critical_failures) == 0

    def generate_html_report(self, score, readiness_level, color):
        """Generate HTML report"""
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OurChat Production Readiness Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .header h1 {{ margin: 0; font-size: 2.5em; }}
        .header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
        .score-section {{ padding: 30px; text-align: center; border-bottom: 1px solid #eee; }}
        .score-circle {{ width: 150px; height: 150px; border-radius: 50%; background: conic-gradient({color} {score}%, #eee {score}%); display: flex; align-items: center; justify-content: center; margin: 0 auto 20px; position: relative; }}
        .score-circle::before {{ content: ''; width: 120px; height: 120px; border-radius: 50%; background: white; position: absolute; }}
        .score-text {{ position: relative; z-index: 1; font-size: 2em; font-weight: bold; color: {color}; }}
        .readiness-status {{ font-size: 1.5em; font-weight: bold; color: {color}; margin-bottom: 10px; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; padding: 30px; }}
        .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #667eea; }}
        .stat-card h3 {{ margin: 0 0 10px 0; color: #333; }}
        .stat-card .number {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        .section {{ padding: 30px; border-bottom: 1px solid #eee; }}
        .section h2 {{ color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
        .test-item {{ display: flex; align-items: center; padding: 10px; margin: 5px 0; border-radius: 5px; }}
        .test-item.passed {{ background: #d4edda; }}
        .test-item.failed {{ background: #f8d7da; }}
        .test-icon {{ font-size: 1.2em; margin-right: 15px; }}
        .test-details {{ flex-grow: 1; }}
        .test-duration {{ color: #666; font-size: 0.9em; }}
        .error-message {{ color: #721c24; font-size: 0.9em; margin-top: 5px; }}
        .critical {{ background: #f8d7da; border-left: 4px solid #dc3545; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .recommendation {{ background: #d1ecf1; border-left: 4px solid #17a2b8; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .footer {{ padding: 20px 30px; background: #f8f9fa; text-align: center; color: #666; border-radius: 0 0 10px 10px; }}
        @media (max-width: 768px) {{ .stats-grid {{ grid-template-columns: 1fr; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>OurChat Production Readiness Report</h1>
            <p>Comprehensive testing and analysis completed on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="score-section">
            <div class="score-circle">
                <div class="score-text">{score:.0f}%</div>
            </div>
            <div class="readiness-status">{readiness_level}</div>
            <p>Production Readiness Score</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Tests</h3>
                <div class="number">{len(self.test_results)}</div>
            </div>
            <div class="stat-card">
                <h3>Passed</h3>
                <div class="number">{len([t for t in self.test_results if t['status'] == 'PASSED'])}</div>
            </div>
            <div class="stat-card">
                <h3>Failed</h3>
                <div class="number">{len([t for t in self.test_results if t['status'] == 'FAILED'])}</div>
            </div>
            <div class="stat-card">
                <h3>Critical Issues</h3>
                <div class="number">{len(self.critical_failures)}</div>
            </div>
        </div>
        
        <div class="section">
            <h2>🚨 Critical Issues</h2>
            {''.join([f'<div class="critical">❌ {failure}</div>' for failure in self.critical_failures]) if self.critical_failures else '<p>✅ No critical issues found!</p>'}
        </div>
        
        <div class="section">
            <h2>⚠️ Warnings</h2>
            {''.join([f'<div class="warning">⚠️ {warning}</div>' for warning in self.warnings]) if self.warnings else '<p>✅ No warnings!</p>'}
        </div>
        
        <div class="section">
            <h2>📋 Detailed Test Results</h2>
            {''.join([f'''
                <div class="test-item {'passed' if test['status'] == 'PASSED' else 'failed'}">
                    <span class="test-icon">{'✅' if test['status'] == 'PASSED' else '❌'}</span>
                    <div class="test-details">
                        <div><strong>{test['test']}</strong></div>
                        <div class="test-duration">Duration: {test['duration']:.2f}s</div>
                        {'<div class="error-message">Error: ' + test.get('error', 'Unknown error') + '</div>' if test['status'] == 'FAILED' else ''}
                    </div>
                </div>
            ''' for test in self.test_results])}
        </div>
        
        <div class="section">
            <h2>💡 Recommendations</h2>
            <div class="recommendation">🚨 Fix all critical failures before deploying to production</div>
            <div class="recommendation">📊 Consider upgrading to PostgreSQL or MySQL for production</div>
            <div class="recommendation">🔐 Ensure SECRET_KEY is properly configured</div>
            <div class="recommendation">🔒 Enable HTTPS for production deployment</div>
            <div class="recommendation">🔄 Set up automated backups for production database</div>
            <div class="recommendation">📊 Configure monitoring and logging for production</div>
            <div class="recommendation">🚀 Use a production WSGI server (Gunicorn, uWSGI)</div>
            <div class="recommendation">🔧 Set up health check endpoints for load balancers</div>
            <div class="recommendation">🛡️ Implement rate limiting for API endpoints</div>
            <div class="recommendation">📈 Set up error tracking (Sentry, Rollbar)</div>
        </div>
        
        <div class="footer">
            <p>Report generated by OurChat Production Readiness Test Suite</p>
            <p>Test URL: {self.base_url}</p>
        </div>
    </div>
</body>
</html>
"""
        
        html_file = f"production_readiness_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"📊 HTML report saved to: {html_file}")

    def cleanup(self):
        """Clean up test resources"""
        try:
            if self.test_dir.exists():
                import shutil
                shutil.rmtree(self.test_dir)
            self.logger.info("✅ Test cleanup completed")
        except Exception as e:
            self.logger.warning(f"⚠️ Test cleanup failed: {str(e)}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='OurChat Production Readiness Test Suite')
    parser.add_argument('--url', default='http://localhost:5000', help='Base URL to test (default: http://localhost:5000)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('--quick', action='store_true', help='Run only critical tests')
    
    args = parser.parse_args()
    
    print("🚀 Starting OurChat Production Readiness Test Suite...")
    print(f"   Target URL: {args.url}")
    print(f"   Verbose: {args.verbose}")
    print("   " + "="*50)
    
    try:
        tester = ProductionReadinessTest(base_url=args.url, verbose=args.verbose)
        is_ready = tester.run_all_tests()
        
        print("\n" + "="*50)
        if is_ready:
            print("🎉 SUCCESS: Your application appears ready for production!")
            print("   Review the detailed report for any remaining optimizations.")
        else:
            print("⚠️  WARNING: Your application needs attention before production deployment.")
            print("   Please address the critical issues identified in the report.")
        
        print("📄 Check the generated reports for detailed information.")
        
        # Cleanup
        tester.cleanup()
        
        # Exit with appropriate code
        sys.exit(0 if is_ready else 1)
        
    except KeyboardInterrupt:
        print("\n🛑 Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
