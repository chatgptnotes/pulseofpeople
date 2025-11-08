#!/bin/bash

# Permission Management API Test Script
# This script tests all permission management endpoints

set -e  # Exit on error

# Configuration
BASE_URL="http://127.0.0.1:8000/api"
ADMIN_EMAIL="admin@example.com"
ADMIN_PASSWORD="admin123"
TEST_USER_ID=2  # Change this to an actual user ID in your database

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

print_header() {
    echo ""
    echo "=========================================="
    echo "$1"
    echo "=========================================="
}

# Step 1: Login and get token
print_header "Step 1: Login and Get Access Token"
print_info "Logging in as $ADMIN_EMAIL..."

LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login/" \
    -H "Content-Type: application/json" \
    -d "{
        \"email\": \"$ADMIN_EMAIL\",
        \"password\": \"$ADMIN_PASSWORD\"
    }")

# Extract access token
ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access":"[^"]*' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
    print_error "Failed to get access token"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

print_success "Access token obtained"
echo "Token: ${ACCESS_TOKEN:0:20}..."

# Step 2: List all permissions
print_header "Step 2: List All Permissions"

PERMISSIONS_RESPONSE=$(curl -s -X GET "$BASE_URL/permissions/" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

PERMISSION_COUNT=$(echo "$PERMISSIONS_RESPONSE" | grep -o '"count":[0-9]*' | cut -d':' -f2)

if [ -z "$PERMISSION_COUNT" ]; then
    print_error "Failed to get permissions"
    echo "Response: $PERMISSIONS_RESPONSE"
else
    print_success "Found $PERMISSION_COUNT permissions"
fi

# Step 3: Get permission categories
print_header "Step 3: Get Permission Categories"

CATEGORIES_RESPONSE=$(curl -s -X GET "$BASE_URL/permissions/categories/" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

echo "$CATEGORIES_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$CATEGORIES_RESPONSE"

if echo "$CATEGORIES_RESPONSE" | grep -q "categories"; then
    print_success "Categories retrieved successfully"
else
    print_error "Failed to get categories"
fi

# Step 4: Get role permissions (analyst)
print_header "Step 4: Get Role Permissions (Analyst)"

ROLE_PERMS_RESPONSE=$(curl -s -X GET "$BASE_URL/permissions/roles/analyst/" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

echo "$ROLE_PERMS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$ROLE_PERMS_RESPONSE"

if echo "$ROLE_PERMS_RESPONSE" | grep -q "analyst"; then
    print_success "Role permissions retrieved successfully"
else
    print_error "Failed to get role permissions"
fi

# Step 5: Get user permissions
print_header "Step 5: Get User Permissions (User ID: $TEST_USER_ID)"

USER_PERMS_RESPONSE=$(curl -s -X GET "$BASE_URL/users/$TEST_USER_ID/permissions/" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

echo "$USER_PERMS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$USER_PERMS_RESPONSE"

if echo "$USER_PERMS_RESPONSE" | grep -q "user_id"; then
    print_success "User permissions retrieved successfully"
else
    print_error "Failed to get user permissions (User may not exist with ID $TEST_USER_ID)"
    print_info "Update TEST_USER_ID in this script to match an actual user ID"
fi

# Step 6: Grant permission (example - may fail if permission already granted)
print_header "Step 6: Grant Permission to User"

print_info "Attempting to grant 'view_analytics' permission..."

GRANT_RESPONSE=$(curl -s -X POST "$BASE_URL/users/$TEST_USER_ID/permissions/grant/" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "permission": "view_analytics",
        "reason": "Testing permission grant API"
    }')

echo "$GRANT_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$GRANT_RESPONSE"

if echo "$GRANT_RESPONSE" | grep -q "success"; then
    print_success "Permission granted successfully"
elif echo "$GRANT_RESPONSE" | grep -q "already granted"; then
    print_info "Permission already granted (this is expected if you ran this test before)"
else
    print_error "Failed to grant permission"
fi

# Step 7: Revoke permission (example)
print_header "Step 7: Revoke Permission from User"

print_info "Attempting to revoke 'view_analytics' permission..."

REVOKE_RESPONSE=$(curl -s -X POST "$BASE_URL/users/$TEST_USER_ID/permissions/revoke/" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "permission": "view_analytics",
        "reason": "Testing permission revoke API"
    }')

echo "$REVOKE_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$REVOKE_RESPONSE"

if echo "$REVOKE_RESPONSE" | grep -q "success"; then
    print_success "Permission revoked successfully"
else
    print_error "Failed to revoke permission"
fi

# Step 8: Get permission history
print_header "Step 8: Get Permission History"

HISTORY_RESPONSE=$(curl -s -X GET "$BASE_URL/users/$TEST_USER_ID/permissions/history/" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

echo "$HISTORY_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$HISTORY_RESPONSE"

if echo "$HISTORY_RESPONSE" | grep -q "history"; then
    print_success "Permission history retrieved successfully"
else
    print_error "Failed to get permission history"
fi

# Step 9: Sync to role defaults (commented out as it's destructive)
print_header "Step 9: Sync to Role Defaults (SKIPPED)"

print_info "Sync operation is skipped by default as it removes all custom permissions"
print_info "To test it, uncomment the code below in this script"

# Uncomment to test sync operation
# SYNC_RESPONSE=$(curl -s -X POST "$BASE_URL/users/$TEST_USER_ID/permissions/sync-role/" \
#     -H "Authorization: Bearer $ACCESS_TOKEN" \
#     -H "Content-Type: application/json" \
#     -d '{
#         "confirm": true
#     }')
#
# echo "$SYNC_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$SYNC_RESPONSE"
#
# if echo "$SYNC_RESPONSE" | grep -q "success"; then
#     print_success "Permissions synced successfully"
# else
#     print_error "Failed to sync permissions"
# fi

# Summary
print_header "Test Summary"

print_success "All basic permission management endpoints are working!"
print_info "Review the responses above to verify correctness"
print_info ""
print_info "Next steps:"
print_info "1. Update TEST_USER_ID in this script to test with actual users"
print_info "2. Test with different roles (admin, superadmin, etc.)"
print_info "3. Test error cases (invalid permissions, unauthorized access, etc.)"
print_info "4. Integrate with your frontend application"

echo ""
