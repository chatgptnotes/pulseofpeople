# API Reference - Pulse of People Platform

## Table of Contents
1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Master Data Endpoints](#master-data-endpoints)
4. [Wards and Booths](#wards-and-booths)
5. [Feedback and Reports](#feedback-and-reports)
6. [Analytics](#analytics)
7. [User Management](#user-management)
8. [Error Codes](#error-codes)
9. [Rate Limiting](#rate-limiting)
10. [Examples](#examples)

---

## Overview

### Base URL

```
Production: https://api.pulseofpeople.com
Development: http://127.0.0.1:8000
```

All API endpoints are prefixed with `/api/`

**Example:** `http://127.0.0.1:8000/api/constituencies/`

### API Versioning

Current version: **v1** (default)

Future versions will use: `/api/v2/`, `/api/v3/`, etc.

### Content Type

All requests and responses use JSON format:

```
Content-Type: application/json
```

### Response Format

**Success Response:**
```json
{
  "status": "success",
  "data": { ... },
  "message": "Operation completed successfully"
}
```

**Error Response:**
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": { ... }
  }
}
```

**Paginated Response:**
```json
{
  "count": 1000,
  "next": "http://api.example.com/api/booths/?page=2",
  "previous": null,
  "results": [ ... ]
}
```

---

## Authentication

### 1. Register User

**Endpoint:** `POST /api/auth/signup/`

**Access:** Public (but requires invite code or admin approval)

**Request:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecureP@ss123",
  "password_confirm": "SecureP@ss123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+919876543210"
}
```

**Response:** `201 Created`
```json
{
  "status": "success",
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "username": "johndoe",
      "role": "viewer"
    },
    "message": "Account created. Awaiting admin approval."
  }
}
```

**Errors:**
- `400` - Validation error (email exists, weak password)
- `429` - Too many registration attempts

---

### 2. Login

**Endpoint:** `POST /api/auth/login/`

**Access:** Public

**Request:**
```json
{
  "username": "johndoe",
  "password": "SecureP@ss123"
}
```

OR

```json
{
  "email": "user@example.com",
  "password": "SecureP@ss123"
}
```

**Response:** `200 OK`
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "johndoe",
    "role": "admin",
    "organization": {
      "id": "org-uuid",
      "name": "TVK Party"
    }
  }
}
```

**Token Lifetime:**
- Access Token: 60 minutes
- Refresh Token: 7 days

**Errors:**
- `401` - Invalid credentials
- `403` - Account inactive or not approved
- `429` - Too many login attempts (rate limited)

---

### 3. Refresh Token

**Endpoint:** `POST /api/auth/refresh/`

**Access:** Public

**Request:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:** `200 OK`
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Errors:**
- `401` - Invalid or expired refresh token

---

### 4. Logout

**Endpoint:** `POST /api/auth/logout/`

**Access:** Authenticated

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:** `200 OK`
```json
{
  "message": "Successfully logged out"
}
```

**Note:** Blacklists the refresh token

---

### 5. Get Current User Profile

**Endpoint:** `GET /api/auth/profile/`

**Access:** Authenticated

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "role": "admin",
  "organization": {
    "id": "org-uuid",
    "name": "TVK Party",
    "slug": "tvk"
  },
  "permissions": [
    "view_analytics",
    "manage_users",
    "upload_data"
  ],
  "assigned_constituencies": [
    {"id": "uuid", "name": "Chennai Central", "code": "TN-AC-001"}
  ]
}
```

---

### 6. Update Profile

**Endpoint:** `PATCH /api/auth/profile/`

**Access:** Authenticated

**Request:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+919876543210"
}
```

**Response:** `200 OK`
```json
{
  "message": "Profile updated successfully",
  "user": { ... }
}
```

---

### Using Authentication

**Include token in all authenticated requests:**

```http
GET /api/wards/ HTTP/1.1
Host: api.pulseofpeople.com
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json
```

**cURL Example:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://127.0.0.1:8000/api/wards/
```

---

## Master Data Endpoints

### 1. States

**List States**

`GET /api/states/`

**Access:** Public

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "name": "Tamil Nadu",
    "code": "TN",
    "capital": "Chennai",
    "region": "South",
    "total_districts": 38,
    "total_constituencies": 234
  },
  {
    "id": "uuid",
    "name": "Puducherry",
    "code": "PY",
    "capital": "Puducherry",
    "region": "South",
    "total_districts": 4,
    "total_constituencies": 30
  }
]
```

**Get Single State**

`GET /api/states/{id}/`

---

### 2. Districts

**List Districts**

`GET /api/districts/`

**Access:** Public

**Query Parameters:**
- `state` - Filter by state code (e.g., `?state=TN`)
- `search` - Search by name
- `page` - Page number (default: 1)
- `page_size` - Results per page (default: 50, max: 100)

**Response:** `200 OK`
```json
{
  "count": 38,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "name": "Chennai",
      "code": "TN-CH",
      "state": {
        "id": "uuid",
        "name": "Tamil Nadu",
        "code": "TN"
      },
      "total_constituencies": 16,
      "population": 10000000
    }
  ]
}
```

**Get Single District**

`GET /api/districts/{id}/`

---

### 3. Constituencies

**List Constituencies**

`GET /api/constituencies/`

**Access:** Public

**Query Parameters:**
- `state` - Filter by state code
- `district` - Filter by district ID
- `type` - Filter by type: `assembly` or `parliament`
- `search` - Search by name or code
- `ordering` - Sort: `name`, `-name`, `code`, `number`

**Response:** `200 OK`
```json
{
  "count": 234,
  "next": "http://api.example.com/api/constituencies/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "name": "Chennai Central",
      "code": "TN-AC-001",
      "number": 1,
      "type": "assembly",
      "state": {
        "name": "Tamil Nadu",
        "code": "TN"
      },
      "district": {
        "name": "Chennai",
        "code": "TN-CH"
      },
      "total_wards": 25,
      "total_booths": 350,
      "total_voters": 250000,
      "reserved_for": null
    }
  ]
}
```

**Get Single Constituency**

`GET /api/constituencies/{id}/`

**Get Constituency Statistics**

`GET /api/constituencies/{id}/stats/`

**Response:**
```json
{
  "constituency": {
    "id": "uuid",
    "name": "Chennai Central",
    "code": "TN-AC-001"
  },
  "stats": {
    "total_wards": 25,
    "total_booths": 350,
    "total_voters": 250000,
    "male_voters": 125000,
    "female_voters": 124500,
    "transgender_voters": 500,
    "feedback_count": 1250,
    "field_reports_count": 85,
    "sentiment_score": 0.65
  }
}
```

---

### 4. Political Parties

**List Parties**

`GET /api/political-parties/`

**Access:** Public

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Tamilaga Vettri Kazhagam",
    "short_name": "TVK",
    "symbol": "Two Leaves",
    "color": "#FF0000",
    "founded_year": 2024,
    "is_active": true
  }
]
```

