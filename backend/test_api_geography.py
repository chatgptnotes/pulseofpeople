"""
Test script for Ward and Polling Booth APIs
Run this script to test all geography endpoints
"""

import requests
import json
import os

# Configuration
BASE_URL = "http://localhost:8000/api"
GEOGRAPHY_URL = f"{BASE_URL}/geography"

# Replace with your actual credentials
USERNAME = "admin@example.com"
PASSWORD = "your-password"


def get_auth_token():
    """Obtain JWT authentication token"""
    response = requests.post(
        f"{BASE_URL}/auth/login/",
        json={"email": USERNAME, "password": PASSWORD}
    )

    if response.status_code == 200:
        data = response.json()
        return data['access']
    else:
        print(f"Login failed: {response.status_code}")
        print(response.text)
        return None


def test_ward_list(token):
    """Test GET /geography/wards/"""
    print("\n=== TEST: List Wards ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{GEOGRAPHY_URL}/wards/", headers=headers)

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_ward_create(token):
    """Test POST /geography/wards/"""
    print("\n=== TEST: Create Ward ===")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Note: Replace constituency_id with an actual UUID from your database
    data = {
        "constituency_id": "22222222-2222-2222-2222-222222222222",
        "name": "Test Ward API",
        "code": "TN-AC-999-W-999",
        "ward_number": 999,
        "population": 30000,
        "voter_count": 22000,
        "urbanization": "urban",
        "income_level": "medium",
        "literacy_rate": 88.5
    }

    response = requests.post(f"{GEOGRAPHY_URL}/wards/", headers=headers, json=data)

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 201


def test_ward_bulk_import(token):
    """Test POST /geography/wards/bulk-import/"""
    print("\n=== TEST: Bulk Import Wards ===")
    headers = {"Authorization": f"Bearer {token}"}

    # Check if sample file exists
    csv_path = "test_data/sample_wards.csv"
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found")
        return False

    with open(csv_path, 'rb') as f:
        files = {'file': f}
        data = {'update_existing': 'false'}
        response = requests.post(
            f"{GEOGRAPHY_URL}/wards/bulk-import/",
            headers=headers,
            files=files,
            data=data
        )

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code in [200, 201]


def test_booth_list(token):
    """Test GET /geography/polling-booths/"""
    print("\n=== TEST: List Polling Booths ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{GEOGRAPHY_URL}/polling-booths/", headers=headers)

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_booth_create(token):
    """Test POST /geography/polling-booths/"""
    print("\n=== TEST: Create Polling Booth ===")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Note: Replace constituency_id with an actual UUID from your database
    data = {
        "constituency_id": "22222222-2222-2222-2222-222222222222",
        "booth_number": "999",
        "name": "Test Polling Booth API",
        "address": "Test Address, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "total_voters": 1500,
        "male_voters": 750,
        "female_voters": 740,
        "transgender_voters": 10,
        "booth_type": "regular",
        "is_accessible": True,
        "priority_level": 4
    }

    response = requests.post(f"{GEOGRAPHY_URL}/polling-booths/", headers=headers, json=data)

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 201


def test_booth_bulk_import(token):
    """Test POST /geography/polling-booths/bulk-import/"""
    print("\n=== TEST: Bulk Import Polling Booths ===")
    headers = {"Authorization": f"Bearer {token}"}

    # Check if sample file exists
    csv_path = "test_data/sample_booths.csv"
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found")
        return False

    with open(csv_path, 'rb') as f:
        files = {'file': f}
        data = {'update_existing': 'false'}
        response = requests.post(
            f"{GEOGRAPHY_URL}/polling-booths/bulk-import/",
            headers=headers,
            files=files,
            data=data
        )

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code in [200, 201]


def test_booths_nearby(token):
    """Test GET /geography/polling-booths/nearby/"""
    print("\n=== TEST: Find Booths Nearby ===")
    headers = {"Authorization": f"Bearer {token}"}

    params = {
        "latitude": 13.0827,
        "longitude": 80.2707,
        "radius_meters": 5000
    }

    response = requests.get(
        f"{GEOGRAPHY_URL}/polling-booths/nearby/",
        headers=headers,
        params=params
    )

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_ward_statistics(token):
    """Test GET /geography/wards/statistics/"""
    print("\n=== TEST: Ward Statistics ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{GEOGRAPHY_URL}/wards/statistics/", headers=headers)

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_booth_statistics(token):
    """Test GET /geography/polling-booths/statistics/"""
    print("\n=== TEST: Polling Booth Statistics ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{GEOGRAPHY_URL}/polling-booths/statistics/", headers=headers)

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def run_all_tests():
    """Run all API tests"""
    print("=" * 60)
    print("GEOGRAPHY API TEST SUITE")
    print("=" * 60)

    # Get authentication token
    print("\n=== Authenticating ===")
    token = get_auth_token()

    if not token:
        print("ERROR: Authentication failed. Cannot proceed with tests.")
        return

    print(f"✓ Authentication successful")

    # Run tests
    tests = [
        ("List Wards", test_ward_list),
        ("Create Ward", test_ward_create),
        ("Bulk Import Wards", test_ward_bulk_import),
        ("List Polling Booths", test_booth_list),
        ("Create Polling Booth", test_booth_create),
        ("Bulk Import Polling Booths", test_booth_bulk_import),
        ("Find Booths Nearby", test_booths_nearby),
        ("Ward Statistics", test_ward_statistics),
        ("Booth Statistics", test_booth_statistics),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            success = test_func(token)
            results.append((test_name, success))
        except Exception as e:
            print(f"✗ {test_name} FAILED: {str(e)}")
            results.append((test_name, False))

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{status}: {test_name}")

    print("=" * 60)
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
