# API Documentation

Complete API reference for Pulse of People platform.

## Base URL

**Production:** `https://api.yourdomain.com`
**Development:** `http://localhost:8000`

## Authentication

All API endpoints (except health checks and public endpoints) require JWT authentication.

### Obtaining Access Token

**Endpoint:** `POST /api/auth/login/`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "your-password"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "role": "admin",
    "organization": "TVK"
  }
}
```

### Using Access Token

Include the access token in the Authorization header:

```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Refreshing Token

**Endpoint:** `POST /api/auth/refresh/`

**Request:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## Health Check Endpoints

No authentication required.

### Basic Health Check

**Endpoint:** `GET /api/health/`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1699545600,
  "version": "1.0.0",
  "environment": "production"
}
```

### Detailed Health Check

**Endpoint:** `GET /api/health/detailed/`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1699545600,
  "version": "1.0.0",
  "environment": "production",
  "components": {
    "database": {
      "healthy": true,
      "response_time_ms": 12.5,
      "message": "Database connection successful"
    },
    "cache": {
      "healthy": true,
      "response_time_ms": 3.2,
      "message": "Cache connection successful"
    },
    "celery": {
      "healthy": true,
      "workers": 4,
      "message": "4 worker(s) active"
    },
    "disk": {
      "healthy": true,
      "total_gb": 100,
      "free_gb": 45.5,
      "percent_used": 54.5,
      "status": "healthy"
    }
  }
}
```

### Liveness Probe

**Endpoint:** `GET /api/health/liveness/`

**Response:**
```json
{
  "status": "alive"
}
```

### Readiness Probe

**Endpoint:** `GET /api/health/readiness/`

**Response:**
```json
{
  "status": "ready",
  "components": {
    "database": true,
    "cache": true
  }
}
```

### Version Info

**Endpoint:** `GET /api/version/`

**Response:**
```json
{
  "version": "1.0.0",
  "environment": "production",
  "build_number": "123",
  "commit_hash": "abc123def456",
  "deployment_platform": "railway",
  "python_version": "3.11.0",
  "django_version": "5.2.7"
}
```

---

## User Management

### List Users

**Endpoint:** `GET /api/users/`

**Query Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20, max: 100)
- `role` - Filter by role
- `organization` - Filter by organization
- `search` - Search by name or email

**Response:**
```json
{
  "count": 100,
  "next": "https://api.yourdomain.com/api/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "admin",
      "organization": "TVK",
      "is_active": true,
      "created_at": "2023-11-09T10:00:00Z"
    }
  ]
}
```

### Get User Details

**Endpoint:** `GET /api/users/{id}/`

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "admin",
  "organization": "TVK",
  "phone": "+91-9876543210",
  "is_active": true,
  "permissions": ["view_users", "manage_users", "view_analytics"],
  "created_at": "2023-11-09T10:00:00Z",
  "updated_at": "2023-11-09T12:00:00Z"
}
```

### Create User

**Endpoint:** `POST /api/users/`

**Request:**
```json
{
  "email": "newuser@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "role": "user",
  "organization": "TVK",
  "phone": "+91-9876543210",
  "password": "SecurePassword123!"
}
```

**Response:** `201 Created`
```json
{
  "id": 2,
  "email": "newuser@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "role": "user",
  "organization": "TVK",
  "created_at": "2023-11-09T14:00:00Z"
}
```

### Update User

**Endpoint:** `PUT /api/users/{id}/` or `PATCH /api/users/{id}/`

**Request:**
```json
{
  "first_name": "Jane",
  "phone": "+91-9999999999"
}
```

**Response:** `200 OK`

### Delete User

**Endpoint:** `DELETE /api/users/{id}/`

**Response:** `204 No Content`

---

## Organization Management

### List Organizations

**Endpoint:** `GET /api/organizations/`

**Response:**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "name": "TVK",
      "slug": "tvk",
      "description": "Tamilaga Vettri Kazhagam",
      "logo": "https://cdn.example.com/logos/tvk.png",
      "created_at": "2023-01-01T00:00:00Z"
    }
  ]
}
```

---

## Campaign Management

### List Campaigns

**Endpoint:** `GET /api/campaigns/`

**Query Parameters:**
- `status` - Filter by status (active, completed, scheduled)
- `organization` - Filter by organization

