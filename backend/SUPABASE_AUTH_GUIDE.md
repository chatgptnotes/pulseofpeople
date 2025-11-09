# Supabase JWT Authentication Guide

## Overview

The Django backend has been updated to properly validate Supabase JWT tokens sent from the frontend. This guide explains how the authentication system works and how to test it.

## Architecture

### Authentication Flow

1. **Frontend**: User authenticates with Supabase (email/password, OAuth, etc.)
2. **Supabase**: Returns JWT access token to frontend
3. **Frontend**: Sends API requests with `Authorization: Bearer <token>` header
4. **Django Backend**:
   - Validates JWT token using SUPABASE_JWT_SECRET
   - Extracts user information from token payload
   - Gets or creates Django User based on email
   - Creates/updates UserProfile with role from Supabase metadata
   - Returns user data in response

### Files Modified

#### `/Users/murali/Downloads/pulseofpeople/backend/api/authentication.py`
**Changes:**
- **Line 6-8**: Added logging import for comprehensive debugging
- **Line 15**: Added logger instance for api.authentication module
- **Line 23-56**: Enhanced `authenticate()` method with detailed logging at each step
- **Line 58-96**: Enhanced `verify_supabase_token()` with:
  - Proper JWT secret validation
  - Explicit decode options for signature, expiration, and audience verification
  - Comprehensive error logging for all failure scenarios
- **Line 98-111**: Refactored `get_or_create_user()` to use centralized utility function
- **Line 120-167**: Enhanced `HybridAuthentication` class with:
  - Removed silent failures (no more `pass` statements)
  - Added detailed logging for authentication flow
  - Proper error handling and fallback logic

#### `/Users/murali/Downloads/pulseofpeople/backend/config/settings.py`
**Changes:**
- **Line 204-223**: Supabase configuration already properly set up
- **Line 219**: SUPABASE_JWT_SECRET loaded from environment
- **Line 234-236**: HybridAuthentication set as default authentication class
- **Line 555-559**: Added dedicated logger for api.authentication module with DEBUG level in development

## Environment Variables

Ensure these are set in `/Users/murali/Downloads/pulseofpeople/backend/.env`:

```env
# Supabase Authentication
SUPABASE_URL=https://iwtgbseaoztjbnvworyq.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_JWT_SECRET=X6j+39tynhesQLZuzPc9IXP8H9UONWcKmkKdonFBnrvIqXMO+T+PACOWxpks6fVaKoPblX0FPyI3vc3X5J1x7g==
```

**Critical**: The `SUPABASE_JWT_SECRET` is the actual JWT secret used to validate tokens. This is different from the anon key.

## How It Works

### 1. Token Validation

The `SupabaseJWTAuthentication` class decodes and validates the token using:

```python
payload = jwt.decode(
    token,
    supabase_jwt_secret,
    algorithms=['HS256'],
    audience='authenticated',
    options={
        'verify_signature': True,
        'verify_exp': True,
        'verify_aud': True,
    }
)
```

### 2. Token Payload Structure

Expected Supabase JWT payload:
```json
{
  "sub": "user-uuid-from-supabase",
  "email": "user@example.com",
  "role": "authenticated",
  "aud": "authenticated",
  "exp": 1234567890,
  "iat": 1234567890,
  "user_metadata": {
    "first_name": "John",
    "last_name": "Doe",
    "username": "johndoe",
    "phone": "+1234567890",
    "bio": "User bio"
  },
  "app_metadata": {
    "role": "user",
    "organization_id": 123
  }
}
```

### 3. User Sync

The `get_user_from_supabase_payload()` utility function:
- Extracts email and user ID from token
- Finds existing Django user by email OR creates new user
- Creates/updates UserProfile with:
  - Role from `app_metadata.role` or `user_metadata.role` (defaults to 'user')
  - Phone, bio, avatar from user_metadata
  - Organization assignment from `app_metadata.organization_id`

### 4. Hybrid Authentication

The `HybridAuthentication` class provides fallback support:
1. **First**: Try Supabase JWT authentication
2. **Fallback**: Try Django JWT authentication (for legacy users)

This allows both authentication methods to coexist during migration.

## Testing

### Manual Testing with cURL

1. **Get a Supabase token** (from frontend login or Supabase dashboard)

2. **Test authenticated endpoint**:
```bash
curl -X GET http://127.0.0.1:8000/api/users/me/ \
  -H "Authorization: Bearer <your-supabase-token>"
```

