# 🔄 MIGRATION GUIDE: SQLite → Supabase + Directory Rename

## ⚠️ IMPORTANT: Follow Steps in EXACT Order

**Date:** 2025-11-07
**Estimated Time:** 20-30 minutes
**Risk Level:** Low (with backups)

---

## 📋 PRE-MIGRATION CHECKLIST

Before starting, ensure:
- [ ] Django server is STOPPED (kill the process)
- [ ] React dev server is STOPPED (kill the process)
- [ ] All terminal windows closed
- [ ] VS Code or any IDE closed
- [ ] No files open from the project

---

## STEP 1: BACKUP CURRENT DATA (5 minutes)

### 1.1 Backup SQLite Database

```bash
cd "/Users/murali/Downloads/pulseofproject python/backend"

# Create backup
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)

# Verify backup exists
ls -lh db.sqlite3*
```

**Expected:** You should see 2 files (original + backup)

### 1.2 Export User Data (Safety)

```bash
./venv/bin/python manage.py dumpdata auth.User api.UserProfile --indent 2 > users_backup.json

# Verify
cat users_backup.json
```

**Expected:** JSON file with all 6 users

---

## STEP 2: RENAME PROJECT DIRECTORY (3 minutes)

### 2.1 Close Everything First

**CRITICAL:** Close all:
- Terminal windows
- VS Code
- Any app accessing the project folder

### 2.2 Rename Using Finder (Safest Method)

```
1. Open Finder
2. Navigate to /Users/murali/Downloads/
3. Find: "pulseofproject python"
4. Right-click → Rename
5. Change to: "pulseofpeople"
6. Press Enter
```

**OR via Terminal:**

```bash
cd /Users/murali/Downloads
mv "pulseofproject python" "pulseofpeople"
```

### 2.3 Verify New Path

```bash
cd /Users/murali/Downloads/pulseofpeople
pwd
# Should show: /Users/murali/Downloads/pulseofpeople

ls -la
# Should show: backend/ voter/ and other folders
```

---

## STEP 3: UPDATE TERMINAL PATHS (2 minutes)

### 3.1 Open NEW Terminal

```bash
# Navigate to new location
cd /Users/murali/Downloads/pulseofpeople/backend

# Verify Python venv works
./venv/bin/python --version

# Test Django
./venv/bin/python manage.py --version
```

**Expected:** No errors, shows Python 3.14 and Django 5.2

---

## STEP 4: SETUP SUPABASE CONNECTION (10 minutes)

### 4.1 Get Supabase Credentials

**Go to:** https://supabase.com/dashboard

1. Select your project (or create new one: "pulseofpeople")
2. Click "Project Settings" → "Database"
3. Copy these values:

```
Host: [something].supabase.co
Database name: postgres
User: postgres
Password: [your password]
Port: 5432
```

### 4.2 Create .env File

```bash
cd /Users/murali/Downloads/pulseofpeople/backend

# Create .env file
cat > .env << 'EOF'
# Database Configuration
USE_SQLITE=False
DB_HOST=db.xxxxxxxxx.supabase.co
DB_NAME=postgres
DB_USER=postgres.xxxxxxxxx
DB_PASSWORD=your-supabase-password-here
DB_PORT=5432
DB_SSLMODE=require

# Django Secret Key
SECRET_KEY=your-django-secret-key-here

# Django Debug Mode
DEBUG=True
EOF
```

**IMPORTANT:** Replace the placeholders with your actual Supabase credentials!

### 4.3 Verify .env File

```bash
cat .env
```

**Expected:** Should show your Supabase credentials (NOT placeholder text)

---

## STEP 5: INSTALL POSTGRESQL ADAPTER (2 minutes)

```bash
cd /Users/murali/Downloads/pulseofpeople/backend

# Install psycopg2 (PostgreSQL adapter for Django)
./venv/bin/pip install psycopg2-binary

# Verify installation
./venv/bin/pip list | grep psycopg2
```

**Expected:** Shows psycopg2-binary version

---

## STEP 6: TEST SUPABASE CONNECTION (3 minutes)

```bash
cd /Users/murali/Downloads/pulseofpeople/backend

# Test database connection
./venv/bin/python manage.py dbshell --version

# Check Django can connect
./venv/bin/python manage.py check --database default
```

**Expected:** No errors

---

## STEP 7: RUN MIGRATIONS TO SUPABASE (5 minutes)

### 7.1 Create Fresh Schema

```bash
cd /Users/murali/Downloads/pulseofpeople/backend

# Show migrations to be applied
./venv/bin/python manage.py showmigrations

# Apply all migrations to Supabase
./venv/bin/python manage.py migrate

# Verify
./venv/bin/python manage.py showmigrations
```

**Expected:** All migrations show [X] (applied)

### 7.2 Verify Tables Created

```bash
./venv/bin/python manage.py shell -c "
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute(\"SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename;\")
    tables = cursor.fetchall()
    print('Tables in Supabase:')
    for table in tables:
        print(f'  - {table[0]}')
"
```

**Expected:** Shows list of Django tables (auth_user, api_userprofile, etc.)

---

## STEP 8: MIGRATE USER DATA (3 minutes)

