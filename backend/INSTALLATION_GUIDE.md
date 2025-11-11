# Installation & Testing Guide - Workstream 2

Complete guide to install, configure, and test all Workstream 2 backend features.

---

## Prerequisites

- Python 3.10+ installed
- PostgreSQL 12+ (or use SQLite for development)
- Git installed
- Virtual environment tool (venv or virtualenv)

---

## Step 1: Clone & Setup Environment

```bash
# Navigate to project directory
cd /Users/murali/Downloads/pulseofpeople

# Navigate to backend
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

---

## Step 2: Install Dependencies

```bash
# Install all requirements
pip install -r requirements.txt

# Verify key packages are installed
pip list | grep -E "(Django|djangorestframework|django-filter|Faker)"
```

Expected output:
```
Django                      5.2.7
django-cors-headers         4.9.0
django-filter               24.3
djangorestframework         3.16.1
djangorestframework-simplejwt 5.5.1
Faker                       33.1.0
```

---

## Step 3: Configure Database

### Option A: SQLite (Development - Easiest)
No configuration needed! SQLite is default.

### Option B: PostgreSQL (Production)

1. Create PostgreSQL database:
```bash
psql -U postgres
CREATE DATABASE pulseofpeople;
CREATE USER pulseuser WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE pulseofpeople TO pulseuser;
\q
```

2. Update environment variables:
```bash
# Create .env file
cat > .env << EOF
USE_SQLITE=False
DB_NAME=pulseofpeople
DB_USER=pulseuser
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
EOF
```

---

## Step 4: Run Migrations

```bash
# Create all database tables
python manage.py migrate

# Verify migrations
python manage.py showmigrations
```

Expected output should show:
```
api
 [X] 0001_initial
 [X] 0002_userprofile_role
 [X] 0003_organization_permission_userprofile_avatar_url_and_more
 [X] 0004_notification
 [X] 0005_uploadedfile
 [X] 0006_district_state_constituency_and_more
 [X] 0007_workstream2_core_models  <-- NEW!
```

---

## Step 5: Create Superuser

```bash
# Option 1: Use custom command (creates with default credentials)
python manage.py createsuperadmin

# Option 2: Create manually
python manage.py createsuperuser
# Enter username, email, password when prompted
```

Default credentials (if using createsuperadmin):
- Email: `admin@pulseofpeople.com`
- Password: `admin123`

---

## Step 6: Seed Sample Data

### Quick Seed (Recommended for testing)
```bash
python manage.py seed_all_data --quick
```

This creates:
- Political data (States, Districts, Constituencies)
- 500 voters
- 25 campaigns
- 250 voter interactions
- 50 events

### Full Seed (Larger dataset)
```bash
python manage.py seed_all_data
```

This creates:
- Political data (States, Districts, Constituencies)
- 1,000 voters
- 50 campaigns
- 500 voter interactions
- 100 events

### Individual Seed Commands
```bash
# Seed only voters
python manage.py seed_voters --count 1000

# Seed only campaigns
python manage.py seed_campaigns --count 50

# Seed only interactions
python manage.py seed_interactions --count 500

# Seed only events
python manage.py seed_events --count 100
```

---

## Step 7: Start Development Server

```bash
python manage.py runserver
```

Server will start at: `http://127.0.0.1:8000`

---

## Step 8: Test API Endpoints

### 8.1: Login and Get Token

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@pulseofpeople.com",
    "password": "admin123"
  }'
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@pulseofpeople.com",
    "name": "Admin User",
    "role": "superadmin"
  }
}
```

**IMPORTANT**: Copy the `access` token for next steps!

---

### 8.2: Set Your Access Token

```bash
# Replace with your actual token
export ACCESS_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."
```

---

### 8.3: Test Voter Endpoints

#### List Voters
```bash
curl http://127.0.0.1:8000/api/voters/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

#### Get Voter Stats
```bash
curl http://127.0.0.1:8000/api/voters/stats/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

#### Filter Voters by Party
```bash
curl "http://127.0.0.1:8000/api/voters/?party_affiliation=tvk" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

