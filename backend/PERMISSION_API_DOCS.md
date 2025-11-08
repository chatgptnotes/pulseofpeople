# Permission Management API Documentation

## Overview

This API provides comprehensive permission management endpoints for the Pulse of People platform. Administrators can programmatically grant, revoke, and sync user permissions with full audit logging.

## Base URL

```
http://127.0.0.1:8000/api
```

## Authentication

All endpoints require JWT authentication. Include the access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Permission Requirements

- **View Permissions**: `manage_roles` permission (Admin and above)
- **Grant/Revoke**: `manage_roles` permission (Admin and above)
- **Cannot grant permissions higher than own level**
- **Cannot modify superadmin permissions**
- **All permission changes are audited**

---

## Endpoints

### 1. List All Permissions

Get a list of all available permissions in the system.

**Endpoint:** `GET /api/permissions/`

**Permission Required:** Admin or above

**Response:**
```json
{
  "count": 67,
  "results": [
    {
      "id": 1,
      "name": "create_users",
      "category": "users",
      "description": "Can create new user accounts",
      "created_at": "2025-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "name": "view_analytics",
      "category": "analytics",
      "description": "Can view analytics dashboard",
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

---

### 2. Get Permission Categories

Get all permission categories with counts.

**Endpoint:** `GET /api/permissions/categories/`

**Permission Required:** Admin or above

**Response:**
```json
{
  "categories": [
    {
      "name": "users",
      "label": "User Management",
      "count": 15
    },
    {
      "name": "data",
      "label": "Data Access",
      "count": 20
    },
    {
      "name": "analytics",
      "label": "Analytics",
      "count": 12
    },
    {
      "name": "settings",
      "label": "Settings",
      "count": 10
    },
    {
      "name": "system",
      "label": "System",
      "count": 10
    }
  ]
}
```

---

### 3. Get Role Default Permissions

Get default permissions for a specific role.

**Endpoint:** `GET /api/permissions/roles/{role}/`

**Permission Required:** Admin or above

**Path Parameters:**
- `role` (string): One of: `superadmin`, `admin`, `manager`, `analyst`, `user`, `viewer`, `volunteer`

**Example:** `GET /api/permissions/roles/analyst/`

**Response:**
```json
{
  "role": "analyst",
  "permissions": [
    "view_analytics",
    "view_reports",
    "export_data",
    "view_polling_booths",
    "view_feedback"
  ]
}
```

---

### 4. List User Permissions

Get all permissions for a specific user, including role-based and custom permissions.

**Endpoint:** `GET /api/users/{user_id}/permissions/`

**Permission Required:** Admin or above

**Path Parameters:**
- `user_id` (integer): User ID

**Example:** `GET /api/users/123/permissions/`

**Response:**
```json
{
  "user_id": 123,
  "username": "john_doe",
  "email": "john@example.com",
  "role": "analyst",
  "role_permissions": [
    "view_analytics",
    "view_reports",
    "export_data"
  ],
  "custom_grants": [
    "create_users"
  ],
  "custom_revocations": [
    "export_data"
  ],
  "effective_permissions": [
    "view_analytics",
    "view_reports",
    "create_users"
  ]
}
```

**Field Descriptions:**
- `role_permissions`: Permissions that come from the user's role
- `custom_grants`: Permissions explicitly granted to this user (overrides role)
- `custom_revocations`: Permissions explicitly revoked from this user (overrides role)
- `effective_permissions`: Final computed permissions (role + grants - revocations)

---

### 5. Grant Permission to User

Grant a specific permission to a user.

**Endpoint:** `POST /api/users/{user_id}/permissions/grant/`

**Permission Required:** Admin or above

**Path Parameters:**
- `user_id` (integer): User ID

**Request Body:**
```json
{
  "permission": "create_users",
  "reason": "Promoted to team lead"
}
```

**Request Fields:**
- `permission` (string, required): Permission name to grant
- `reason` (string, optional): Reason for granting this permission

**Success Response (201 Created):**
```json
{
  "success": true,
  "user_id": 123,
  "username": "john_doe",
  "permission": "create_users",
  "granted_by": "admin@example.com",
  "granted_at": "2025-11-08T20:30:00Z",
  "message": "Permission 'create_users' granted successfully"
}
```

**Error Responses:**

**400 Bad Request** - Permission doesn't exist:
```json
{
  "error": {
    "permission": ["Permission 'invalid_permission' does not exist"]
  }
}
```

**400 Bad Request** - Permission already granted:
```json
{
  "error": {
    "non_field_errors": ["Permission 'create_users' is already granted to this user"]
  }
}
```

**403 Forbidden** - Cannot modify superadmin:
```json
{
  "error": {
    "non_field_errors": ["Cannot modify superadmin permissions"]
  }
}
```

**403 Forbidden** - Insufficient privileges:
```json
{
  "error": {
    "non_field_errors": ["Only superadmins can grant system permissions"]
  }
}
```

---

### 6. Revoke Permission from User

Revoke a specific permission from a user.

**Endpoint:** `POST /api/users/{user_id}/permissions/revoke/`

**Permission Required:** Admin or above

**Path Parameters:**
- `user_id` (integer): User ID

**Request Body:**
```json
{
  "permission": "create_users",
  "reason": "Role changed"
}
```

**Request Fields:**
- `permission` (string, required): Permission name to revoke
- `reason` (string, optional): Reason for revoking this permission

**Success Response (200 OK):**
```json
{
  "success": true,
  "user_id": 123,
  "username": "john_doe",
  "permission": "create_users",
  "revoked_by": "admin@example.com",
  "revoked_at": "2025-11-08T20:35:00Z",
  "message": "Permission 'create_users' revoked successfully"
}
```

**Error Responses:**

Similar to Grant Permission endpoint.

---

### 7. Sync User Permissions to Role Defaults

Reset user permissions to their role defaults (removes all custom grants and revocations).

**Endpoint:** `POST /api/users/{user_id}/permissions/sync-role/`

**Permission Required:** Admin or above

**Path Parameters:**
- `user_id` (integer): User ID

**Request Body:**
```json
{
  "confirm": true
}
```

**Request Fields:**
- `confirm` (boolean, required): Must be `true` to confirm this destructive operation

**Success Response (200 OK):**
```json
{
  "success": true,
  "user_id": 123,
  "username": "john_doe",
  "role": "analyst",
  "removed_grants": [
    "create_users"
  ],
  "removed_revocations": [
    "export_data"
  ],
  "current_permissions": [
    "view_analytics",
    "view_reports",
    "export_data"
  ],
  "message": "Permissions synced to role defaults. Removed 2 custom permissions."
}
```

**Error Responses:**

**400 Bad Request** - Confirmation not provided:
```json
{
  "error": {
    "confirm": ["You must confirm this operation by setting 'confirm' to true"]
  }
}
```

---

### 8. Get User Permission History

Get the permission change history for a user.

**Endpoint:** `GET /api/users/{user_id}/permissions/history/`

**Permission Required:** Admin or above

**Path Parameters:**
- `user_id` (integer): User ID

**Example:** `GET /api/users/123/permissions/history/`

**Response:**
```json
{
  "user_id": 123,
  "username": "john_doe",
  "total_changes": 5,
  "history": [
    {
      "action": "permission_granted",
      "permission": "create_users",
      "changed_by": "admin@example.com",
      "timestamp": "2025-11-08T20:30:00Z",
      "reason": "Promoted to team lead",
      "details": {
        "target_user_id": 123,
        "target_user_email": "john@example.com",
        "permission": "create_users",
        "reason": "Promoted to team lead",
        "granted_by": "admin@example.com"
      }
    },
    {
      "action": "permission_revoked",
      "permission": "export_data",
      "changed_by": "admin@example.com",
      "timestamp": "2025-11-08T19:15:00Z",
      "reason": "Security policy",
      "details": {
        "target_user_id": 123,
        "target_user_email": "john@example.com",
        "permission": "export_data",
        "reason": "Security policy",
        "revoked_by": "admin@example.com"
      }
    }
  ]
}
```

---

## Permission Business Logic

### How Effective Permissions are Calculated

1. **Start with role permissions**: User gets all permissions assigned to their role
2. **Add custom grants**: Any explicitly granted permissions are added
3. **Remove custom revocations**: Any explicitly revoked permissions are removed

**Example:**
- User role: `analyst`
- Role permissions: `["view_analytics", "view_reports", "export_data"]`
- Custom grants: `["create_users"]`
- Custom revocations: `["export_data"]`
- **Effective permissions**: `["view_analytics", "view_reports", "create_users"]`

### Permission Hierarchy Rules

1. **Superadmins**:
   - Have all permissions automatically
   - Can grant/revoke any permission
   - Can modify any user (except other superadmins' permissions)

2. **Admins**:
   - Can grant/revoke permissions to users in their organization
   - Cannot grant system permissions
   - Cannot modify superadmin permissions
   - Cannot modify their own permissions

3. **Other Roles**:
   - Cannot grant/revoke permissions
   - Cannot modify their own permissions

### Validation Rules

1. **Cannot modify superadmin permissions** (except superadmins themselves)
2. **Cannot modify own permissions** (except superadmins)
3. **Admins can only grant permissions they have**
4. **System permissions can only be granted by superadmins**
5. **Organization isolation**: Admins can only manage users in their organization

---

## Audit Logging

All permission changes are automatically logged to the audit log with:

- **User**: Who made the change
- **Action**: `permission_granted`, `permission_revoked`, or `permission_sync`
- **Target**: Which user was affected
- **Permission**: Which permission was changed
- **Reason**: Why the change was made (if provided)
- **Timestamp**: When the change occurred
- **IP Address**: Where the request came from
- **User Agent**: What client made the request

---

## Example Use Cases

### Use Case 1: Promote User to Team Lead

Grant a user the ability to create users:

```bash
POST /api/users/123/permissions/grant/
{
  "permission": "create_users",
  "reason": "Promoted to team lead"
}
```

### Use Case 2: Temporarily Remove Access

Revoke export permission for security:

```bash
POST /api/users/123/permissions/revoke/
{
  "permission": "export_data",
  "reason": "Under investigation"
}
```

### Use Case 3: Reset Permissions After Role Change

After changing a user's role, sync their permissions:

```bash
# First, update user role via user management API
PATCH /api/users/123/
{
  "role": "manager"
}