---

### 5. Issue Categories

**List Issues**

`GET /api/issue-categories/`

**Access:** Public

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Social Justice & Caste Issues",
    "priority": 9,
    "color": "#E74C3C",
    "icon": "balance",
    "description": "Issues related to social justice and caste-based discrimination"
  },
  {
    "id": "uuid",
    "name": "Women's Safety & Empowerment",
    "priority": 8,
    "color": "#9B59B6",
    "icon": "female",
    "description": "Women's safety, empowerment, and gender equality"
  }
]
```

---

### 6. Voter Segments

**List Voter Segments**

`GET /api/voter-segments/`

**Access:** Public

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Fishermen Community",
    "priority_level": 9,
    "estimated_population": 500000,
    "key_issues": ["livelihood", "coastal_protection"],
    "description": "Traditional fishing communities along the coast"
  }
]
```

---

## Wards and Booths

### 1. Wards

**List Wards**

`GET /api/wards/`

**Access:** Authenticated (Role-based filtering applies)

**Query Parameters:**
- `constituency` - Filter by constituency ID
- `search` - Search by name or code
- `urbanization` - Filter: `urban`, `semi-urban`, `rural`
- `income_level` - Filter: `low`, `medium`, `high`
- `ordering` - Sort by field

**Response:** `200 OK`
```json
{
  "count": 500,
  "next": "http://api.example.com/api/wards/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "organization": {
        "id": "uuid",
        "name": "TVK Party"
      },
      "constituency": {
        "id": "uuid",
        "name": "Chennai Central",
        "code": "TN-AC-001"
      },
      "name": "Anna Nagar Ward 1",
      "code": "TN-AC-001-W-001",
      "ward_number": 1,
      "population": 25000,
      "voter_count": 18500,
      "total_booths": 12,
      "urbanization": "urban",
      "income_level": "medium",
      "literacy_rate": 85.50,
      "created_at": "2025-11-01T10:00:00Z",
      "updated_at": "2025-11-05T14:30:00Z"
    }
  ]
}
```

