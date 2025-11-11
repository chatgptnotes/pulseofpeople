# 🚀 SETUP INSTRUCTIONS - TVK Political Platform Backend

## ⚠️ YOUR ISSUE
Your virtual environment (venv) was created on a different computer, so it's broken.

## ✅ SOLUTION - Run These Commands

Open your terminal and copy-paste these commands ONE BY ONE:

### Step 1: Navigate to Backend Folder
```bash
cd "/Users/murali/Downloads/pulseofproject python/backend"
```

### Step 2: Remove Old Broken Virtual Environment
```bash
rm -rf venv
```

### Step 3: Create New Virtual Environment
```bash
python3 -m venv venv
```

If you get "command not found: python3", try:
```bash
python -m venv venv
```

### Step 4: Activate Virtual Environment
```bash
source venv/bin/activate
```

You should see `(venv)` appear in your terminal.

### Step 5: Install All Dependencies
```bash
pip install -r requirements.txt
```

This will take 2-3 minutes. Wait for it to finish.

### Step 6: Create Database Tables (Migrations)
```bash
python manage.py makemigrations
```

### Step 7: Apply Migrations to Database
```bash
python manage.py migrate
```

### Step 8: Create Admin User (Optional but Recommended)
```bash
python manage.py createsuperuser
```

Follow the prompts:
- Username: admin
- Email: admin@tvk.com
- Password: admin123 (or whatever you want)

### Step 9: Start the Server
```bash
python manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
```

### Step 10: Test It
Open your browser and go to:
- http://127.0.0.1:8000/api/health/
- You should see: `{"status": "ok"}`

---

## 🆘 IF YOU GET ERRORS

### Error: "python3: command not found"
**Solution**: Install Python from https://www.python.org/downloads/

### Error: "pip: command not found"
**Solution**: After activating venv, try:
```bash
python -m pip install -r requirements.txt
```

### Error: "ModuleNotFoundError: No module named 'django'"
**Solution**: Reinstall dependencies:
```bash
pip install Django djangorestframework django-cors-headers djangorestframework-simplejwt
```

### Error: "Circular import" during makemigrations
**Solution**: There's a model import issue. Let me know and I'll fix it.

---

## 📋 WHAT TO DO NEXT

Once you successfully run `python manage.py runserver`, come back and tell me:
✅ "Server is running!"

Then I'll continue creating the APIs for you!

---

## 🎯 QUICK SUMMARY
1. Delete old venv
2. Create new venv
3. Install packages
4. Run migrations
5. Start server
6. Tell me it worked!

**Start with Step 1 and work your way down. Copy-paste the commands exactly!**
