# User Management System - Quick Testing Instructions

## Prerequisites

1. **Backend running:**
   ```bash
   cd /Users/murali/Downloads/pulseofpeople/backend
   ./venv/bin/python manage.py runserver
   ```

2. **Frontend running:**
   ```bash
   cd /Users/murali/Downloads/pulseofpeople/voter
   npm run dev
   ```

3. **Login with admin user:**
   - Open http://localhost:5173
   - Login with admin/superadmin account

---

## Test 1: Individual User Creation (2 minutes)

1. Navigate to **User Management** page
2. Click **"Create User"** button
3. Fill form:
   - Name: `Test User`
   - Email: `test.user@example.com`
   - Password: `Test@1234`
   - Role: `user`
   - Phone: `+91 9876543210`
4. Click **"Create User"**
5. **Expected:** Success message, user appears in list

---

## Test 2: Bulk Upload - Valid Data (5 minutes)

1. Click **"Bulk Upload (CSV)"** button
2. Click **"Download CSV Template"** to see format
3. Upload file: `/Users/murali/Downloads/pulseofpeople/backend/test_users_valid.csv`
4. Click **"Start Upload"**
5. **Expected:**
   - Progress modal appears
   - Status: pending → validating → processing → completed
   - 10 total, 10 success, 0 failed
   - 10 welcome emails in console
   - 10 new users in list

---

## Test 3: Bulk Upload - With Errors (5 minutes)

1. Click **"Bulk Upload (CSV)"** button
2. Upload file: `/Users/murali/Downloads/pulseofpeople/backend/test_users_with_errors.csv`
3. Click **"Start Upload"**
4. **Expected:**
   - Status: completed
   - 10 total, 3-5 success, 5-7 failed
   - "Download Error Report" button
5. Click **"Download Error Report"**
6. **Expected:** CSV with detailed errors

---

## Test 4: Template Download (1 minute)

1. Click **"Bulk Upload (CSV)"**
2. Click **"Download CSV Template"**
3. **Expected:** CSV file downloads with example data
4. Open CSV - verify format

---

## Test 5: Progress Tracking (2 minutes)

1. Upload CSV with 10+ users
2. Watch progress modal
3. **Expected:**
   - Progress bar updates
   - Percentage increases
   - Processed count increases
   - Real-time updates every 2 seconds

---

## Test 6: Email Notifications (1 minute)

1. Complete any bulk upload
2. Check terminal/console where Django is running
3. **Expected:**
   - Welcome emails for each user
   - Completion email to admin
   - Emails contain username, password, login URL

---

## Test CSV Files Location

### Valid Data (10 users):
```
/Users/murali/Downloads/pulseofpeople/backend/test_users_valid.csv
```

### With Errors (mix of valid/invalid):
```
/Users/murali/Downloads/pulseofpeople/backend/test_users_with_errors.csv
```

---

## Expected Errors in Test File

The `test_users_with_errors.csv` contains these intentional errors:

1. **Row 2:** Missing name
2. **Row 3:** Invalid email format
3. **Row 4:** Invalid role
4. **Row 5:** Unauthorized role (superadmin)
5. **Row 6:** Non-existent state/district IDs

Only 3-5 rows should succeed.

---

## Viewing Emails (Development)

Since we're using console email backend, all emails print to the terminal where Django is running.

**To see emails:**
1. Look at the terminal/console running `manage.py runserver`
2. Scroll to find email content
3. Format will be:
   ```
   Content-Type: text/plain; charset="utf-8"
   MIME-Version: 1.0
   Content-Transfer-Encoding: 7bit
   Subject: Welcome to Pulse of People - Your Account Details
   From: noreply@pulseofpeople.com
   To: user@example.com

   Hello John,

   Your account has been created successfully!

   Login Details:
   - Email: john@example.com
   - Username: john
   - Temporary Password: Abc123!@#xyz

   ...
   ```

---

## Quick Verification Checklist

After testing, verify:

- [ ] Individual user creation works
- [ ] Bulk upload with valid data works
- [ ] Bulk upload with errors works (partial success)
- [ ] Error report downloads correctly
- [ ] Template downloads correctly
- [ ] Progress tracking updates in real-time
- [ ] Welcome emails printed to console
- [ ] Completion email printed to console
- [ ] New users appear in user list
- [ ] Can login with created users
- [ ] Users have `must_change_password=True` flag

---

## Troubleshooting

### Issue: "Permission denied"
**Solution:** Login with admin/superadmin role

### Issue: "Email already exists"
**Solution:** Change emails in CSV or delete test users from database

### Issue: "State ID does not exist"
**Solution:** Check if states are seeded in database
```bash
./venv/bin/python manage.py seed_political_data
```

### Issue: No progress updates
**Solution:** Check browser console for errors, verify backend is running

### Issue: Upload fails immediately
**Solution:** Check Django console for errors, verify file size <5MB

---

## Database Check Commands

### Count users:
```bash
./venv/bin/python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.count()
```

### View bulk upload jobs:
```bash
>>> from api.models import BulkUploadJob
>>> for job in BulkUploadJob.objects.all():
...     print(f"{job.job_id}: {job.status} - {job.success_count}/{job.total_rows}")
```

### View errors for a job:
```bash
>>> from api.models import BulkUploadError
>>> job = BulkUploadJob.objects.first()
>>> for error in job.errors.all():
...     print(f"Row {error.row_number}: {error.error_message}")
```

---

## Success Criteria

All tests pass if:

1. ✅ Individual user created successfully
2. ✅ Bulk upload processes 10 users (100% success)
3. ✅ Bulk upload with errors shows correct success/fail counts
4. ✅ Error CSV contains detailed error information
5. ✅ Progress updates in real-time
6. ✅ Emails printed to console
7. ✅ New users visible in UI
8. ✅ Can login with created credentials

---

**Testing Time:** ~15-20 minutes for complete test suite

**Status:** Ready for testing! 🚀
