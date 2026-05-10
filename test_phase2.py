#!/usr/bin/env python
"""
Test script for Phase 2 Dashboard implementation
Tests all dashboard API endpoints and functionality
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = 'http://localhost:5000'
API_BASE = f'{BASE_URL}/api/dashboard'

# Test user credentials
TEST_USER = {
    'username': 'testuser123',
    'email': 'testuser@test.com',
    'password': 'TestPassword123!',
    'confirm_password': 'TestPassword123!'
}

session = requests.Session()

def test_signup():
    """Test user signup"""
    print("\n" + "="*60)
    print("TEST 1: User Signup")
    print("="*60)
    
    data = {
        'username': TEST_USER['username'],
        'email': TEST_USER['email'],
        'password': TEST_USER['password'],
        'confirm_password': TEST_USER['confirm_password']
    }
    
    response = session.post(f'{BASE_URL}/auth/signup', data=data)
    
    if response.status_code in [200, 302]:  # 302 is redirect
        print("✅ Signup successful!")
        return True
    else:
        print(f"❌ Signup failed: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def test_login():
    """Test user login"""
    print("\n" + "="*60)
    print("TEST 2: User Login")
    print("="*60)
    
    data = {
        'email': TEST_USER['email'],
        'password': TEST_USER['password']
    }
    
    response = session.post(f'{BASE_URL}/auth/login', data=data)
    
    if response.status_code in [200, 302]:  # 302 is redirect
        print("✅ Login successful!")
        return True
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def test_get_profile():
    """Test getting user profile"""
    print("\n" + "="*60)
    print("TEST 3: Get User Profile")
    print("="*60)
    
    response = session.get(f'{API_BASE}/profile')
    
    if response.status_code == 200:
        print("✅ Profile retrieved successfully!")
        print(json.dumps(response.json(), indent=2))
        return True
    else:
        print(f"❌ Failed to get profile: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def test_get_stats():
    """Test getting dashboard stats"""
    print("\n" + "="*60)
    print("TEST 4: Get Dashboard Stats")
    print("="*60)
    
    response = session.get(f'{API_BASE}/stats')
    
    if response.status_code == 200:
        print("✅ Stats retrieved successfully!")
        stats = response.json()
        print(f"Total Trips: {stats['total_trips']}")
        print(f"Active Trips: {stats['active_trips']}")
        print(f"Total Budget: ₹{stats['total_budget']}")
        print(f"Average Budget: ₹{stats['average_trip_budget']}")
        return True
    else:
        print(f"❌ Failed to get stats: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def test_create_trip():
    """Test creating a trip"""
    print("\n" + "="*60)
    print("TEST 5: Create a Trip")
    print("="*60)
    
    start_date = datetime.now().date()
    end_date = start_date + timedelta(days=7)
    
    trip_data = {
        'title': 'Summer Vacation to Paris',
        'destination': 'Paris, France',
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'budget': 5000.00,
        'description': 'A wonderful trip to explore the City of Light'
    }
    
    response = session.post(
        f'{API_BASE}/trips',
        json=trip_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 201:
        print("✅ Trip created successfully!")
        trip = response.json()
        print(json.dumps(trip, indent=2))
        return trip['id']
    else:
        print(f"❌ Failed to create trip: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def test_get_trips():
    """Test getting all trips"""
    print("\n" + "="*60)
    print("TEST 6: Get All Trips")
    print("="*60)
    
    response = session.get(f'{API_BASE}/trips')
    
    if response.status_code == 200:
        print("✅ Trips retrieved successfully!")
        data = response.json()
        print(f"Total trips: {data['total']}")
        print(f"Trips in response: {len(data['trips'])}")
        if data['trips']:
            print(json.dumps(data['trips'][0], indent=2))
        return True
    else:
        print(f"❌ Failed to get trips: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def test_get_active_trips():
    """Test getting active trips"""
    print("\n" + "="*60)
    print("TEST 7: Get Active Trips")
    print("="*60)
    
    response = session.get(f'{API_BASE}/active-trips')
    
    if response.status_code == 200:
        print("✅ Active trips retrieved successfully!")
        data = response.json()
        print(f"Active trips: {len(data['trips'])}")
        return True
    else:
        print(f"❌ Failed to get active trips: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def test_update_trip(trip_id):
    """Test updating a trip"""
    print("\n" + "="*60)
    print("TEST 8: Update a Trip")
    print("="*60)
    
    if not trip_id:
        print("❌ No trip ID provided, skipping test")
        return False
    
    update_data = {
        'title': 'Summer Vacation to Paris (Updated)',
        'budget': 6000.00,
        'description': 'Updated trip description'
    }
    
    response = session.put(
        f'{API_BASE}/trips/{trip_id}',
        json=update_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        print("✅ Trip updated successfully!")
        trip = response.json()
        print(f"Updated title: {trip['title']}")
        print(f"Updated budget: ₹{trip['budget']}")
        return True
    else:
        print(f"❌ Failed to update trip: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def main():
    """Run all tests"""
    print("\n" + "#"*60)
    print("# TRAVELOOP PHASE 2 DASHBOARD API TESTS")
    print("#"*60)
    
    # Run tests in order
    if not test_signup():
        print("\n❌ Cannot proceed: Signup failed")
        return
    
    if not test_login():
        print("\n❌ Cannot proceed: Login failed")
        return
    
    test_get_profile()
    test_get_stats()
    
    trip_id = test_create_trip()
    
    test_get_trips()
    test_get_active_trips()
    test_update_trip(trip_id)
    
    print("\n" + "#"*60)
    print("# ALL TESTS COMPLETED")
    print("#"*60 + "\n")

if __name__ == '__main__':
    main()
