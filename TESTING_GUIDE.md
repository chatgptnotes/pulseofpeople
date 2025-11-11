# 🧪 Testing Guide - Role-Based Dashboards

## ✅ What Was Completed

Successfully implemented **7 role-based dashboards** with automatic routing based on user roles.

---

## 🚀 Quick Start Testing

### **Step 1: Start Backend**

```bash
cd backend
python manage.py runserver
```

Should see:
```
Django version 5.2.7, using settings 'backend.settings'
Starting development server at http://127.0.0.1:8000/
```

### **Step 2: Start Frontend**

```bash
cd voter
npm run dev
```

Should see:
```
VITE v5.x.x ready in xxx ms
➜  Local:   http://localhost:5173/
```

### **Step 3: Test Auto-Routing**

Visit: `http://localhost:5173/dashboard`

You should be redirected based on your role:
- Superadmin → `/dashboard/superadmin`
- Admin → `/dashboard/admin`
- Manager → `/dashboard/manager`
- Analyst → `/dashboard/analyst`
- User → `/dashboard/user`
- Volunteer → `/dashboard/volunteer`
- Viewer → `/dashboard/viewer`

---

## 👥 Create Test Users

### **Option 1: Using Django Shell**

```bash
cd backend
python manage.py shell
```

Then run:

```python
from django.contrib.auth.models import User
from api.models import UserProfile, State, District

# 1. Superadmin
user = User.objects.create_user(
    username='superadmin',
    email='superadmin@tvk.com',
    password='test123',
    first_name='Super',
    last_name='Admin'
)
UserProfile.objects.create(user=user, role='superadmin')
print("✅ Created: superadmin@tvk.com / test123")

# 2. Admin (State - Vijay)
user = User.objects.create_user(
    username='vijay',
    email='vijay@tvk.com',
    password='test123',
    first_name='Vijay',
    last_name='TVK'
)
state = State.objects.get(code='TN')
UserProfile.objects.create(user=user, role='admin', assigned_state=state)
print("✅ Created: vijay@tvk.com / test123")

# 3. Manager (District - Chennai)
user = User.objects.create_user(
    username='manager_chennai',
    email='manager@tvk.com',
    password='test123',
    first_name='District',
    last_name='Manager'
)
district = District.objects.filter(state__code='TN', name__icontains='Chennai').first()
if district:
    UserProfile.objects.create(user=user, role='manager', assigned_district=district)
    print("✅ Created: manager@tvk.com / test123")
else:
    print("❌ Chennai district not found")

# 4. Analyst (Constituency)
user = User.objects.create_user(
    username='analyst',
    email='analyst@tvk.com',
    password='test123',
    first_name='Constituency',
    last_name='Analyst'
)
UserProfile.objects.create(user=user, role='analyst')
print("✅ Created: analyst@tvk.com / test123")
print("⚠️  TODO: Add constituency assignment once field is added")

# 5. User (Booth Agent)
user = User.objects.create_user(
    username='boothagentt',
    email='boothagentt@tvk.com',
    password='test123',
    first_name='Booth',
    last_name='Agent'
)
UserProfile.objects.create(user=user, role='user')
print("✅ Created: boothagentt@tvk.com / test123")

# 6. Volunteer
user = User.objects.create_user(
    username='volunteer',
    email='volunteer@tvk.com',
    password='test123',
    first_name='Field',
    last_name='Volunteer'
)
UserProfile.objects.create(user=user, role='volunteer')
print("✅ Created: volunteer@tvk.com / test123")

# 7. Viewer
user = User.objects.create_user(
    username='viewer',
    email='viewer@tvk.com',
    password='test123',
    first_name='Read',
    last_name='Only'
)
UserProfile.objects.create(user=user, role='viewer')
print("✅ Created: viewer@tvk.com / test123")

print("\n✅ All test users created successfully!")
```

### **Option 2: Quick Creation Script**

Save this as `backend/create_test_users.py`:

