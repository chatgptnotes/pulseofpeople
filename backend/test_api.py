#!/usr/bin/env python
import requests
import json

BASE_URL = 'http://localhost:8000/api'

print('🔍 Testing Django API Endpoints...\n')
print('=' * 80)

# Test 1: Login with email
print('\n1️⃣  Testing LOGIN with EMAIL (dev@tvk.com)')
print('-' * 80)
try:
    response = requests.post(
        f'{BASE_URL}/auth/login/',
        json={'email': 'dev@tvk.com', 'password': 'Dev@1234'}
    )
    if response.status_code == 200:
        data = response.json()
        print('✅ Login successful!')
        print(f'   Access Token (first 50 chars): {data.get("access", "")[:50]}...')
        access_token = data.get('access')
    else:
        print(f'❌ Login failed: {response.status_code}')
        print(f'   Response: {response.text}')
        access_token = None
except Exception as e:
    print(f'❌ Error: {e}')
    access_token = None

# Test 2: Get User Profile
if access_token:
    print('\n2️⃣  Testing GET USER PROFILE')
    print('-' * 80)
    try:
        response = requests.get(
            f'{BASE_URL}/auth/profile/',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        if response.status_code == 200:
            data = response.json()
            print('✅ Profile fetched successfully!')
            print(f'   User: {data.get("name")} ({data.get("email")})')
            print(f'   Role: {data.get("role")}')
            print(f'   Permissions: {len(data.get("permissions", []))} total')
        else:
            print(f'❌ Failed: {response.status_code}')
            print(f'   Response: {response.text}')
    except Exception as e:
        print(f'❌ Error: {e}')

    # Test 3: List Users
    print('\n3️⃣  Testing LIST USERS (role-based filtering)')
    print('-' * 80)
    try:
        response = requests.get(
            f'{BASE_URL}/auth/users/',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        if response.status_code == 200:
            data = response.json()
            users = data.get('results', []) if isinstance(data, dict) else data
            print(f'✅ Users list fetched successfully!')
            print(f'   Total users visible: {len(users)}')
            if len(users) > 0:
                print(f'   First user: {users[0].get("name")} - {users[0].get("role")}')
        else:
            print(f'❌ Failed: {response.status_code}')
            print(f'   Response: {response.text}')
    except Exception as e:
        print(f'❌ Error: {e}')

print('\n' + '=' * 80)
print('\n✅ API Testing Complete!\n')