# Then sync permissions to new role defaults
POST /api/users/123/permissions/sync-role/
{
  "confirm": true
}
```

### Use Case 4: Audit Permission Changes

Check what permission changes were made to a user:

```bash
GET /api/users/123/permissions/history/
```

---

## Error Handling

All endpoints return consistent error responses:

**Format:**
```json
{
  "error": {
    "field_name": ["Error message"],
    "another_field": ["Another error message"]
  }
}
```

**Common HTTP Status Codes:**
- `200 OK`: Success (for GET, DELETE operations)
- `201 Created`: Success (for POST operations that create resources)
- `400 Bad Request`: Validation error or invalid input
- `401 Unauthorized`: Authentication required or token invalid
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: User or permission not found
- `500 Internal Server Error`: Server error

---

## Testing with curl

### Get all permissions:
```bash
curl -X GET http://127.0.0.1:8000/api/permissions/ \
  -H "Authorization: Bearer <access_token>"
```

### Grant permission:
```bash
curl -X POST http://127.0.0.1:8000/api/users/123/permissions/grant/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "permission": "create_users",
    "reason": "Promoted to team lead"
  }'
```

### List user permissions:
```bash
curl -X GET http://127.0.0.1:8000/api/users/123/permissions/ \
  -H "Authorization: Bearer <access_token>"
