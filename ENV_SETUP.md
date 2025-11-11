# Environment Variables Setup Guide

## Overview
This document explains all environment variables used in the Pulse of People platform for Supabase-Django integration.

## Architecture
- **Backend**: Django REST Framework with Supabase PostgreSQL
- **Frontend**: React + TypeScript + Vite
- **Authentication**: Supabase Auth with JWT tokens
- **Database**: Supabase PostgreSQL with Row Level Security (RLS)

---

## Backend Environment Variables (`backend/.env`)

### Django Settings
```env
# Django secret key for cryptographic signing
SECRET_KEY=django-insecure-development-key-change-in-production

# Debug mode (True for development, False for production)
DEBUG=True

# Comma-separated list of allowed hostnames
ALLOWED_HOSTS=localhost,127.0.0.1,pulseofpeople-production.up.railway.app
```

### Supabase PostgreSQL Database
```env
# Database name (always 'postgres' for Supabase)
DB_NAME=postgres

# Database user (format: postgres.{project_ref})
DB_USER=postgres.iwtgbseaoztjbnvworyq

# Database password
DB_PASSWORD=your-password-here

# Database host (Session Pooler for IPv4 compatibility)
DB_HOST=aws-1-ap-south-1.pooler.supabase.com

# Database port (6543 for Session Pooler, 5432 for Direct Connection)
DB_PORT=6543

# SSL mode for PostgreSQL connection
DB_SSLMODE=prefer

# Set to False to use PostgreSQL, True to use SQLite (development only)
USE_SQLITE=False
```

**Important Notes:**
- Use **Session Pooler** (port 6543) for serverless deployments (Railway, Vercel)
- Use **Direct Connection** (port 5432) for long-running servers with persistent connections
- Session Pooler is more reliable for Railway deployments

### CORS Settings
```env
# Comma-separated list of allowed origins for CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174
```

### Supabase Authentication

#### 1. SUPABASE_URL
```env
SUPABASE_URL=https://iwtgbseaoztjbnvworyq.supabase.co
```
- **Purpose**: Base URL for Supabase REST API and Auth endpoints
- **Where to find**: Supabase Dashboard > Settings > API > Project URL
- **Used by**: Backend (for API calls) and Frontend (for auth)
- **Security**: Public, safe to expose

#### 2. SUPABASE_ANON_KEY
```env
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
- **Purpose**: Public API key for client-side authentication
- **Where to find**: Supabase Dashboard > Settings > API > Project API keys > `anon` `public`
- **Used by**: Frontend (for auth requests) and Backend (for API calls)
- **Security**: Public, safe to expose in frontend
- **Note**: This key respects Row Level Security (RLS) policies

#### 3. SUPABASE_JWT_SECRET (CRITICAL)
```env
SUPABASE_JWT_SECRET=X6j+39tynhesQLZuzPc9IXP8H9UONWcKmkKdonFBnrvIqXMO+T+PACOWxpks6fVaKoPblX0FPyI3vc3X5J1x7g==
```
- **Purpose**: Secret key used to validate JWT tokens issued by Supabase
- **Where to find**: Supabase Dashboard > Settings > API > JWT Settings > JWT Secret
- **Used by**: Backend ONLY (for token validation)
- **Security**: **PRIVATE - NEVER expose in frontend or version control**
- **Critical**: This is different from SUPABASE_ANON_KEY and is required for JWT validation

#### 4. SUPABASE_SERVICE_KEY (Optional)
```env
# SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... (service_role key)
```
- **Purpose**: Admin key that bypasses Row Level Security (RLS)
- **Where to find**: Supabase Dashboard > Settings > API > Project API keys > `service_role` `secret`
- **Used by**: Backend only (for admin operations like user provisioning)
- **Security**: **HIGHLY SENSITIVE - Only use for trusted server-side operations**
- **When to use**: User creation, bulk operations, admin tasks that need to bypass RLS

---

## Frontend Environment Variables (`frontend/.env`)

### Supabase Configuration
```env
# Supabase Project URL (same as backend)
VITE_SUPABASE_URL=https://iwtgbseaoztjbnvworyq.supabase.co

# Supabase Anonymous Key (public key)
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Security Note:**
- ✅ VITE_SUPABASE_URL is safe to expose (public)
- ✅ VITE_SUPABASE_ANON_KEY is safe to expose (public, RLS protected)
- ❌ **NEVER** include SUPABASE_JWT_SECRET or SUPABASE_SERVICE_KEY in frontend

### Application Settings
```env
# Base URL for the frontend application
VITE_APP_URL=http://localhost:5173

# Application display name
VITE_APP_NAME=Pulse of People
```

### Multi-tenancy Settings
```env
# Enable/disable multi-tenant mode
VITE_MULTI_TENANT=false

# Tenant detection mode (subdomain, path, or header)
VITE_TENANT_MODE=subdomain

# Default tenant for single-tenant mode
VITE_DEFAULT_TENANT=tvk
```

### Django Backend API
```env
# Django REST API base URL
# Local: http://127.0.0.1:8000/api
# Production: https://your-railway-app.up.railway.app/api
VITE_DJANGO_API_URL=https://pulseofpeople-production.up.railway.app/api
```

### Mapbox Configuration
```env
# Mapbox access token for interactive maps
VITE_MAPBOX_ACCESS_TOKEN=pk.eyJ1IjoibXVyYWxpLXRlc3QiLCJhIjoiY20yenl6eXRhMDNwczJxcHd6OHE0NTY4ZiJ9.demo-token
```