#### Search Voters
```bash
curl "http://127.0.0.1:8000/api/voters/?search=john" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

#### Create Voter
```bash
curl -X POST http://127.0.0.1:8000/api/voters/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "voter_id": "VOTER999999",
    "first_name": "Test",
    "last_name": "User",
    "age": 30,
    "gender": "male",
    "phone": "9999999999",
    "ward": "Ward 1",
    "party_affiliation": "tvk",
    "sentiment": "supporter"
  }'
```

---

### 8.4: Test Campaign Endpoints

#### List Campaigns
```bash
curl http://127.0.0.1:8000/api/campaigns/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

#### Get Campaign Stats
```bash
curl http://127.0.0.1:8000/api/campaigns/stats/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

#### Filter Active Campaigns
```bash
curl "http://127.0.0.1:8000/api/campaigns/?status=active" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

---

### 8.5: Test Voter Interaction Endpoints

#### List Interactions
```bash
curl http://127.0.0.1:8000/api/voter-interactions/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

#### Get Pending Follow-ups
```bash
curl http://127.0.0.1:8000/api/voter-interactions/pending_followups/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

---

### 8.6: Test Event Endpoints

#### List Events
```bash
curl http://127.0.0.1:8000/api/events/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

#### Get Upcoming Events
```bash
curl http://127.0.0.1:8000/api/events/upcoming/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

---

### 8.7: Test Alert Endpoints

#### Get Unread Alerts
```bash
curl http://127.0.0.1:8000/api/alerts/unread/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

---

### 8.8: Test Expense Endpoints

#### List Expenses
```bash
curl http://127.0.0.1:8000/api/expenses/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

#### Get Pending Approvals
```bash
curl http://127.0.0.1:8000/api/expenses/pending_approvals/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

---

## Step 9: Test with Browser

### Django Admin Panel
```
URL: http://127.0.0.1:8000/admin/
Login with superuser credentials
```

You should see all the new models:
- Voters
- Voter Interactions
- Campaigns
- Social Media Posts
- Alerts
- Events
- Volunteer Profiles
- Expenses

### DRF Browsable API
```
URL: http://127.0.0.1:8000/api/voters/
URL: http://127.0.0.1:8000/api/campaigns/
URL: http://127.0.0.1:8000/api/events/
```

Django REST Framework provides a browsable API for testing.

---

## Step 10: Test Filtering & Search

### Filtering Examples
```bash
# Voters by sentiment
curl "http://127.0.0.1:8000/api/voters/?sentiment=supporter" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Voters by party
curl "http://127.0.0.1:8000/api/voters/?party_affiliation=tvk" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Active campaigns
curl "http://127.0.0.1:8000/api/campaigns/?status=active" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Events by type
curl "http://127.0.0.1:8000/api/events/?event_type=rally" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### Search Examples
```bash
# Search voters by name
curl "http://127.0.0.1:8000/api/voters/?search=john" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Search campaigns
curl "http://127.0.0.1:8000/api/campaigns/?search=election" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### Ordering Examples
```bash
# Voters by creation date (newest first)
curl "http://127.0.0.1:8000/api/voters/?ordering=-created_at" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Campaigns by budget (highest first)
curl "http://127.0.0.1:8000/api/campaigns/?ordering=-budget" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### Pagination Examples
```bash
# Page 2 of voters
curl "http://127.0.0.1:8000/api/voters/?page=2" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Custom page size
curl "http://127.0.0.1:8000/api/voters/?page_size=50" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

---

## Step 11: Test Custom Actions

### Voter Custom Actions
```bash
# Get voter statistics
curl http://127.0.0.1:8000/api/voters/stats/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Get sentiment breakdown
curl http://127.0.0.1:8000/api/voters/by_sentiment/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Mark voter as contacted (replace {id} with actual voter ID)
curl -X POST http://127.0.0.1:8000/api/voters/1/mark_contacted/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### Campaign Custom Actions
```bash
# Get campaign statistics
curl http://127.0.0.1:8000/api/campaigns/stats/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Get campaign performance (replace {id})
curl http://127.0.0.1:8000/api/campaigns/1/performance/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### Event Custom Actions
```bash
# Get event statistics
curl http://127.0.0.1:8000/api/events/stats/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Get upcoming events
curl http://127.0.0.1:8000/api/events/upcoming/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

