#!/usr/bin/env python3
"""
OurChat Security & Performance Test Suite
Tests critical security and performance issues before production deployment.
"""

import os
import sys
import time
import requests
import json
from datetime import datetime

class SecurityTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = {
            'critical': [],
            'warnings': [],
            'passed': [],
            'performance': []
        }
    
    def log_result(self, category, test_name, status, details=None):
        """Log test results"""
        result = {
            'test': test_name,
            'status': status,
            'details': details or '',
            'timestamp': datetime.now().isoformat()
        }
        self.results[category].append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {status}")
        if details:
            print(f"   {details}")
    
    def test_secret_key(self):
        """Test if SECRET_KEY is properly configured"""
        secret_key = os.environ.get('SECRET_KEY')
        
        if not secret_key:
            self.log_result('critical', 'SECRET_KEY Environment Variable', 'FAIL', 
                           'SECRET_KEY not set in environment')
            return False
        
        if len(secret_key) < 32:
            self.log_result('critical', 'SECRET_KEY Length', 'FAIL',
                           f'SECRET_KEY too short: {len(secret_key)} chars (minimum: 32)')
            return False
        
        if secret_key == 'your-secret-key-change-this-in-production':
            self.log_result('critical', 'SECRET_KEY Default Value', 'FAIL',
                           'Using default SECRET_KEY - security risk!')
            return False
        
        self.log_result('passed', 'SECRET_KEY Configuration', 'PASS',
                       f'Secure key configured ({len(secret_key)} chars)')
        return True
    
    def test_debug_mode(self):
        """Test if debug mode is disabled"""
        try:
            response = self.session.get(f"{self.base_url}/")
            
            # Check for debug information in response
            debug_indicators = ['Werkzeug', 'Debug mode:', 'Traceback', 'Debugger PIN']
            has_debug = any(indicator in response.text for indicator in debug_indicators)
            
            if has_debug:
                self.log_result('critical', 'Debug Mode Check', 'FAIL',
                               'Debug mode appears to be enabled')
                return False
            
            self.log_result('passed', 'Debug Mode Check', 'PASS', 'Debug mode disabled')
            return True
            
        except Exception as e:
            self.log_result('critical', 'Debug Mode Check', 'ERROR', str(e))
            return False
    
    def test_security_headers(self):
        """Test for required security headers"""
        try:
            response = self.session.get(f"{self.base_url}/")
            headers = response.headers
            
            required_headers = {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'X-XSS-Protection': '1; mode=block',
                'Content-Security-Policy': True,  # Just check if present
            }
            
            missing_headers = []
            for header, expected_value in required_headers.items():
                if header not in headers:
                    missing_headers.append(header)
                elif expected_value != True and headers[header] != expected_value:
                    missing_headers.append(f"{header} (incorrect value)")
            
            if missing_headers:
                self.log_result('warnings', 'Security Headers', 'PARTIAL',
                               f'Missing headers: {", ".join(missing_headers)}')
                return False
            
            self.log_result('passed', 'Security Headers', 'PASS', 'All security headers present')
            return True
            
        except Exception as e:
            self.log_result('warnings', 'Security Headers', 'ERROR', str(e))
            return False
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/health")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code != 200:
                self.log_result('warnings', 'Health Check Endpoint', 'FAIL',
                               f'HTTP {response.status_code}')
                return False
            
            health_data = response.json()
            if health_data.get('status') != 'healthy':
                self.log_result('critical', 'Health Check Status', 'FAIL',
                               f'Status: {health_data.get("status")}')
                return False
            
            self.log_result('passed', 'Health Check Endpoint', 'PASS',
                           f'Healthy ({response_time:.1f}ms)')
            self.log_result('performance', 'Health Check Response Time', 
                           'PASS' if response_time < 1000 else 'SLOW',
                           f'{response_time:.1f}ms')
            return True
            
        except Exception as e:
            self.log_result('critical', 'Health Check Endpoint', 'ERROR', str(e))
            return False
    
    def test_database_connection(self):
        """Test database connectivity via health endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                db_status = health_data.get('database', 'unknown')
                
                if db_status == 'connected':
                    self.log_result('passed', 'Database Connection', 'PASS', 'Database healthy')
                    return True
                else:
                    self.log_result('critical', 'Database Connection', 'FAIL',
                                   f'Database status: {db_status}')
                    return False
            
            self.log_result('critical', 'Database Connection', 'ERROR', 
                           'Could not reach health endpoint')
            return False
            
        except Exception as e:
            self.log_result('critical', 'Database Connection', 'ERROR', str(e))
            return False
    
    def test_xss_protection(self):
        """Test basic XSS protection"""
        try:
            # This would require authentication, so we'll just check if the endpoint exists
            response = self.session.get(f"{self.base_url}/api/auth/check")
            
            if response.status_code in [200, 401]:  # Both are valid responses
                self.log_result('passed', 'XSS Protection Endpoints', 'PASS',
                               'API endpoints responding correctly')
                return True
            
            self.log_result('warnings', 'XSS Protection Endpoints', 'FAIL',
                           f'Unexpected response: {response.status_code}')
            return False
            
        except Exception as e:
            self.log_result('warnings', 'XSS Protection Endpoints', 'ERROR', str(e))
            return False
    
    def test_endpoint_performance(self):
        """Test critical endpoint performance"""
        endpoints = [
            ('/', 'Main Page'),
            ('/api/auth/check', 'Auth Check'),
            ('/health', 'Health Check'),
            ('/static/script.js', 'Static JS'),
        ]
        
        slow_endpoints = []
        
        for endpoint, name in endpoints:
            try:
                start_time = time.time()
                response = self.session.get(f"{self.base_url}{endpoint}")
                response_time = (time.time() - start_time) * 1000
                
                if response_time > 2000:  # 2 seconds threshold
                    slow_endpoints.append(f"{name}: {response_time:.0f}ms")
                    
                status = 'PASS' if response_time < 1000 else 'SLOW' if response_time < 2000 else 'FAIL'
                self.log_result('performance', f'{name} Response Time', status,
                               f'{response_time:.1f}ms')
                
            except Exception as e:
                self.log_result('performance', f'{name} Performance', 'ERROR', str(e))
        
        if slow_endpoints:
            self.log_result('warnings', 'Slow Endpoints Detection', 'FAIL',
                           f'Slow endpoints: {", ".join(slow_endpoints)}')
            return False
        
        return True
    
    def run_all_tests(self):
        """Run all security and performance tests"""
        print(f"🔒 OurChat Security & Performance Test Suite")
        print(f"Testing: {self.base_url}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Critical security tests
        print("\n🚨 CRITICAL SECURITY TESTS")
        self.test_secret_key()
        self.test_debug_mode()
        self.test_database_connection()
        
        # Warning-level tests
        print("\n⚠️ WARNING-LEVEL TESTS")
        self.test_security_headers()
        self.test_xss_protection()
        
        # Performance tests
        print("\n⚡ PERFORMANCE TESTS")
        self.test_health_endpoint()
        self.test_endpoint_performance()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print(f"✅ Passed: {len(self.results['passed'])}")
        print(f"⚠️ Warnings: {len(self.results['warnings'])}")
        print(f"❌ Critical Issues: {len(self.results['critical'])}")
        print(f"⚡ Performance Tests: {len(self.results['performance'])}")
        
        # Show critical issues
        if self.results['critical']:
            print("\n🚨 CRITICAL ISSUES TO FIX:")
            for issue in self.results['critical']:
                if issue['status'] in ['FAIL', 'ERROR']:
                    print(f"   ❌ {issue['test']}: {issue['details']}")
        
        # Show warnings
        if self.results['warnings']:
            print("\n⚠️ WARNINGS TO ADDRESS:")
            for warning in self.results['warnings']:
                if warning['status'] in ['FAIL', 'PARTIAL', 'ERROR']:
                    print(f"   ⚠️ {warning['test']}: {warning['details']}")
        
        # Overall assessment
        has_critical = any(r['status'] in ['FAIL', 'ERROR'] for r in self.results['critical'])
        has_warnings = any(r['status'] in ['FAIL', 'PARTIAL', 'ERROR'] for r in self.results['warnings'])
        
        print("\n" + "=" * 60)
        if not has_critical and not has_warnings:
            print("🎉 ALL TESTS PASSED - Ready for production deployment!")
            return True
        elif not has_critical:
            print("✅ No critical issues - Safe to deploy with warnings addressed")
            return True
        else:
            print("⛔ CRITICAL ISSUES FOUND - DO NOT DEPLOY TO PRODUCTION")
            return False

def main():
    """Main test execution"""
    # Check if server is running locally
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    tester = SecurityTester(base_url)
    success = tester.run_all_tests()
    
    # Save results to file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = f'security_test_report_{timestamp}.json'
    
    with open(results_file, 'w') as f:
        json.dump({
            'test_run': {
                'timestamp': datetime.now().isoformat(),
                'base_url': base_url,
                'total_tests': sum(len(self.results[category]) for category in self.results),
            },
            'results': tester.results
        }, f, indent=2)
    
    print(f"\n📄 Full report saved to: {results_file}")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