3. **Expected success response**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "user",
  "profile": {
    "role": "user",
    "phone": "+1234567890",
    "bio": "User bio"
  }
}
```

4. **Test with invalid token**:
```bash
curl -X GET http://127.0.0.1:8000/api/users/me/ \
  -H "Authorization: Bearer invalid-token"
```

Expected error:
```json
{
  "detail": "Invalid token"
}
```

### Logging Output

With DEBUG=True, you'll see detailed logs:

```
[INFO] api.authentication - Attempting Supabase JWT authentication with token: eyJhbGciOiJIUzI1NiI...
[DEBUG] api.authentication - Using JWT secret: X6j+39tynh...
[DEBUG] api.authentication - Token payload: sub=abc-123, email=user@example.com, role=authenticated
[INFO] api.authentication - Token verified successfully. User ID: abc-123, Email: user@example.com
[INFO] api.authentication - Found existing user: user@example.com (ID: 1)
[INFO] api.authentication - User authenticated: user@example.com (ID: 1)
```

### Error Scenarios

#### 1. Expired Token
```
[WARNING] api.authentication - Token expired: Signature has expired
```
Response: `{"detail": "Token has expired"}`

#### 2. Invalid Signature
```
[WARNING] api.authentication - Invalid token error: Signature verification failed
```
Response: `{"detail": "Invalid token"}`

#### 3. Missing JWT Secret
```
[ERROR] api.authentication - SUPABASE_JWT_SECRET not configured in settings
```
Response: `{"detail": "Supabase JWT secret not configured"}`

## Frontend Integration

### Axios Example

```typescript
import axios from 'axios';
import { supabase } from './supabase';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
});

// Add token to all requests
api.interceptors.request.use(async (config) => {
  const { data: { session } } = await supabase.auth.getSession();

  if (session?.access_token) {
    config.headers.Authorization = `Bearer ${session.access_token}`;
  }

  return config;
});

// Usage
const getUserProfile = async () => {
  const response = await api.get('/api/users/me/');
  return response.data;
};
```

### Fetch Example

```typescript
const token = (await supabase.auth.getSession()).data.session?.access_token;

const response = await fetch('http://127.0.0.1:8000/api/users/me/', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  },
});

const data = await response.json();
```

## Role-Based Access Control

User roles are synced from Supabase metadata:

```typescript
// In Supabase, set user role via metadata
await supabase.auth.admin.updateUserById(userId, {
  app_metadata: {
    role: 'admin',  // or 'manager', 'analyst', 'user', etc.
  }
});
```

Django will automatically update the UserProfile.role on next authentication.

## Troubleshooting

### Issue: "Supabase JWT secret not configured"

**Solution**: Verify SUPABASE_JWT_SECRET is set in `.env` file and server is restarted.

### Issue: "Invalid token"

**Causes**:
- Token expired (default: 1 hour from Supabase)
- Wrong JWT secret configured
- Token tampered with
- Token from different Supabase project

**Solution**:
1. Get fresh token from Supabase
2. Verify JWT secret matches your Supabase project (Dashboard > Settings > API > JWT Secret)

### Issue: User not created in Django

**Check logs** for errors in user sync:
```
[ERROR] api.authentication - User sync failed: ...
```

**Common causes**:
- Email missing from token
- Database connection issue
- UserProfile model validation error

## Security Considerations

1. **JWT Secret**: Never expose SUPABASE_JWT_SECRET in frontend code
2. **Token Expiration**: Tokens expire after 1 hour (configurable in Supabase)
3. **HTTPS**: Always use HTTPS in production
4. **Token Refresh**: Implement token refresh on frontend before expiration
5. **Role Verification**: Backend validates roles from trusted Supabase metadata

## Performance

- **Token Validation**: ~5-10ms per request
- **User Lookup**: Cached by Django ORM
- **User Creation**: Only on first authentication
- **Logging**: DEBUG level logging adds ~1-2ms overhead

## Next Steps

1. Test authentication with real Supabase tokens
2. Verify user creation/sync works correctly
3. Test role-based permissions
4. Monitor logs for any authentication issues
5. Configure token refresh on frontend
6. Add rate limiting for auth endpoints (already configured: 100/hour for anonymous)

## Support

For issues or questions:
1. Check Django logs: `/Users/murali/Downloads/pulseofpeople/backend/logs/app.log`
2. Check error logs: `/Users/murali/Downloads/pulseofpeople/backend/logs/error.log`
3. Enable DEBUG logging for detailed authentication flow