```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import UserProfile, State, District

# Clear existing test users (optional)
test_emails = [
    'superadmin@tvk.com',
    'vijay@tvk.com',
    'manager@tvk.com',
    'analyst@tvk.com',
    'boothagentt@tvk.com',
    'volunteer@tvk.com',
    'viewer@tvk.com'
]

User.objects.filter(email__in=test_emails).delete()
print("🗑️  Cleared existing test users\n")

# Create test users
users_data = [
    {
        'username': 'superadmin',
        'email': 'superadmin@tvk.com',
        'password': 'test123',
        'first_name': 'Super',
        'last_name': 'Admin',
        'role': 'superadmin'
    },
    {
        'username': 'vijay',
        'email': 'vijay@tvk.com',
        'password': 'test123',
        'first_name': 'Vijay',
        'last_name': 'TVK',
        'role': 'admin',
        'state_code': 'TN'
    },
    {
        'username': 'manager_chennai',
        'email': 'manager@tvk.com',
        'password': 'test123',
        'first_name': 'District',
        'last_name': 'Manager',
        'role': 'manager',
        'district_name': 'Chennai'
    },
    {
        'username': 'analyst',
        'email': 'analyst@tvk.com',
        'password': 'test123',
        'first_name': 'Constituency',
        'last_name': 'Analyst',
        'role': 'analyst'
    },
    {
        'username': 'boothagentt',
        'email': 'boothagentt@tvk.com',
        'password': 'test123',
        'first_name': 'Booth',
        'last_name': 'Agent',
        'role': 'user'
    },
    {
        'username': 'volunteer',
        'email': 'volunteer@tvk.com',
        'password': 'test123',
        'first_name': 'Field',
        'last_name': 'Volunteer',
        'role': 'volunteer'
    },
    {
        'username': 'viewer',
        'email': 'viewer@tvk.com',
        'password': 'test123',
        'first_name': 'Read',
        'last_name': 'Only',
        'role': 'viewer'
    }
]

for user_data in users_data:
    user = User.objects.create_user(
        username=user_data['username'],
        email=user_data['email'],
        password=user_data['password'],
        first_name=user_data['first_name'],
        last_name=user_data['last_name']
    )

    profile_data = {'user': user, 'role': user_data['role']}

    # Add state assignment for admin
    if 'state_code' in user_data:
        state = State.objects.filter(code=user_data['state_code']).first()
        if state:
            profile_data['assigned_state'] = state

    # Add district assignment for manager
    if 'district_name' in user_data:
        district = District.objects.filter(name__icontains=user_data['district_name']).first()
        if district:
            profile_data['assigned_district'] = district

    UserProfile.objects.create(**profile_data)
    print(f"✅ Created: {user_data['email']} / test123 ({user_data['role']})")

print("\n✅ All test users created successfully!")
print("\n📋 Test Credentials:")
print("=" * 50)
for user_data in users_data:
    print(f"{user_data['role']:15} | {user_data['email']:25} | test123")
```

Run it:
```bash
cd backend
python create_test_users.py
```

---

## 🧪 Testing Each Dashboard

### **1. Test Superadmin Dashboard**

**Login:** `superadmin@tvk.com` / `test123`

**Expected:**
- See platform overview
- Total organizations count
- Platform admins count
- Total users count
- System health status
- Links to `/super-admin/*` routes work

**Test:**
- [ ] Dashboard loads without errors
- [ ] All stat cards display
- [ ] Quick actions are clickable
- [ ] Recent activity shows
- [ ] System status shows "Healthy"

---

### **2. Test Admin Dashboard (State - Vijay)**

**Login:** `vijay@tvk.com` / `test123`

**Expected:**
- See Tamil Nadu state dashboard
- Overall sentiment for TN
- Total feedback count
- 38 districts shown
- 234 constituencies count
- Top performing districts
- Top issues across state

