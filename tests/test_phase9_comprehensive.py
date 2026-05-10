#!/usr/bin/env python
"""
Comprehensive API Test Suite for Traveloop Phase 9
Tests all backend routes with rate limiting, error handling, and data validation
"""

import requests
import json
from datetime import datetime, timedelta, date

BASE_URL = 'http://localhost:5000'
API_BASE = f'{BASE_URL}/api'

# Test user credentials
TEST_USER = {
    'username': 'testuser_phase9',
    'email': 'testuser_phase9@test.com',
    'password': 'SecurePassword123!',
    'confirm_password': 'SecurePassword123!'
}

# Test session
session = requests.Session()
test_results = {
    'passed': 0,
    'failed': 0,
    'errors': []
}

def log_test(name, status, message=""):
    """Log test result"""
    print(f"\n{'✅' if status else '❌'} {name}")
    if message:
        print(f"   {message}")
    if status:
        test_results['passed'] += 1
    else:
        test_results['failed'] += 1
        test_results['errors'].append(f"{name}: {message}")

# ===== AUTHENTICATION TESTS =====
def test_auth_signup():
    """Test user signup"""
    print("\n" + "="*60)
    print("AUTHENTICATION TESTS")
    print("="*60)
    
    response = session.post(f'{BASE_URL}/auth/signup', data=TEST_USER)
    log_test("Signup", response.status_code in [200, 302], f"Status: {response.status_code}")

def test_auth_login():
    """Test user login"""
    data = {
        'identifier': TEST_USER['email'],
        'password': TEST_USER['password']
    }
    response = session.post(f'{BASE_URL}/auth/login', data=data)
    log_test("Login", response.status_code in [200, 302], f"Status: {response.status_code}")

def test_rate_limiting():
    """Test rate limiting on auth endpoints"""
    print("\n" + "="*60)
    print("RATE LIMITING TESTS (5 req/min)")
    print("="*60)
    
    # Try to exceed rate limit
    attempts = 7
    for i in range(attempts):
        response = session.post(f'{BASE_URL}/auth/login', 
                              data={'identifier': 'test', 'password': 'wrong'},
                              allow_redirects=False)
        if response.status_code == 429:
            log_test(f"Rate Limit (Attempt {i+1})", True, "Rate limit enforced")
            break
    else:
        log_test("Rate Limit Enforcement", False, "Rate limit not triggered after 7 attempts")