```

### Sync to role defaults:
```bash
curl -X POST http://127.0.0.1:8000/api/users/123/permissions/sync-role/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "confirm": true
  }'
```

---

## Security Considerations

1. **All endpoints require authentication** via JWT tokens
2. **All permission changes are audited** with full context
3. **Organization isolation** prevents cross-organization access
4. **Role hierarchy** prevents privilege escalation
5. **Cannot modify own permissions** (except superadmins)
6. **Cannot modify superadmin permissions** (except by other superadmins)
7. **System permissions** are protected (superadmin only)

---

## Frontend Integration

### Example React Hook for Permission Management

```typescript
import { useState } from 'react';
import axios from 'axios';

const usePermissions = (userId: number) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const grantPermission = async (permission: string, reason?: string) => {
    setLoading(true);
    try {
      const response = await axios.post(
        `/api/users/${userId}/permissions/grant/`,
        { permission, reason },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      return response.data;
    } catch (err) {
      setError(err.response?.data?.error);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const revokePermission = async (permission: string, reason?: string) => {
    setLoading(true);
    try {
      const response = await axios.post(
        `/api/users/${userId}/permissions/revoke/`,
        { permission, reason },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      return response.data;
    } catch (err) {
      setError(err.response?.data?.error);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { grantPermission, revokePermission, loading, error };
};
```

---

## Version

**API Version**: 1.0
**Last Updated**: 2025-11-08
**Status**: Production Ready