**Get Single Ward**

`GET /api/wards/{id}/`

**Create Ward**

`POST /api/wards/`

**Access:** Admin only

**Request:**
```json
{
  "constituency": "constituency-uuid",
  "name": "Anna Nagar Ward 1",
  "code": "TN-AC-001-W-001",
  "ward_number": 1,
  "population": 25000,
  "voter_count": 18500,
  "urbanization": "urban",
  "income_level": "medium"
}
```

**Response:** `201 Created`

**Update Ward**

`PATCH /api/wards/{id}/`

**Access:** Admin only

**Delete Ward**

`DELETE /api/wards/{id}/`

**Access:** Admin only

**Response:** `204 No Content`

**Bulk Upload Wards (CSV)**

`POST /api/wards/bulk-upload/`

**Access:** Admin only

**Request:** `multipart/form-data`
```
file: wards.csv
```

**Response:** `200 OK`
```json
{
  "status": "success",
  "summary": {
    "total_rows": 100,
    "imported": 95,
    "updated": 5,
    "failed": 0
  },
  "errors": []
}
```

---

### 2. Polling Booths

**List Polling Booths**

`GET /api/polling-booths/`

**Access:** Authenticated

**Query Parameters:**
- `constituency` - Filter by constituency ID
- `ward` - Filter by ward ID
- `search` - Search by name, number, or address
- `accessible` - Filter: `true` for accessible booths only
- `ordering` - Sort by field
- `bbox` - Bounding box filter: `min_lng,min_lat,max_lng,max_lat`

**Response:** `200 OK`
```json
{
  "count": 5000,
  "next": "http://api.example.com/api/polling-booths/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "organization": {
        "id": "uuid",
        "name": "TVK Party"
      },
      "constituency": {
        "id": "uuid",
        "name": "Chennai Central",
        "code": "TN-AC-001"
      },
      "ward": {
        "id": "uuid",
        "name": "Anna Nagar Ward 1",
        "code": "TN-AC-001-W-001"
      },
      "booth_number": "001",
      "name": "Government High School Anna Nagar",
      "address": "123 Main St, Anna Nagar, Chennai - 600040",
      "latitude": 13.08270000,
      "longitude": 80.27070000,
      "landmark": "Near Anna Nagar Tower",
      "total_voters": 1500,
      "male_voters": 750,
      "female_voters": 750,
      "transgender_voters": 0,
      "accessible": true,
      "parking_available": true,
      "facilities": {
        "toilets": true,
        "drinking_water": true,
        "wheelchair_ramp": true
      },
      "is_active": true,
      "created_at": "2025-11-01T10:00:00Z"
    }
  ]
}
```

**Get Single Booth**

`GET /api/polling-booths/{id}/`

**Get Booth Statistics**

`GET /api/polling-booths/{id}/stats/`

**Response:**
```json
{
  "booth": {
    "id": "uuid",
    "name": "Government High School Anna Nagar",
    "booth_number": "001"
  },
  "stats": {
    "total_voters": 1500,
    "feedback_count": 45,
    "field_reports_count": 8,
    "sentiment_score": 0.68,
    "last_activity": "2025-11-09T08:30:00Z"
  }
}
```

**Create Booth**

`POST /api/polling-booths/`

**Access:** Admin only