### 8.1 Load Data from Backup

```bash
cd /Users/murali/Downloads/pulseofpeople/backend

# Load users from backup
./venv/bin/python manage.py loaddata users_backup.json
```

**Expected:** "Installed X object(s) from 1 fixture(s)"

### 8.2 Verify Users in Supabase

```bash
./venv/bin/python manage.py shell -c "
from django.contrib.auth.models import User
from api.models import UserProfile

print('=== USERS IN SUPABASE ===')
for u in User.objects.all().select_related('profile'):
    profile = getattr(u, 'profile', None)
    role = profile.role if profile else 'NO PROFILE'
    print(f'{u.id}. {u.username} | {u.email} | {role}')
"
```

**Expected:** Shows all 6 users

---

## STEP 9: START SERVERS & TEST (5 minutes)

### 9.1 Start Django Server

```bash
cd /Users/murali/Downloads/pulseofpeople/backend
./venv/bin/python manage.py runserver
```

**Expected:**
```
Starting development server at http://127.0.0.1:8000/
```

### 9.2 Test Login API

**Open NEW Terminal:**

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "dev@tvk.com", "password": "Dev@1234"}'
```

**Expected:** JSON with tokens (access, refresh)

### 9.3 Start React Server

**Open NEW Terminal:**

```bash
cd /Users/murali/Downloads/pulseofpeople/voter
npm run dev
```

**Expected:** Server starts on http://localhost:5173

### 9.4 Test Login in Browser

1. Go to: http://localhost:5173/login
2. Login: dev@tvk.com / Dev@1234
3. Should redirect to dashboard
4. Refresh page (F5)
5. Should stay logged in (not redirect to login)

---

## STEP 10: VERIFY SUPABASE DASHBOARD (2 minutes)

### 10.1 Check Supabase UI

1. Go to: https://supabase.com/dashboard
2. Select your project
3. Click "Table Editor"
4. Click "auth_user" table
5. Should see 6 users

### 10.2 Verify Database Type

```bash
cd /Users/murali/Downloads/pulseofpeople/backend

./venv/bin/python manage.py shell -c "
from django.conf import settings
print('Database Engine:', settings.DATABASES['default']['ENGINE'])
print('Database Host:', settings.DATABASES['default']['HOST'])
print('Using Supabase:', 'postgresql' in settings.DATABASES['default']['ENGINE'])
"
```

**Expected:**
```
Database Engine: django.db.backends.postgresql
Database Host: db.xxxxxxxxx.supabase.co
Using Supabase: True
```

---

## ✅ POST-MIGRATION CHECKLIST

Verify everything works:

- [ ] Django server starts without errors
- [ ] React server starts without errors
- [ ] Login works (email and username)
- [ ] Dashboard loads
- [ ] Page refresh keeps you logged in
- [ ] User creation works
- [ ] User list loads
- [ ] Data persists in Supabase
- [ ] No SQLite references in code

---

## 🔄 ROLLBACK PROCEDURE (If Something Goes Wrong)

### Quick Rollback to SQLite

```bash
cd /Users/murali/Downloads/pulseofpeople/backend

# Edit .env or delete it
rm .env

# Or set USE_SQLITE=True in .env
echo "USE_SQLITE=True" > .env

# Restore backup database
cp db.sqlite3.backup.* db.sqlite3

# Restart Django server
./venv/bin/python manage.py runserver
```

---

## 📊 VERIFICATION MATRIX

| Check | SQLite (Old) | Supabase (New) | Status |
|-------|--------------|----------------|--------|
| Database Type | sqlite3 | postgresql | [ ] |
| Location | Local file | Cloud (Supabase) | [ ] |
| Users Count | 6 | 6 | [ ] |
| Login Works | Yes | Yes | [ ] |
| Refresh Works | Yes | Yes | [ ] |
| User Creation | Yes | Yes | [ ] |
| Data Persists | Yes | Yes | [ ] |

---

## 🆘 TROUBLESHOOTING

### Issue 1: "psycopg2 not installed"
```bash
cd /Users/murali/Downloads/pulseofpeople/backend
./venv/bin/pip install psycopg2-binary
```

### Issue 2: "Connection refused"
- Check Supabase credentials in .env
- Verify HOST and PASSWORD are correct
- Check if IP allowed in Supabase dashboard

### Issue 3: "relation does not exist"
```bash
# Run migrations
./venv/bin/python manage.py migrate
```

### Issue 4: "No users after migration"
```bash
# Load backup
./venv/bin/python manage.py loaddata users_backup.json
```

---

## 📞 SUPPORT CHECKLIST

If you encounter issues, provide:
1. Error message (full text)
2. Which step you're on
3. Output of: `cat .env` (hide password)
4. Output of: `./venv/bin/python manage.py check`

---

## 🎯 SUCCESS CRITERIA

Migration is successful when:
✅ Project renamed to "pulseofpeople"
✅ Django connects to Supabase (not SQLite)
✅ All 6 users exist in Supabase
✅ Login works with Supabase
✅ Page refresh keeps session
✅ User creation saves to Supabase
✅ No SQLite database in use

**Ready to proceed?** Start with Step 1!