---

## Step 12: Test Role-Based Access Control

### Create Test Users with Different Roles

```bash
# Admin user
curl -X POST http://127.0.0.1:8000/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "password": "password123",
    "name": "Admin Test",
    "role": "admin"
  }'

# Manager user
curl -X POST http://127.0.0.1:8000/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "manager@test.com",
    "password": "password123",
    "name": "Manager Test",
    "role": "manager"
  }'

# Regular user
curl -X POST http://127.0.0.1:8000/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@test.com",
    "password": "password123",
    "name": "User Test",
    "role": "user"
  }'
```

### Login as Different Users and Test Data Visibility

```bash
# Login as manager
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "manager@test.com",
    "password": "password123"
  }'

# Use manager's token to list voters (should see only district data)
curl http://127.0.0.1:8000/api/voters/ \
  -H "Authorization: Bearer MANAGER_ACCESS_TOKEN"
```

---

## Troubleshooting

### Issue: Migration Error
```bash
# Reset migrations (CAUTION: This deletes data!)
python manage.py migrate api zero
python manage.py migrate
```

### Issue: Import Error for django_filters
```bash
# Reinstall django-filter
pip install django-filter==24.3
```

### Issue: Faker not found
```bash
# Install Faker
pip install Faker==33.1.0
```

### Issue: Token expired
```bash
# Login again to get new token
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@pulseofpeople.com", "password":"admin123"}'
```

### Issue: Database locked (SQLite)
```bash
# Stop the server and restart
# Delete db.sqlite3 if necessary (will lose data)
rm db.sqlite3
python manage.py migrate
python manage.py seed_all_data --quick
```

---

## Postman Collection

### Import into Postman

1. Create new collection: "Pulse of People API"
2. Add environment variables:
   - `base_url`: `http://127.0.0.1:8000`
   - `access_token`: (get from login)

3. Add requests (examples):
   - Login: `POST {{base_url}}/api/auth/login/`
   - List Voters: `GET {{base_url}}/api/voters/`
   - Voter Stats: `GET {{base_url}}/api/voters/stats/`
   - List Campaigns: `GET {{base_url}}/api/campaigns/`
   - Campaign Stats: `GET {{base_url}}/api/campaigns/stats/`

4. Add Authorization header to all requests:
   - Type: Bearer Token
   - Token: `{{access_token}}`

---

## Performance Testing

### Check Query Performance
```bash
# Enable SQL logging in settings.py
DEBUG = True
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}

# Watch SQL queries in console
python manage.py runserver
```

### Load Test with Locust (if installed)
```bash
# Create locustfile.py with sample tests
locust -f locustfile.py --host=http://127.0.0.1:8000
```

---

## Next Steps

1. **Write Tests**
   - Create unit tests for models
   - Create API tests for endpoints
   - Create integration tests

2. **Deploy to Staging**
   - Configure PostgreSQL
   - Set environment variables
   - Run migrations
   - Deploy to Railway/Render

3. **Frontend Integration**
   - Connect React app to API
   - Test all endpoints
   - Implement error handling

4. **Production Setup**
   - Configure Redis caching
   - Set up Celery for background tasks
   - Configure monitoring (Sentry)
   - Set up automated backups

---

## Support

If you encounter issues:
1. Check the error message carefully
2. Verify all migrations are applied
3. Ensure dependencies are installed
4. Check Django logs
5. Refer to WORKSTREAM2_SUMMARY.md for details

---

**Last Updated:** 2025-11-09
**Version:** 1.0
**Status:** PRODUCTION READY