**Request:**
```json
{
  "constituency": "constituency-uuid",
  "ward": "ward-uuid",
  "booth_number": "001",
  "name": "Government High School",
  "address": "123 Main St",
  "latitude": 13.0827,
  "longitude": 80.2707,
  "total_voters": 1500,
  "male_voters": 750,
  "female_voters": 750,
  "accessible": true,
  "landmark": "Near Tower"
}
```

**Response:** `201 Created`

**Update Booth**

`PATCH /api/polling-booths/{id}/`

**Delete Booth**

`DELETE /api/polling-booths/{id}/`

**Bulk Upload Booths (CSV)**

`POST /api/polling-booths/bulk-upload/`

**Access:** Admin only

**Request:** `multipart/form-data`
```
file: booths.csv
```

**Response:** `200 OK`
```json
{
  "status": "success",
  "summary": {
    "total_rows": 500,
    "imported": 485,
    "updated": 10,
    "failed": 5
  },
  "errors": [
    {
      "row": 23,
      "error": "Invalid GPS coordinates"
    }
  ]
}
```

**Get Booths by Bounding Box (Map View)**

`GET /api/polling-booths/?bbox=80.25,13.05,80.30,13.10`

Returns booths within the specified geographic area (for map rendering).

---

## Feedback and Reports

### 1. Citizen Feedback

**Submit Feedback (Public)**

`POST /api/feedback/`

**Access:** Public (no authentication required)

**Request:**
```json
{
  "citizen_name": "Ravi Kumar",
  "citizen_age": 35,
  "citizen_phone": "+919876543210",
  "citizen_email": "ravi@example.com",
  "state": "state-uuid",
  "district": "district-uuid",
  "constituency": "constituency-uuid",
  "ward": "Ward 123",
  "booth_number": "B456",
  "detailed_location": "123 Main Street, Near Temple",
  "issue_category": "issue-uuid",
  "message_text": "We need better roads in our area.",
  "expectations": "TVK should prioritize infrastructure.",
  "voter_segment": "segment-uuid"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "feedback_id": "a1b2c3d4-e5f6-7890",
  "citizen_name": "Ravi Kumar",
  "status": "pending",
  "submitted_at": "2025-11-09T10:30:00Z",
  "message": "Thank you for your feedback"
}
```

**List Feedback (Authenticated)**

`GET /api/feedback/`

**Access:** Authenticated (role-filtered)

**Query Parameters:**
- `status` - Filter: `pending`, `reviewed`, `escalated`, `resolved`
- `ward` - Filter by ward code
- `constituency` - Filter by constituency ID
- `issue_category` - Filter by issue ID
- `search` - Search in message text
- `ordering` - Sort: `-submitted_at`, `ai_urgency`
- `date_from` - Filter from date
- `date_to` - Filter to date

**Response:**
```json
{
  "count": 250,
  "results": [
    {
      "id": "uuid",
      "feedback_id": "a1b2c3d4-e5f6-7890",
      "citizen_name": "Ravi Kumar",
      "citizen_age": 35,
      "ward": "Ward 123",
      "constituency_name": "Chennai Central",
      "district_name": "Chennai",
      "issue_name": "Infrastructure",
      "message_text": "We need better roads...",
      "status": "pending",
      "ai_sentiment_polarity": "negative",
      "ai_urgency": "high",
      "submitted_at": "2025-11-09T10:30:00Z",
      "reviewed_at": null,
      "reviewed_by": null
    }
  ]
}
```

**Get Feedback Details**

`GET /api/feedback/{id}/`

**Update Feedback Status**

`PATCH /api/feedback/{id}/`

**Access:** Manager or above

**Request:**
```json
{
  "status": "reviewed",
  "review_notes": "Issue forwarded to district office"
}
```

**Mark as Reviewed**

`POST /api/feedback/{id}/mark_reviewed/`

**Escalate Feedback**

`POST /api/feedback/{id}/escalate/`

**Get Feedback Statistics**

`GET /api/feedback/stats/`

**Response:**
```json
{
  "total": 1500,
  "by_status": {
    "pending": 450,
    "reviewed": 800,
    "escalated": 150,
    "resolved": 100
  },
  "by_urgency": {
    "low": 300,
    "medium": 600,
    "high": 400,
    "urgent": 200
  },
  "pending_count": 450,
  "escalated_count": 150
}
```

