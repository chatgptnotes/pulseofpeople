"""
Test Script for Audit Logging Implementation

This script provides manual tests for the audit logging functionality.
Run this after activating your virtual environment and running migrations.

Usage:
    python test_audit_logging.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import AuditLog, UserProfile
from api.utils.audit import (
    log_action, capture_model_state, get_field_changes,
    ACTION_USER_CREATED, ACTION_USER_UPDATED, ACTION_LOGIN_SUCCESS
)


def test_basic_logging():
    """Test basic audit logging functionality"""
    print("\n=== Test 1: Basic Audit Logging ===")

    # Create a test user
    user, created = User.objects.get_or_create(
        username='audit_test_user',
        defaults={'email': 'audit@test.com'}
    )

    # Log an action
    log_action(
        user=user,
        action=ACTION_USER_CREATED,
        resource_type='User',
        resource_id=str(user.id),
        changes={'username': user.username, 'email': user.email},
        request=None,
        async_log=False  # Synchronous for testing
    )

    # Check if log was created
    recent_log = AuditLog.objects.filter(user=user).first()
    if recent_log:
        print(f"✓ Audit log created successfully")
        print(f"  - Action: {recent_log.action}")
        print(f"  - Resource: {recent_log.target_model} (ID: {recent_log.target_id})")
        print(f"  - Changes: {recent_log.changes}")
        return True
    else:
        print("✗ Failed to create audit log")
        return False


def test_state_capture():
    """Test model state capture and change detection"""
    print("\n=== Test 2: State Capture & Change Detection ===")

    # Get or create a user
    user, _ = User.objects.get_or_create(
        username='audit_test_user',
        defaults={'email': 'audit@test.com'}
    )

    # Create profile if needed
    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={'role': 'user'}
    )

    # Capture before state
    before_state = capture_model_state(profile)
    print(f"✓ Captured before state: {len(before_state)} fields")

    # Make changes
    profile.role = 'analyst'
    profile.phone = '+1234567890'
    profile.save()

    # Capture after state
    after_state = capture_model_state(profile)
    print(f"✓ Captured after state: {len(after_state)} fields")

    # Get changes
    changes = get_field_changes(before_state, after_state)
    if changes:
        print(f"✓ Detected {len(changes)} changes:")
        for field, change in changes.items():
            print(f"  - {field}: {change['before']} → {change['after']}")
        return True
    else:
        print("✗ No changes detected")
        return False


def test_action_constants():
    """Test that action constants are valid"""
    print("\n=== Test 3: Action Constants ===")

    from api.utils.audit import (
        ACTION_USER_CREATED, ACTION_USER_UPDATED, ACTION_USER_DELETED,
        ACTION_ROLE_CHANGED, ACTION_LOGIN_SUCCESS, ACTION_LOGIN_FAILED,
        ACTION_LOGOUT, ACTION_BULK_UPLOAD_STARTED
    )

    actions = [
        ACTION_USER_CREATED, ACTION_USER_UPDATED, ACTION_USER_DELETED,
        ACTION_ROLE_CHANGED, ACTION_LOGIN_SUCCESS, ACTION_LOGIN_FAILED,
        ACTION_LOGOUT, ACTION_BULK_UPLOAD_STARTED
    ]

    # Check if all actions are valid (exist in MODEL choices)
    valid_actions = [choice[0] for choice in AuditLog.ACTION_TYPES]

    all_valid = True
    for action in actions:
        if action in valid_actions:
            print(f"✓ {action} is valid")
        else:
            print(f"✗ {action} is NOT valid")
            all_valid = False

    return all_valid


def test_query_performance():
    """Test audit log query performance"""
    print("\n=== Test 4: Query Performance ===")

    # Count total logs
    total = AuditLog.objects.count()
    print(f"✓ Total audit logs: {total}")

    # Test indexed queries
    user = User.objects.first()
    if user:
        user_logs = AuditLog.objects.filter(user=user).count()
        print(f"✓ Logs for user {user.username}: {user_logs}")

    # Test action filter
    login_logs = AuditLog.objects.filter(action='login_success').count()
    print(f"✓ Login success logs: {login_logs}")

    return True


def test_serializers():
    """Test audit log serializers"""
    print("\n=== Test 5: Serializers ===")

    try:
        from api.serializers import AuditLogSerializer, AuditLogListSerializer

        log = AuditLog.objects.first()
        if log:
            # Test full serializer
            full_serializer = AuditLogSerializer(log)
            print(f"✓ AuditLogSerializer works")
            print(f"  - Fields: {', '.join(full_serializer.data.keys())}")

            # Test list serializer
            list_serializer = AuditLogListSerializer(log)
            print(f"✓ AuditLogListSerializer works")
            print(f"  - Fields: {', '.join(list_serializer.data.keys())}")
            return True
        else:
            print("⚠ No audit logs to test serializers")
            return True
    except Exception as e:
        print(f"✗ Serializer test failed: {str(e)}")
        return False


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("AUDIT LOGGING TEST SUITE")
    print("=" * 60)

    tests = [
        test_basic_logging,
        test_state_capture,
        test_action_constants,
        test_query_performance,
        test_serializers
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Test failed with exception: {str(e)}")
            results.append(False)

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")

    if passed == total:
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed. Check output above.")

    return passed == total


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
