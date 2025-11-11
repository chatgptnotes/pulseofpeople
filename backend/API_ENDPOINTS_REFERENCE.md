# API Endpoints Reference - Workstream 2

Quick reference guide for all Core Platform API endpoints.

## Base URL
```
Development: http://127.0.0.1:8000/api
Production: https://pulseofpeople-production.up.railway.app/api
```

## Authentication
All endpoints require JWT authentication:
```bash
# Login
POST /api/auth/login/
{
  "email": "user@example.com",
  "password": "password123"
}

# Response
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

# Use in headers
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

## 1. VOTERS

### List Voters
```
GET /api/voters/
GET /api/voters/?party_affiliation=tvk
GET /api/voters/?sentiment=supporter
GET /api/voters/?search=john
GET /api/voters/?ordering=-created_at
GET /api/voters/?page=2
```

### Create Voter
```
POST /api/voters/
{
  "voter_id": "VOTER123456",
  "first_name": "John",
  "last_name": "Doe",
  "age": 35,
  "gender": "male",
  "phone": "9876543210",
  "ward": "Ward 5",
  "constituency": 1,
  "district": 1,
  "state": 1,
  "party_affiliation": "tvk",
  "sentiment": "supporter"
}
```

### Get Voter Details
```
GET /api/voters/{id}/
```

### Update Voter
```
PATCH /api/voters/{id}/
{
  "sentiment": "strong_supporter",
  "notes": "Very engaged, attended 3 rallies"
}
```

### Delete Voter
```
DELETE /api/voters/{id}/
```

### Voter Stats
```
GET /api/voters/stats/
# Returns: total, by_party, by_sentiment, by_influence, opinion_leaders
```

### Voters by Sentiment
```
GET /api/voters/by_sentiment/
# Returns: breakdown with counts and percentages
```

### Mark Voter Contacted
```
POST /api/voters/{id}/mark_contacted/
```

---

## 2. VOTER INTERACTIONS

### List Interactions
```
GET /api/voter-interactions/
GET /api/voter-interactions/?interaction_type=phone_call
GET /api/voter-interactions/?sentiment=positive
GET /api/voter-interactions/?voter=123
```

### Create Interaction
```
POST /api/voter-interactions/
{
  "voter": 123,
  "interaction_type": "phone_call",
  "duration_minutes": 15,
  "sentiment": "positive",
  "issues_discussed": ["Education", "Healthcare"],
  "follow_up_required": true,
  "follow_up_date": "2025-11-15",
  "notes": "Voter is very supportive of education policies"
}
```

### Interaction Stats
```
GET /api/voter-interactions/stats/
# Returns: total, by_type, by_sentiment, follow_ups_pending, avg_duration
```

### Pending Follow-ups
```
GET /api/voter-interactions/pending_followups/
# Returns: interactions requiring follow-up in next 7 days
```

---

## 3. CAMPAIGNS

### List Campaigns
```
GET /api/campaigns/
GET /api/campaigns/?status=active
GET /api/campaigns/?campaign_type=election
```

### Create Campaign
```
POST /api/campaigns/
{
  "campaign_name": "2025 Assembly Election - District 5",
  "campaign_type": "election",
  "start_date": "2025-01-01",
  "end_date": "2025-03-31",
  "status": "planning",
  "budget": 5000000,
  "target_constituency": 15,
  "campaign_manager": 5,
  "team_members": [5, 10, 15, 20],
  "goals": {
    "voter_outreach": 50000,
    "events": 25,
    "social_reach": 500000
  }
}
```

### Campaign Stats
```
GET /api/campaigns/stats/
# Returns: total, active, by_type, by_status, total_budget, total_spent
```

### Update Campaign Metrics
```
POST /api/campaigns/{id}/update_metrics/
{
  "metrics": {
    "voters_contacted": 15000,
    "events_held": 10,
    "social_reach": 250000
  }
}
```

### Campaign Performance
```
GET /api/campaigns/{id}/performance/
# Returns: budget_utilization, team_size, events_count, social_posts_count, metrics
```

---

## 4. SOCIAL MEDIA POSTS

### List Posts
```
GET /api/social-posts/
GET /api/social-posts/?platform=facebook
GET /api/social-posts/?is_published=true
GET /api/social-posts/?campaign=5
```

### Create Post
```
POST /api/social-posts/
{
  "platform": "facebook",
  "post_content": "Join us for the town hall meeting on Saturday!",
  "posted_at": "2025-11-10T10:00:00Z",
  "campaign": 5,
  "hashtags": ["#TVK2025", "#TamilNadu"],
  "is_published": true
}
```

### Social Media Stats
```
GET /api/social-posts/stats/
# Returns: total_posts, by_platform, total_reach, total_engagement, total_likes, total_shares
```

### Top Performing Posts
```
GET /api/social-posts/top_performing/
# Returns: Top 10 posts by engagement
```

---

## 5. ALERTS

### List Alerts
```
GET /api/alerts/
GET /api/alerts/?priority=urgent
GET /api/alerts/?target_role=admin
GET /api/alerts/?is_read=false
```

### Create Alert
```
POST /api/alerts/
{
  "alert_type": "urgent",
  "title": "Rally Location Changed",
  "message": "The rally scheduled for tomorrow has been moved to Gandhi Ground.",
  "priority": "high",
  "target_role": "volunteer",
  "constituency": 15,
  "action_required": true
}
```

### Mark Alert as Read
```
POST /api/alerts/{id}/mark_read/
```

### Get Unread Alerts
```
GET /api/alerts/unread/
```

---

## 6. EVENTS

### List Events
```
GET /api/events/
GET /api/events/?event_type=rally
GET /api/events/?status=planned
GET /api/events/?organizer=5
```

### Create Event
```
POST /api/events/
{
  "event_name": "Town Hall Meeting - Ward 10",
  "event_type": "town_hall",
  "start_datetime": "2025-11-15T18:00:00Z",
  "end_datetime": "2025-11-15T20:00:00Z",
  "location": "Community Center, Ward 10",
  "ward": "Ward 10",
  "constituency": 15,
  "expected_attendance": 500,
  "organizer": 5,
  "volunteers": [10, 15, 20],
  "budget": 50000
}
```

### Event Stats
```
GET /api/events/stats/
# Returns: total, by_type, by_status, total_budget, total_expenses, total_attendance
```

### Upcoming Events
```
GET /api/events/upcoming/
# Returns: Next 10 planned events
```

### Mark Event Complete
```
POST /api/events/{id}/mark_completed/
{
  "actual_attendance": 450
}
```

---

## 7. VOLUNTEERS

### List Volunteers
```
GET /api/volunteers/
GET /api/volunteers/?is_active=true
GET /api/volunteers/?assigned_constituency=15
```

### Create Volunteer
```
POST /api/volunteers/
{
  "user": 25,
  "volunteer_id": "VOL001",
  "skills": ["Canvassing", "Social Media", "Event Management"],
  "availability": {
    "weekdays": ["evening"],
    "weekends": ["morning", "afternoon"]
  },
  "assigned_ward": "Ward 10",
  "assigned_constituency": 15
}
```

### Volunteer Stats
```
GET /api/volunteers/stats/
# Returns: total, active, total_hours, total_tasks, avg_rating
```

### Log Volunteer Hours
```
POST /api/volunteers/{id}/log_hours/
{
  "hours": 4.5
}
```

---

## 8. EXPENSES

### List Expenses
```
GET /api/expenses/
GET /api/expenses/?expense_type=travel
GET /api/expenses/?status=pending
GET /api/expenses/?campaign=5
```

### Create Expense
```
POST /api/expenses/
{
  "expense_type": "event",
  "amount": 15000,
  "description": "Sound system rental for rally",
  "campaign": 5,
  "event": 10
}
```

### Expense Stats
```
GET /api/expenses/stats/
# Returns: total_expenses, by_type, by_status, total_amount, pending_amount, approved_amount
```

### Approve Expense
```
POST /api/expenses/{id}/approve/
```

### Reject Expense
```
POST /api/expenses/{id}/reject/
```

### Pending Approvals
```
GET /api/expenses/pending_approvals/
```

---

## 9. ORGANIZATIONS

### List Organizations
```
GET /api/organizations/
GET /api/organizations/?organization_type=party
GET /api/organizations/?is_active=true
```

### Create Organization
```
POST /api/organizations/
{
  "name": "TVK Tamil Nadu",
  "slug": "tvk-tn",
  "organization_type": "party",
  "contact_email": "contact@tvk.org",
  "contact_phone": "044-12345678",
  "city": "Chennai",
  "state": "Tamil Nadu",
  "subscription_plan": "pro"
}
```

### Organization Stats
```
GET /api/organizations/stats/
# Returns: total, active, by_type, by_plan
```

---

## Query Parameters (All Endpoints)

### Pagination
```
?page=2
?page_size=50
```

### Filtering
```
?{field_name}={value}
?status=active
?created_at__gte=2025-01-01
```

### Search
```
?search={query}
?search=john
```

### Ordering
```
?ordering={field}
?ordering=-created_at  (descending)
?ordering=first_name   (ascending)
```

---

## Response Format

### Success (List)
```json
{
  "count": 1000,
  "next": "http://api/voters/?page=2",
  "previous": null,
  "results": [...]
}
```

### Success (Detail)
```json
{
  "id": 123,
  "voter_id": "VOTER123456",
  "first_name": "John",
  ...
}
```

### Error
```json
{
  "detail": "Not found."
}
```

```json
{
  "field_name": ["Error message"]
}
```

---

## HTTP Status Codes

- `200 OK` - Success
- `201 Created` - Resource created
- `204 No Content` - Success, no response body
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## Role-Based Data Visibility

### Superadmin
- Sees: ALL data

### Admin (State level)
- Sees: Entire state data

### Manager (District level)
- Sees: Their district data

### Analyst/User
- Sees: Only data they created

### Booth Agent
- Sees: Only their assigned wards/booths

---

## Testing with cURL

### Example: Get all voters
```bash
curl -X GET http://127.0.0.1:8000/api/voters/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Example: Create voter
```bash
curl -X POST http://127.0.0.1:8000/api/voters/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "voter_id": "VOTER123456",
    "first_name": "John",
    "last_name": "Doe",
    "age": 35,
    "gender": "male",
    "phone": "9876543210",
    "ward": "Ward 5",
    "constituency": 1,
    "district": 1,
    "state": 1,
    "party_affiliation": "tvk",
    "sentiment": "supporter"
  }'
```

---

## Testing with Postman

1. Create environment variables:
   - `base_url`: `http://127.0.0.1:8000`
   - `access_token`: (get from login)

2. Add to request headers:
   - `Authorization`: `Bearer {{access_token}}`
   - `Content-Type`: `application/json`

3. Import collection (create from this reference)

---

**Last Updated:** 2025-11-09
**Version:** 1.0
**Total Endpoints:** 90+
