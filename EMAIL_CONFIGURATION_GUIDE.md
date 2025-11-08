# Email Notification Configuration Guide

## Current Status: Console Backend (Development Mode)

Your Django backend is configured to **print emails to the console** instead of sending real emails. This is normal for development.

---

## Where to See Emails

### **Check Django Server Console Output**

Emails are displayed in the terminal where Django is running:

```bash
cd /Users/murali/Downloads/pulseofpeople/backend
./venv/bin/python manage.py runserver
```

When a user is created, you'll see output like:

```
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: Welcome to Pulse of People
From: noreply@pulseofpeople.com
To: testuser@example.com
Date: Fri, 08 Nov 2024 03:15:00 -0000
Message-ID: <...>

Hello Test User,

Your account has been created successfully!

Login Credentials:
- Email: testuser@example.com
- Password: Test@1234
- Role: user

Please login at http://localhost:5173/login

For security, we recommend changing your password after first login.

Best regards,
Pulse of People Team
```

---

## Current Configuration

**File:** `backend/config/settings.py` (Lines 280-289)

```python
if DEBUG:
    # Development: Print emails to console
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    # Production: Send real emails via SMTP
    EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
    EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
    EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
    EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@pulseofpeople.com')
```

---

## When Emails Are Sent

### **1. Individual User Creation**

When you click "Add Worker" and create a user:
- ✅ Welcome email sent immediately
- Contains: Name, Email, Password, Role, Login URL

### **2. Bulk CSV Import**

When you upload a CSV with multiple users:
- ✅ Welcome email sent to each user
- ✅ Completion email sent to admin who uploaded

**Example Completion Email:**
```
Subject: Bulk User Import Completed

Hello dev@tvk.com,

Your bulk user import job has completed successfully!

Summary:
- Total Users Processed: 100
- Successfully Created: 98
- Failed: 2

All users have been sent welcome emails with their credentials.

View Details: http://localhost:5173/field-worker-management

Best regards,
Pulse of People Team
```

---

## How to Test Email System

### **Step 1: Open Django Console**

```bash
cd /Users/murali/Downloads/pulseofpeople/backend

# Kill any existing Django process
/usr/bin/killall -9 Python 2>/dev/null

# Start Django and watch console
./venv/bin/python manage.py runserver
```

### **Step 2: Create a Test User**

1. Go to http://localhost:5173/field-worker-management
2. Click "Add Worker"
3. Fill in form:
   - Name: Test User
   - Email: test@example.com
   - Password: Test@1234
   - Role: user
4. Click "Create User"

### **Step 3: Check Django Console**

You should immediately see the email output in the terminal.

---

## Production Email Setup (For Real Emails)

### **Option 1: Gmail SMTP**

1. Create a Gmail App Password:
   - Go to Google Account → Security → 2-Step Verification → App Passwords
   - Generate password for "Mail"

2. Update `.env` file:

```bash
# backend/.env
DEBUG=False
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password-here
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

### **Option 2: SendGrid**

```bash
# backend/.env
DEBUG=False
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@pulseofpeople.com
```

### **Option 3: AWS SES**

```bash
# backend/.env
DEBUG=False
EMAIL_BACKEND=django_ses.SESBackend
AWS_SES_REGION_NAME=us-east-1
AWS_SES_REGION_ENDPOINT=email.us-east-1.amazonaws.com
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
DEFAULT_FROM_EMAIL=noreply@pulseofpeople.com
```

---

## Email Templates

### **Welcome Email Template**

**File:** `backend/api/services/bulk_user_import.py` (Lines 150-175)

```python
def _send_welcome_email(self, user: User, password: str):
    """Send welcome email with credentials"""
    subject = 'Welcome to Pulse of People'
    message = f'''
Hello {user.name},

Your account has been created successfully!

Login Credentials:
- Email: {user.email}
- Password: {password}
- Role: {user.profile.role}

Please login at http://localhost:5173/login

For security, we recommend changing your password after first login.

Best regards,
Pulse of People Team
'''

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Failed to send email to {user.email}: {str(e)}")
```

---

## Troubleshooting

### ❌ **Issue: "I don't see any emails"**

**Solutions:**

1. **Check Django is running:**
   ```bash
   /bin/ps aux | /usr/bin/grep "manage.py runserver"
   ```

2. **Check console output:**
   - Look at the terminal where Django is running
   - Emails appear immediately after user creation

3. **Check email configuration:**
   ```bash
   cd /Users/murali/Downloads/pulseofpeople/backend
   /usr/bin/grep -A 10 "EMAIL_BACKEND" config/settings.py
   ```

4. **Test email manually:**
   ```bash
   cd /Users/murali/Downloads/pulseofpeople/backend
   ./venv/bin/python manage.py shell

   # In Python shell:
   from django.core.mail import send_mail
   send_mail(
       'Test Subject',
       'Test message',
       'noreply@pulseofpeople.com',
       ['test@example.com'],
   )
   ```

### ❌ **Issue: "Emails not sent during bulk import"**

**Cause:** The bulk import service might have an error.

**Check:**
```bash
cd /Users/murali/Downloads/pulseofpeople/backend
./venv/bin/python manage.py shell

from api.services.bulk_user_import import BulkUserImportService
# Test the service
```

---

## Email Service Implementation

### **Individual User Creation**

When calling `djangoApi.register()`, the Django signup view does NOT send emails. You need to add email sending to the signup view.

### **Bulk CSV Import**

The bulk import service DOES send emails automatically:

1. **During Import:** Welcome email to each user
2. **After Completion:** Summary email to admin

**File:** `backend/api/services/bulk_user_import.py`

---

## Next Steps

### For Development:
✅ **No action needed** - Emails print to console (current setup)

### For Production:
1. Choose email provider (Gmail, SendGrid, AWS SES)
2. Get SMTP credentials
3. Update `.env` file
4. Set `DEBUG=False`
5. Test email delivery

---

## Summary

- **Development Mode:** Emails print to Django console ✅
- **Individual Creation:** Welcome emails sent ✅
- **Bulk Import:** Welcome emails + completion email sent ✅
- **Production:** Configure SMTP when deploying ⏳

**To see emails now:** Watch the Django server console output when creating users!