---

### 2. Field Reports

**Submit Field Report**

`POST /api/field-reports/`

**Access:** Authenticated (Volunteer or above)

**Request:**
```json
{
  "state": "state-uuid",
  "district": "district-uuid",
  "constituency": "constituency-uuid",
  "ward": "Ward 123",
  "booth_number": "B456",
  "report_type": "daily_summary",
  "title": "Daily Report - November 9",
  "positive_reactions": [
    "People happy with new schemes",
    "Good response to campaign"
  ],
  "negative_reactions": [
    "Concerns about unemployment",
    "Water supply issues"
  ],
  "key_issues": ["issue-uuid-1", "issue-uuid-2"],
  "voter_segments_met": ["segment-uuid-1"],
  "crowd_size": 150,
  "quotes": ["We support TVK's vision"],
  "notes": "Overall positive sentiment"
}
```

**Response:** `201 Created`

**List Field Reports**

`GET /api/field-reports/`

**Query Parameters:**
- `report_type` - Filter: `daily_summary`, `event_feedback`, `issue_report`, `competitor_activity`
- `verification_status` - Filter: `pending`, `verified`, `rejected`
- `volunteer` - Filter by volunteer ID
- `ward` - Filter by ward code

**My Reports**

`GET /api/field-reports/my_reports/`

Returns reports submitted by current user.

**Verify Field Report**

`POST /api/field-reports/{id}/verify/`

**Access:** Manager or above

**Request:**
```json
{
  "verification_notes": "Report verified. Data looks accurate."
}
```

---

## Analytics

### 1. Dashboard Overview

`GET /api/analytics/overview/`

**Access:** Authenticated

**Response:**
```json
{
  "total_feedback": 5000,
  "total_field_reports": 1250,
  "pending_feedback": 750,
  "escalated_feedback": 150,
  "recent_feedback_count": 1200,
  "total_constituencies": 234,
  "total_districts": 38,
  "total_wards": 5000,
  "total_booths": 50000,
  "overall_sentiment": 0.65,
  "sentiment_trend": "positive"
}
```

### 2. State Analytics

`GET /api/analytics/state/{state_code}/`

**Example:** `/api/analytics/state/TN/`

**Response:**
```json
{
  "state": {
    "code": "TN",
    "name": "Tamil Nadu",
    "total_districts": 38,
    "total_constituencies": 234
  },
  "total_feedback": 15000,
  "by_status": {
    "pending": 4500,
    "reviewed": 8000,
    "escalated": 1500,
    "resolved": 1000
  },
  "top_issues": [
    {
      "issue_category__name": "Youth Employment",
      "count": 3500,
      "avg_sentiment": 0.35
    }
  ],
  "by_district": [
    {
      "district__name": "Chennai",
      "district__id": "uuid",
      "count": 4500,
      "avg_sentiment": 0.55
    }
  ],
  "by_segment": [
    {
      "voter_segment__name": "Youth (18-25)",
      "count": 5000,
      "avg_sentiment": 0.38
    }
  ]
}
```

### 3. District Analytics

`GET /api/analytics/district/{district_id}/`

### 4. Constituency Analytics

`GET /api/analytics/constituency/{constituency_code}/`

**Example:** `/api/analytics/constituency/TN-AC-001/`

**Response:**
```json
{
  "constituency": {
    "code": "TN-AC-001",
    "name": "Chennai Central",
    "number": 1,
    "district": "Chennai"
  },
  "total_feedback": 450,
  "by_status": { ... },
  "by_urgency": { ... },
  "top_issues": [ ... ],
  "voter_segments": [ ... ],
  "sentiment_score": 0.65,
  "sentiment_trend": "positive"
}
```

---

## User Management

### 1. List Users

`GET /api/users/`

**Access:** Admin only

**Query Parameters:**
- `role` - Filter by role
- `organization` - Filter by organization
- `is_active` - Filter: `true`/`false`
- `search` - Search by name, email, username

**Response:**
```json
{
  "count": 150,
  "results": [
    {
      "id": "uuid",
      "email": "user@example.com",
      "username": "johndoe",
      "first_name": "John",
      "last_name": "Doe",
      "role": "analyst",
      "organization": {
        "id": "uuid",
        "name": "TVK Party"
      },
      "is_active": true,
      "created_at": "2025-10-01T10:00:00Z"
    }
  ]
}
```