**Response:**
```json
{
  "count": 25,
  "results": [
    {
      "id": 1,
      "name": "Tamil Nadu Assembly Elections 2026",
      "description": "Complete campaign strategy for TN elections",
      "status": "active",
      "start_date": "2025-01-01",
      "end_date": "2026-05-01",
      "organization": "TVK",
      "created_by": "admin@tvk.com",
      "created_at": "2023-11-01T00:00:00Z"
    }
  ]
}
```

---

## Analytics

### Get Dashboard Statistics

**Endpoint:** `GET /api/analytics/dashboard/`

**Response:**
```json
{
  "total_voters": 50000,
  "total_campaigns": 25,
  "active_field_workers": 150,
  "sentiment_score": 72.5,
  "recent_activities": [...],
  "trending_issues": [...]
}
```

### Get Sentiment Analysis

**Endpoint:** `GET /api/analytics/sentiment/`

**Query Parameters:**
- `start_date` - Start date (YYYY-MM-DD)
- `end_date` - End date (YYYY-MM-DD)
- `region` - Filter by region

**Response:**
```json
{
  "overall_sentiment": {
    "positive": 65,
    "neutral": 20,
    "negative": 15
  },
  "by_region": [...],
  "trending_topics": [...]
}
```

---

## File Upload

### Upload File

**Endpoint:** `POST /api/upload/`

**Request:** `multipart/form-data`
```
file: <binary>
type: "profile_photo" | "document" | "report"
```

**Response:**
```json
{
  "id": "abc123",
  "url": "https://cdn.example.com/files/abc123.pdf",
  "filename": "report.pdf",
  "size": 1024000,
  "type": "report",
  "uploaded_at": "2023-11-09T15:00:00Z"
}
```

### Maximum File Size
- Standard uploads: 10 MB
- Bulk uploads: 50 MB

---

## Error Responses

### Standard Error Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "email": ["This field is required"],
      "phone": ["Invalid phone number format"]
    }
  }
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Too Many Requests |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

### Common Error Codes

| Code | Description |
|------|-------------|
| `AUTHENTICATION_FAILED` | Invalid credentials |
| `TOKEN_EXPIRED` | JWT token expired |
| `PERMISSION_DENIED` | Insufficient permissions |
| `VALIDATION_ERROR` | Input validation failed |
| `NOT_FOUND` | Resource not found |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `SERVER_ERROR` | Internal server error |

---

## Rate Limiting

Default rate limits:
- **Anonymous users:** 100 requests/hour
- **Authenticated users:** 1000 requests/hour
- **Admin users:** 5000 requests/hour

Rate limit headers:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1699545600
```

---

## Pagination

All list endpoints support pagination:

**Query Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20, max: 100)

**Response:**
```json
{
  "count": 500,
  "next": "https://api.yourdomain.com/api/resource/?page=2",
  "previous": null,
  "results": [...]
}
```

---

## Webhooks

### Register Webhook

**Endpoint:** `POST /api/webhooks/`

**Request:**
```json
{
  "url": "https://your-app.com/webhook",
  "events": ["user.created", "campaign.completed"],
  "secret": "your-webhook-secret"
}
```

### Webhook Events

- `user.created`
- `user.updated`
- `user.deleted`
- `campaign.created`
- `campaign.updated`
- `campaign.completed`

### Webhook Payload

```json
{
  "event": "user.created",
  "timestamp": 1699545600,
  "data": {
    "id": 1,
    "email": "user@example.com",
    ...
  }
}
```

---

## SDKs and Libraries

### Python
```python
import requests

BASE_URL = "https://api.yourdomain.com"
TOKEN = "your-jwt-token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

response = requests.get(f"{BASE_URL}/api/users/", headers=headers)
users = response.json()
```

### JavaScript/TypeScript
```typescript
const BASE_URL = 'https://api.yourdomain.com';
const TOKEN = 'your-jwt-token';

const response = await fetch(`${BASE_URL}/api/users/`, {
  headers: {
    'Authorization': `Bearer ${TOKEN}`,
    'Content-Type': 'application/json'
  }
});

const users = await response.json();
```

---

## Support

For API support:
- Email: api-support@pulseofpeople.com
- Documentation: https://docs.pulseofpeople.com
- Status Page: https://status.pulseofpeople.com