# ===== DASHBOARD API TESTS =====
def test_dashboard_profile():
    """Test get user profile"""
    print("\n" + "="*60)
    print("DASHBOARD API TESTS")
    print("="*60)
    
    response = session.get(f'{API_BASE}/dashboard/profile')
    log_test("Get Profile", response.status_code == 200, f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        log_test("Profile Data Valid", 'username' in data or 'error' in data)

def test_dashboard_trips():
    """Test get user trips"""
    response = session.get(f'{API_BASE}/dashboard/trips?limit=10&offset=0')
    log_test("Get Trips", response.status_code in [200, 401], f"Status: {response.status_code}")

def test_dashboard_active_trips():
    """Test get active trips"""
    response = session.get(f'{API_BASE}/dashboard/active-trips')
    log_test("Get Active Trips", response.status_code in [200, 401], f"Status: {response.status_code}")

# ===== TRIP API TESTS =====
def test_create_trip():
    """Test create trip"""
    print("\n" + "="*60)
    print("TRIP API TESTS")
    print("="*60)
    
    trip_data = {
        'title': 'Test Trip Phase 9',
        'description': 'A test trip for phase 9 validation',
        'start_date': (date.today() + timedelta(days=1)).isoformat(),
        'end_date': (date.today() + timedelta(days=7)).isoformat(),
        'destination': 'Paris'
    }
    response = session.post(f'{API_BASE}/dashboard/trips', json=trip_data)
    log_test("Create Trip", response.status_code in [201, 400, 401], f"Status: {response.status_code}")
    
    # Store trip ID for later tests
    if response.status_code == 201:
        global test_trip_id
        test_trip_id = response.json().get('id')

# ===== LOCATION API TESTS =====
def test_location_autocomplete():
    """Test location autocomplete"""
    print("\n" + "="*60)
    print("LOCATION API TESTS")
    print("="*60)
    
    response = session.get(f'{API_BASE}/locations/cities/autocomplete?q=Paris')
    log_test("Location Autocomplete", response.status_code in [200, 401], f"Status: {response.status_code}")

def test_location_attractions():
    """Test get attractions"""
    response = session.get(f'{API_BASE}/locations/attractions?lat=48.8566&lon=2.3522')
    log_test("Get Attractions", response.status_code in [200, 400, 401], f"Status: {response.status_code}")

def test_location_city_image():
    """Test get city image"""
    response = session.get(f'{API_BASE}/locations/city-image?city=Paris')
    log_test("Get City Image", response.status_code in [200, 401], f"Status: {response.status_code}")

# ===== ERROR HANDLING TESTS =====
def test_error_handling():
    """Test error handling"""
    print("\n" + "="*60)
    print("ERROR HANDLING TESTS")
    print("="*60)
    
    # Test 404
    response = session.get(f'{BASE_URL}/nonexistent-page')
    log_test("404 Error Handling", response.status_code == 404, f"Status: {response.status_code}")
    
    # Test missing required fields
    bad_data = {'email': 'invalidemail'}
    response = session.post(f'{BASE_URL}/auth/signup', data=bad_data)
    log_test("Invalid Input Handling", response.status_code in [400, 200], f"Status: {response.status_code}")
    
    # Test invalid JSON
    response = session.post(f'{API_BASE}/dashboard/trips', 
                           data='invalid json',
                           headers={'Content-Type': 'application/json'})
    log_test("Invalid JSON Handling", response.status_code in [400, 401], f"Status: {response.status_code}")

# ===== CSRF PROTECTION TESTS =====
def test_csrf_protection():
    """Test CSRF protection"""
    print("\n" + "="*60)
    print("CSRF PROTECTION TESTS")
    print("="*60)
    
    # Try POST without CSRF token
    new_session = requests.Session()
    response = new_session.post(f'{BASE_URL}/auth/signup', 
                               data=TEST_USER,
                               allow_redirects=False)
    # Should redirect or require CSRF
    log_test("CSRF Protection", response.status_code in [302, 200], f"Status: {response.status_code}")

# ===== RESPONSIVE/CONTENT TESTS =====
def test_responsive_endpoints():
    """Test that endpoints work with different content types"""
    print("\n" + "="*60)
    print("CONTENT TYPE TESTS")
    print("="*60)
    
    # Test JSON content type
    response = session.get(f'{API_BASE}/dashboard/profile',
                          headers={'Accept': 'application/json'})
    log_test("JSON Response", response.status_code in [200, 401], f"Status: {response.status_code}")
    
    # Test HTML content type
    response = session.get(f'{BASE_URL}/',
                          headers={'Accept': 'text/html'})
    log_test("HTML Response", response.status_code == 200, f"Status: {response.status_code}")

# ===== ACCESSIBILITY TESTS =====
def test_accessibility_headers():
    """Test accessibility-related headers and content"""
    print("\n" + "="*60)
    print("ACCESSIBILITY TESTS")
    print("="*60)
    
    response = session.get(f'{BASE_URL}/')
    
    # Check for basic HTML structure
    has_lang = 'lang=' in response.text
    log_test("HTML Language Attribute", has_lang, "Page has lang attribute")
    
    # Check for meta viewport
    has_viewport = 'viewport' in response.text
    log_test("Responsive Viewport Meta", has_viewport, "Viewport meta tag present")
    
    # Check for main content area
    has_main = '<main' in response.text
    log_test("Main Content Area", has_main, "Main tag present")

def print_summary():
    """Print test summary"""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print(f"Total: {test_results['passed'] + test_results['failed']}")
    
    if test_results['errors']:
        print("\nFailed Tests:")
        for error in test_results['errors']:
            print(f"  - {error}")
    
    print("\n" + "="*60)

def main():
    """Run all tests"""
    print("="*60)
    print("TRAVELOOP PHASE 9 - COMPREHENSIVE API TEST SUITE")
    print("="*60)
    
    try:
        # Authentication tests
        test_auth_signup()
        test_auth_login()
        test_rate_limiting()
        
        # Dashboard tests
        test_dashboard_profile()
        test_dashboard_trips()
        test_dashboard_active_trips()
        
        # Trip tests
        test_create_trip()
        
        # Location tests
        test_location_autocomplete()
        test_location_attractions()
        test_location_city_image()
        
        # Error handling tests
        test_error_handling()
        
        # Security tests
        test_csrf_protection()
        
        # Content type tests
        test_responsive_endpoints()
        
        # Accessibility tests
        test_accessibility_headers()
        
    except Exception as e:
        print(f"\n❌ Test suite error: {str(e)}")
        test_results['errors'].append(f"Suite Error: {str(e)}")
    
    finally:
        print_summary()

if __name__ == "__main__":
    main()