**Test:**
- [ ] Dashboard loads without errors
- [ ] State sentiment shows (percentage)
- [ ] Districts list loads from Django API
- [ ] Issues list loads from Django API
- [ ] "Drill-Down Map" link works
- [ ] "Competitor Analysis" link works
- [ ] Geographic breadcrumb shows "Tamil Nadu"

**API Calls to Verify:**
```javascript
// Open browser console
// You should see:
// ✅ GET http://127.0.0.1:8000/api/analytics/state/TN/
// ✅ GET http://127.0.0.1:8000/api/states/districts/?state_code=TN
// ✅ GET http://127.0.0.1:8000/api/issues/
```

---

### **3. Test Manager Dashboard (District)**

**Login:** `manager@tvk.com` / `test123`

**Expected:**
- See Chennai district dashboard
- District sentiment
- Constituencies within Chennai
- Analyst count
- Booth agents in district
- Constituency performance table
- Recent feedback from district

**Test:**
- [ ] Dashboard loads without errors
- [ ] Breadcrumb shows: Tamil Nadu → Chennai District
- [ ] District sentiment displays
- [ ] Constituencies load from Django API
- [ ] Recent feedback loads from Django API
- [ ] "District Map" link works
- [ ] "Social Monitoring" link works
- [ ] Constituency table shows data

**API Calls to Verify:**
```javascript
// ✅ GET http://127.0.0.1:8000/api/analytics/district/{district_id}/
// ✅ GET http://127.0.0.1:8000/api/constituencies/?state_code=TN&type=assembly
// ✅ GET http://127.0.0.1:8000/api/feedback/?district_id={district_id}
```

---

### **4. Test Analyst Dashboard (Constituency)**

**Login:** `analyst@tvk.com` / `test123`

**Expected:**
- See Perambur constituency dashboard
- Constituency sentiment
- 250 booths (total)
- 187 active booths
- Booth performance table
- Top issues in constituency

**Test:**
- [ ] Dashboard loads without errors
- [ ] Breadcrumb shows: Tamil Nadu → Chennai → Perambur Constituency
- [ ] Constituency sentiment displays
- [ ] Booth performance table shows
- [ ] Top issues load
- [ ] "Constituency Map" link works
- [ ] "Manage Booth Agents" link works

**API Calls to Verify:**
```javascript
// ✅ GET http://127.0.0.1:8000/api/analytics/constituency/{constituency_code}/
// ✅ GET http://127.0.0.1:8000/api/issues/
```

---

### **5. Test User Dashboard (Booth Agent) ⭐ CRITICAL**

**Login:** `boothagentt@tvk.com` / `test123`

**Expected:**
- See booth B-456 dashboard
- Performance score (85%)
- Today's feedback count
- Week's feedback count
- 4 large action buttons:
  1. Collect Feedback
  2. Daily Report
  3. My Voters
  4. Upload Photo
- Today's tasks checklist
- Recent feedback collected

**Test:**
- [ ] Dashboard loads without errors
- [ ] Breadcrumb shows: Chennai → Perambur → Booth B-456
- [ ] Performance score displays
- [ ] All 4 action buttons are large and clickable
- [ ] Buttons link to correct pages:
  - Collect Feedback → `/submit-data`
  - Daily Report → `/data-tracking`
  - My Voters → `/voter-database`
  - Upload Photo → `/submit-data`
- [ ] Today's tasks show completion status
- [ ] Recent feedback shows with sentiment icons

**This is the MOST IMPORTANT dashboard - booth agents are primary data collectors!**

---

### **6. Test Volunteer Dashboard**

**Login:** `volunteer@tvk.com` / `test123`

**Expected:**
- Ultra-simple interface
- Today's progress (feedback, photos, hours)
- 3 LARGE action buttons:
  1. Collect Feedback (Blue)
  2. Upload Photo (Purple)
  3. Mark Location (Green)
- Recent submissions list
- Contact support button

**Test:**
- [ ] Dashboard loads without errors
- [ ] Interface is simple and clean
- [ ] Buttons are large and touch-friendly
- [ ] All buttons link to `/submit-data`
- [ ] Recent submissions show with checkmarks
- [ ] Contact support button present