### Optional Services
```env
# Email service provider
VITE_EMAIL_SERVICE=supabase

# DNS provider for subdomain management
VITE_DNS_PROVIDER=cloudflare

# Payment gateway integration
VITE_PAYMENT_GATEWAY=mock
```

---

## Key Differences: SUPABASE_JWT_SECRET vs SUPABASE_ANON_KEY

### SUPABASE_ANON_KEY (Public)
- **Type**: Public API key
- **Location**: Frontend + Backend
- **Purpose**: Make authenticated requests to Supabase
- **Security Level**: Public (RLS protected)
- **Token Payload**: `{"role": "anon", ...}`

### SUPABASE_JWT_SECRET (Private)
- **Type**: Secret signing key
- **Location**: Backend ONLY
- **Purpose**: Validate JWT tokens issued by Supabase
- **Security Level**: Highly sensitive, backend only
- **Usage**: JWT token verification in Django

**Analogy:**
- SUPABASE_ANON_KEY = Public house key (anyone can enter, but RLS controls what rooms they can access)
- SUPABASE_JWT_SECRET = Master key to verify all other keys are genuine

---

## Security Best Practices

### ✅ DO:
1. Keep SUPABASE_JWT_SECRET in backend `.env` only
2. Add `.env` files to `.gitignore`
3. Use environment variables in production (Railway, Vercel)
4. Rotate SUPABASE_JWT_SECRET periodically
5. Use HTTPS in production
6. Enable Row Level Security (RLS) on all Supabase tables

### ❌ DON'T:
1. Never commit `.env` files to git
2. Never expose SUPABASE_JWT_SECRET in frontend
3. Never use SUPABASE_SERVICE_KEY in frontend
4. Never hardcode secrets in source code
5. Never share production credentials in Slack/email
6. Never use production credentials in development

---

## Environment Variable Validation

### Backend Validation (settings.py)
```python
# Raises error if SUPABASE_JWT_SECRET is missing in production
if not SUPABASE_JWT_SECRET and not DEBUG:
    raise ValueError(
        "SUPABASE_JWT_SECRET is required for production. "
        "Find it in Supabase Dashboard > Settings > API > JWT Settings"
    )
```

### CORS Configuration
```python
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',  # Required for JWT token passing
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
```

**Note**: The `authorization` header is critical for passing JWT tokens from frontend to backend.

---

## Where to Find Supabase Credentials

### Step 1: Access Supabase Dashboard
1. Go to https://supabase.com/dashboard
2. Select your project: `pulseofpeople`

### Step 2: Navigate to API Settings
Dashboard > Settings > API

### Step 3: Copy Required Values

| Variable | Location | Copy From |
|----------|----------|-----------|
| SUPABASE_URL | Project URL | `https://iwtgbseaoztjbnvworyq.supabase.co` |
| SUPABASE_ANON_KEY | Project API keys > `anon` `public` | Long JWT starting with `eyJhbGci...` |
| SUPABASE_JWT_SECRET | JWT Settings > JWT Secret | Base64 string (e.g., `X6j+39tyn...`) |
| SUPABASE_SERVICE_KEY | Project API keys > `service_role` `secret` | Long JWT (use with caution) |

### Step 4: Database Connection
Dashboard > Settings > Database > Connection String

Choose:
- **Session Pooler** (recommended for Railway): Port 6543
- **Direct Connection** (for persistent servers): Port 5432

---

## Testing Your Configuration

### Backend Test
```bash
cd backend
source venv/bin/activate
python manage.py shell

# Test Supabase connection
from django.conf import settings
print(f"Supabase URL: {settings.SUPABASE_URL}")
print(f"JWT Secret Set: {bool(settings.SUPABASE_JWT_SECRET)}")
```

### Frontend Test
```bash
cd frontend
npm run dev

# Check browser console for:
# - VITE_SUPABASE_URL is defined
# - VITE_SUPABASE_ANON_KEY is defined
# - NO errors about missing environment variables
```

---

## Production Deployment

### Railway (Backend)
1. Go to Railway Dashboard > Your Service > Variables
2. Add all backend environment variables
3. **Never** commit production values to git

### Vercel (Frontend)
1. Go to Vercel Dashboard > Project > Settings > Environment Variables
2. Add all `VITE_*` variables
3. Redeploy to apply changes

---

## Troubleshooting

### Error: "JWT token validation failed"
- **Cause**: SUPABASE_JWT_SECRET is missing or incorrect
- **Fix**: Verify SUPABASE_JWT_SECRET in backend `.env` matches Supabase Dashboard

### Error: "CORS header 'Authorization' missing"
- **Cause**: Authorization header not allowed in CORS
- **Fix**: Verify `authorization` is in CORS_ALLOW_HEADERS (line 300 in settings.py)

### Error: "Database connection refused"
- **Cause**: Incorrect database credentials or port
- **Fix**: Verify DB_HOST uses Session Pooler (port 6543) for Railway

### Error: "Invalid API key"
- **Cause**: Wrong SUPABASE_ANON_KEY
- **Fix**: Copy from Supabase Dashboard > Settings > API > `anon` key

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-09 | Initial environment configuration |
| 1.1 | 2025-11-09 | Fixed JWT_SECRET security issue in frontend |
| 1.2 | 2025-11-09 | Added comprehensive documentation |

---

## Support

**Supabase Documentation**: https://supabase.com/docs
**Django REST Framework**: https://www.django-rest-framework.org/
**Railway Deployment**: https://docs.railway.app/

For project-specific issues, check `/Users/murali/Downloads/pulseofpeople/CLAUDE.md`