### 2. Create User

`POST /api/users/`

**Access:** Admin only

### 3. Update User

`PATCH /api/users/{id}/`

### 4. Delete User

`DELETE /api/users/{id}/`

### 5. Assign Constituency

`POST /api/users/{id}/assign-constituency/`

**Request:**
```json
{
  "constituency_id": "uuid"
}
```

---

## Error Codes

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 204 | No Content | Resource deleted successfully |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

### Application Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Input validation failed |
| `AUTHENTICATION_REQUIRED` | Must be logged in |
| `INSUFFICIENT_PERMISSIONS` | User lacks required permissions |
| `RESOURCE_NOT_FOUND` | Requested resource doesn't exist |
| `DUPLICATE_ENTRY` | Resource already exists |
| `INVALID_CREDENTIALS` | Wrong username/password |
| `TOKEN_EXPIRED` | JWT token has expired |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `CSV_VALIDATION_ERROR` | CSV file validation failed |
| `GEOLOCATION_ERROR` | Invalid GPS coordinates |

**Error Response Example:**
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "latitude": ["Must be between 8.0 and 37.0"],
      "voter_count": ["Cannot be negative"]
    }
  }
}
```

---

## Rate Limiting

**Default Limits:**
- Anonymous users: 100 requests/hour
- Authenticated users: 1000 requests/hour
- Admin users: 5000 requests/hour

**Rate Limit Headers:**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1699516800
```

**When rate limit is exceeded:**
```http
HTTP/1.1 429 Too Many Requests
Retry-After: 3600

{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Try again in 3600 seconds."
  }
}
```

---

## Examples

### Complete Workflow: Upload Booths

**Step 1: Login**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"yourpassword"}'
```

Save the `access` token.

**Step 2: Get Constituency ID**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://127.0.0.1:8000/api/constituencies/?search=Chennai%20Central
```

Note the constituency `id`.

**Step 3: Upload Booths CSV**
```bash
curl -X POST http://127.0.0.1:8000/api/polling-booths/bulk-upload/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@booths.csv"
```

**Step 4: Verify on Map**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://127.0.0.1:8000/api/polling-booths/?constituency=CONSTITUENCY_ID"
```

---

### Complete Workflow: Get Analytics

**Step 1: Login** (same as above)

**Step 2: Get Overall Dashboard**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://127.0.0.1:8000/api/analytics/overview/
```

**Step 3: Get State Analytics**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://127.0.0.1:8000/api/analytics/state/TN/
```

**Step 4: Get Constituency Analytics**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://127.0.0.1:8000/api/analytics/constituency/TN-AC-001/
```

---

### JavaScript Example (Fetch API)

```javascript
// Login
const loginResponse = await fetch('http://127.0.0.1:8000/api/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'admin',
    password: 'yourpassword'
  })
});

const { access } = await loginResponse.json();

// Get wards
const wardsResponse = await fetch('http://127.0.0.1:8000/api/wards/', {
  headers: { 'Authorization': `Bearer ${access}` }
});

const wards = await wardsResponse.json();
console.log(wards.results);
```

---

### Python Example (requests)

```python
import requests

# Login
response = requests.post('http://127.0.0.1:8000/api/auth/login/', json={
    'username': 'admin',
    'password': 'yourpassword'
})
token = response.json()['access']

# Get booths
headers = {'Authorization': f'Bearer {token}'}
response = requests.get('http://127.0.0.1:8000/api/polling-booths/', headers=headers)
booths = response.json()

print(f"Total booths: {booths['count']}")
```

---

## Webhooks (Future)

**Coming Soon:**
- Webhook notifications for new feedback
- Real-time alerts via webhooks
- Integration with external systems

---

## Support

**API Issues:**
- Email: api-support@pulseofpeople.com
- Docs: https://docs.pulseofpeople.com
- Status Page: https://status.pulseofpeople.com

---

**Last Updated**: November 9, 2025
**Version**: 1.0
**For**: Pulse of People Platform
