# 🚀 TVK Political Platform - API Documentation

## 📋 Table of Contents
1. [Getting Started](#getting-started)
2. [Authentication](#authentication)
3. [Master Data APIs](#master-data-apis)
4. [Feedback Collection APIs](#feedback-collection-apis)
5. [Field Reports APIs](#field-reports-apis)
6. [Analytics APIs](#analytics-apis)
7. [Testing with cURL](#testing-with-curl)

---

## 🎯 Getting Started

### Base URL
```
http://127.0.0.1:8000/api/
```

### Quick Test
```bash
curl http://127.0.0.1:8000/api/health/
# Response: {"status": "ok"}
```

---

## 🔐 Authentication

### Register New User
```bash
POST /api/auth/register/
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "testpass123",
  "password_confirm": "testpass123"
}
```

### Login (Get JWT Token)
```bash
POST /api/auth/login/
Content-Type: application/json

{
  "username": "testuser",
  "password": "testpass123"
}

# Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Using Token in Requests
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" http://127.0.0.1:8000/api/feedback/
```

---

## 📚 Master Data APIs

### 1. States
```bash
# List all states
GET /api/states/

# Get specific state
GET /api/states/{id}/
```

**Example Response:**
```json
[
  {
    "id": 1,
    "name": "Tamil Nadu",
    "code": "TN",
    "capital": "Chennai",
    "region": "South",
    "total_districts": 38,
    "total_constituencies": 234
  }
]
```

### 2. Districts
```bash
# List all districts
GET /api/districts/

# Filter by state
GET /api/districts/?state=TN

# Get specific district
GET /api/districts/{id}/
```

### 3. Constituencies
```bash
# List all constituencies (234 in Tamil Nadu)
GET /api/constituencies/

# Filter by state and type
GET /api/constituencies/?state=TN&type=assembly

# Get specific constituency
GET /api/constituencies/{id}/
```

### 4. Issue Categories (TVK's 9 Priorities)
```bash
# List all issues
GET /api/issue-categories/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Social Justice & Caste Issues",
    "priority": 9,
    "color": "#E74C3C",
    "icon": "balance"
  },
  {
    "id": 2,
    "name": "Women's Safety & Empowerment",
    "priority": 8,
    "color": "#9B59B6",
    "icon": "female"
  }
  // ... 7 more
]
```

### 5. Voter Segments
```bash
# List all voter segments
GET /api/voter-segments/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Fishermen Community",
    "priority_level": 9,
    "estimated_population": 500000
  },
  {
    "id": 2,
    "name": "Farmers",
    "priority_level": 8,
    "estimated_population": 10000000
  }
  // ... more segments
]
```

### 6. Political Parties
```bash
# List all parties
GET /api/political-parties/
```

---

## 📝 Feedback Collection APIs

### Submit Citizen Feedback (PUBLIC - No Auth Required)
```bash
POST /api/feedback/
Content-Type: application/json

{
  "citizen_name": "Ravi Kumar",
  "citizen_age": 35,
  "citizen_phone": "+919876543210",
  "citizen_email": "ravi@example.com",
  "state": 1,
  "district": 3,
  "constituency": 5,
  "ward": "Ward 123",
  "booth_number": "B456",
  "detailed_location": "123 Main Street, Near Temple",
  "issue_category": 1,
  "message_text": "We need better roads in our area. The current condition is very bad during monsoon.",
  "expectations": "TVK party should prioritize road infrastructure in our ward.",
  "voter_segment": 2
}
```

**Response:**
```json
{
  "id": 1,
  "feedback_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "citizen_name": "Ravi Kumar",
  "status": "pending",
  "submitted_at": "2025-01-07T12:30:00Z"
}
```

### List Feedback (Auth Required, Role-Filtered)
```bash
GET /api/feedback/
Authorization: Bearer YOUR_TOKEN

# Filter by status
GET /api/feedback/?status=pending

# Filter by ward
GET /api/feedback/?search=Ward%20123

# Sort by date
GET /api/feedback/?ordering=-submitted_at
```

**Response:**
```json
{
  "count": 25,
  "results": [
    {
      "id": 1,
      "feedback_id": "...",
      "citizen_name": "Ravi Kumar",
      "ward": "Ward 123",
      "constituency_name": "Perambur",
      "district_name": "Chennai",
      "issue_name": "Social Justice & Caste Issues",
      "status": "pending",
      "ai_sentiment_polarity": "negative",
      "ai_urgency": "high",
      "submitted_at": "2025-01-07T12:30:00Z"
    }
  ]
}
```

### Get Feedback Details
```bash
GET /api/feedback/{id}/
Authorization: Bearer YOUR_TOKEN
```

### Update Feedback Status
```bash
PATCH /api/feedback/{id}/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "status": "reviewed",
  "review_notes": "Issue forwarded to district office."
}
```

### Mark as Reviewed
```bash
POST /api/feedback/{id}/mark_reviewed/
Authorization: Bearer YOUR_TOKEN
```

### Escalate Feedback
```bash
POST /api/feedback/{id}/escalate/
Authorization: Bearer YOUR_TOKEN
```

### Get Feedback Statistics
```bash
GET /api/feedback/stats/
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "total": 150,
  "by_status": {
    "pending": 45,
    "reviewed": 80,
    "escalated": 15,
    "resolved": 10
  },
  "by_urgency": {
    "low": 30,
    "medium": 60,
    "high": 40,
    "urgent": 20
  },
  "pending_count": 45,
  "escalated_count": 15
}
```

---

## 📊 Field Reports APIs

### Submit Field Report (Auth Required)
```bash
POST /api/field-reports/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "state": 1,
  "district": 3,
  "constituency": 5,
  "ward": "Ward 123",
  "booth_number": "B456",
  "report_type": "daily_summary",
  "title": "Daily Report - January 7",
  "positive_reactions": ["People happy with new schemes", "Good response to door-to-door campaign"],
  "negative_reactions": ["Concerns about unemployment", "Water supply issues"],
  "key_issues": [1, 5],
  "voter_segments_met": [1, 2],
  "crowd_size": 150,
  "quotes": ["We support TVK's vision for Tamil Nadu"],
  "notes": "Overall positive sentiment in the ward today."
}
```

### List Field Reports
```bash
GET /api/field-reports/
Authorization: Bearer YOUR_TOKEN

# Filter by type
GET /api/field-reports/?search=daily_summary

# My reports only
GET /api/field-reports/my_reports/
```

### Verify Field Report
```bash
POST /api/field-reports/{id}/verify/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "verification_notes": "Report verified. Data looks accurate."
}
```

---

## 📈 Analytics APIs

### 1. Dashboard Overview
```bash
GET /api/analytics/overview/
```

**Response:**
```json
{
  "total_feedback": 500,
  "total_field_reports": 250,
  "pending_feedback": 75,
  "escalated_feedback": 15,
  "recent_feedback_count": 120,
  "total_constituencies": 234,
  "total_districts": 38
}
```

### 2. Constituency Analytics
```bash
GET /api/analytics/constituency/{code}/
Authorization: Bearer YOUR_TOKEN

# Example
GET /api/analytics/constituency/TN005/
```

**Response:**
```json
{
  "constituency": {
    "code": "TN005",
    "name": "Perambur",
    "number": 5,
    "district": "Chennai"
  },
  "total_feedback": 45,
  "by_status": {
    "pending": 12,
    "reviewed": 25,
    "escalated": 5,
    "resolved": 3
  },
  "by_urgency": {
    "low": 10,
    "medium": 20,
    "high": 10,
    "urgent": 5
  },
  "top_issues": [
    {
      "issue_category__name": "Youth Employment & Education",
      "count": 15,
      "avg_sentiment": 0.35
    },
    {
      "issue_category__name": "Social Justice & Caste Issues",
      "count": 12,
      "avg_sentiment": 0.42
    }
  ],
  "voter_segments": [
    {
      "voter_segment__name": "Youth (18-25)",
      "count": 20,
      "avg_sentiment": 0.38
    }
  ]
}
```

### 3. District Analytics
```bash
GET /api/analytics/district/{district_id}/
Authorization: Bearer YOUR_TOKEN

# Example
GET /api/analytics/district/3/
```

### 4. State Analytics
```bash
GET /api/analytics/state/{state_code}/
Authorization: Bearer YOUR_TOKEN

# Example
GET /api/analytics/state/TN/
```

**Response:**
```json
{
  "state": {
    "code": "TN",
    "name": "Tamil Nadu",
    "total_districts": 38,
    "total_constituencies": 234
  },
  "total_feedback": 1500,
  "by_status": {...},
  "top_issues": [...],
  "by_district": [
    {
      "district__name": "Chennai",
      "district__id": 3,
      "count": 450,
      "avg_sentiment": 0.55
    }
  ],
  "by_segment": [...]
}
```

---

## 🧪 Testing with cURL

### Step 1: Load Seed Data
```bash
python manage.py seed_political_data
```

### Step 2: Create Superuser (if not done)
```bash
python manage.py createsuperuser
```

### Step 3: Get Token
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your_password"}'
```

Save the `access` token from response.

### Step 4: Test Public Feedback Submission
```bash
curl -X POST http://127.0.0.1:8000/api/feedback/ \
  -H "Content-Type: application/json" \
  -d '{
    "citizen_name": "Test User",
    "citizen_age": 30,
    "citizen_phone": "9876543210",
    "state": 1,
    "district": 3,
    "ward": "Test Ward",
    "issue_category": 1,
    "message_text": "This is a test feedback message."
  }'
```

### Step 5: List Feedback (with Auth)
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://127.0.0.1:8000/api/feedback/
```

### Step 6: Get Analytics
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://127.0.0.1:8000/api/analytics/overview/
```

---

## 📊 Role-Based Access

### Admin3 (Booth Agent)
- Can submit field reports
- Can see feedback only from their assigned wards/booths
- Can see their own reports

### Admin2 (District Head)
- Can see all feedback in their district
- Can see all field reports in their district
- Can verify field reports

### Admin1 (State Level - Vijay)
- Can see all feedback in the state
- Can see all field reports in the state
- Full analytics access

### Superadmin
- Can see everything
- Full CRUD access

---

## 🎯 Next Steps

1. **Load seed data:**
   ```bash
   python manage.py seed_political_data
   ```

2. **Test all endpoints** using the examples above

3. **Frontend Integration:**
   - Use the access token in Authorization header
   - Handle 401 (Unauthorized) errors
   - Implement token refresh logic

4. **Production Deployment:**
   - Update ALLOWED_HOSTS in settings.py
   - Set DEBUG=False
   - Use PostgreSQL instead of SQLite
   - Deploy to Railway/Render

---

## ✅ Available Endpoints Summary

```
# Authentication
POST   /api/auth/login/
POST   /api/auth/register/
POST   /api/auth/refresh/

# Master Data (Public)
GET    /api/states/
GET    /api/districts/
GET    /api/constituencies/
GET    /api/issue-categories/
GET    /api/voter-segments/
GET    /api/political-parties/

# Feedback (Mixed Auth)
POST   /api/feedback/                    # Public
GET    /api/feedback/                    # Auth Required
GET    /api/feedback/{id}/               # Auth Required
PATCH  /api/feedback/{id}/               # Auth Required
POST   /api/feedback/{id}/mark_reviewed/ # Auth Required
POST   /api/feedback/{id}/escalate/      # Auth Required
GET    /api/feedback/stats/              # Auth Required

# Field Reports (Auth Required)
POST   /api/field-reports/
GET    /api/field-reports/
GET    /api/field-reports/{id}/
PATCH  /api/field-reports/{id}/
POST   /api/field-reports/{id}/verify/
GET    /api/field-reports/my_reports/

# Analytics (Auth Required)
GET    /api/analytics/overview/
GET    /api/analytics/constituency/{code}/
GET    /api/analytics/district/{id}/
GET    /api/analytics/state/{code}/
```

---

**🎉 Your TVK Political Platform Backend is Ready!**