---

### **7. Test Viewer Dashboard**

**Login:** `viewer@tvk.com` / `test123`

**Expected:**
- Read-only mode indicator at top
- Blue notice: "Limited Access"
- Overall stats (view only)
- 4 available views:
  1. View Analytics
  2. View Reports
  3. View Map
  4. View Data
- Clear restrictions notice

**Test:**
- [ ] Dashboard loads without errors
- [ ] "READ-ONLY MODE" badge shows
- [ ] Blue notice explains limitations
- [ ] Stats display but no edit buttons
- [ ] All 4 view links work
- [ ] "What You Cannot Do" section shows restrictions

---

## 🔍 What to Look For

### **All Dashboards:**
- [ ] No console errors
- [ ] Fast loading (< 2 seconds)
- [ ] Responsive design (test mobile view)
- [ ] Proper role filtering
- [ ] Correct user name displays
- [ ] Footer shows last updated time

### **API Integration:**
- [ ] Check browser Network tab
- [ ] Django API calls succeed (200 status)
- [ ] Data loads from backend (not mock)
- [ ] Error handling works (if API fails)

### **Security:**
- [ ] Users cannot access other role dashboards
- [ ] Try accessing `/dashboard/admin` as user → Should redirect to `/unauthorized`
- [ ] Protected routes work
- [ ] Logout works

---

## 🐛 Common Issues & Fixes

### **Issue 1: "Cannot read property 'role' of null"**
**Cause:** User not logged in
**Fix:** Login first, then visit dashboard

### **Issue 2: Blank dashboard**
**Cause:** Django backend not running
**Fix:**
```bash
cd backend
python manage.py runserver
```

### **Issue 3: "API request failed"**
**Cause:** Django API URL incorrect
**Fix:** Check `voter/.env`:
```
VITE_DJANGO_API_URL=http://127.0.0.1:8000/api
```

### **Issue 4: Dashboard doesn't redirect**
**Cause:** User profile missing role
**Fix:** Check database:
```sql
SELECT u.email, up.role FROM auth_user u
JOIN api_userprofile up ON u.id = up.user_id;
```

### **Issue 5: "Unauthorized" page appears**
**Cause:** User lacks required permission/role
**Fix:** Check `ProtectedRoute` in `App.tsx` - may need to adjust role requirements

---

## 📊 Test Results Checklist

| Dashboard | Loads | Data | Links | API | Mobile | Status |
|-----------|-------|------|-------|-----|--------|--------|
| Superadmin | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Admin (State) | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Manager (District) | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Analyst (Constituency) | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| User (Booth) | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Volunteer | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |
| Viewer | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |

---

## ✅ Success Criteria

**All dashboards PASS if:**
1. Dashboard loads without errors
2. Correct data displays for role
3. All links work
4. API calls succeed (where integrated)
5. Mobile view looks good
6. No security issues

**Overall PASS if:**
- All 7 dashboards work
- Auto-routing works
- Role-based access control works
- No console errors

---

## 🚀 Next Steps After Testing

Once all tests pass:

1. **Backend Updates:**
   - Add `assigned_constituency` field to UserProfile
   - Create PollingBooth model
   - Add booth-level API endpoints

2. **Complete API Integration:**
   - Connect User dashboard to Django
   - Add performance score calculations
   - Integrate task management

3. **Production Deployment:**
   - Build frontend: `npm run build`
   - Deploy to production server
   - Update environment variables

4. **User Training:**
   - Train booth agents on User dashboard
   - Train volunteers on Volunteer dashboard
   - Train analysts on constituency management

---

## 📝 Report Issues

If you find bugs, document:
1. Which dashboard
2. What action caused the error
3. Error message (from console)
4. Steps to reproduce

Then report in project issues or to development team.

---

**Happy Testing! 🎉**

All 7 dashboards are ready for your testing!
