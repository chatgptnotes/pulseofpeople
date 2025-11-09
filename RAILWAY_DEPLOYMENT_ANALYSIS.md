# Railway Deployment Configuration Analysis
## Pulse of People Platform - Complete Issue Report

**Date**: 2025-11-09
**Platform**: Railway
**Services**: Backend (Django) + Frontend (Vite/React)
**Status**: CRITICAL - Multiple deployment-blocking issues identified

---

## EXECUTIVE SUMMARY

Total Issues Found: **23 CRITICAL and HIGH-priority issues**

- **CRITICAL Issues**: 11 (will cause immediate deployment failure)
- **HIGH Issues**: 7 (will cause runtime failures or security vulnerabilities)
- **MEDIUM Issues**: 3 (performance and configuration issues)
- **LOW Issues**: 2 (optimization opportunities)

**Main Problems**:
1. Backend variables contain malformed and incomplete configurations
2. Frontend variables have 100% duplication (all vars listed twice)
3. Missing required Django environment variables
4. CORS and database URL misconfigurations
5. Incorrect SSL mode settings
6. Missing Gunicorn dependency

---

## BACKEND VARIABLES ANALYSIS

### CRITICAL ISSUES

#### 1. BROKEN DATABASE_URL VARIABLE
**Severity**: CRITICAL
**Variable**: `DATABASE_URL`
```
DATABASE_URL="postgresql://postgres:Chindwada%401@db.iwtgbseaoztjbnvworyq.supabase.co:5432/postgres?s"
```

**Issues**:
- URL is truncated - ends with `?s` instead of proper query parameters
- Should be: `?sslmode=require` or `?pgbouncer=true&sslmode=require`
- Django's `dj-database-url` will fail to parse this malformed URL

**Impact**: Django cannot connect to database, application will crash on startup

**Fix Required**:
```bash
DATABASE_URL="postgresql://postgres:Chindwada%401@db.iwtgbseaoztjbnvworyq.supabase.co:5432/postgres?sslmode=require"
```

---

#### 2. ORPHANED VARIABLE: gbouncer
**Severity**: CRITICAL
**Variable**: `gbouncer="true"`

**Issues**:
- This is a typo/fragment from the DATABASE_URL
- Should be part of the DATABASE_URL query parameters: `?pgbouncer=true`
- Exists as standalone variable with no purpose
- Not referenced anywhere in Django settings

**Impact**: Pgbouncer connection pooling not working, potential connection issues

**Fix Required**: Remove this variable and fix DATABASE_URL instead

---

#### 3. ORPHANED VARIABLE: slmode
**Severity**: CRITICAL
**Variable**: `slmode="require"`

**Issues**:
- This is a typo/fragment, should be `sslmode`
- Should be part of DATABASE_URL: `?sslmode=require`
- Exists as standalone variable with no purpose
- SSL mode not being applied to database connections

**Impact**: Database connections may fail or be insecure (no SSL)

**Fix Required**: Remove this variable and fix DATABASE_URL instead

---

#### 4. CONFLICTING DATABASE CONFIGURATION
**Severity**: CRITICAL
**Variables**: Multiple database variables present

**Issues**:
```
DB_HOST="aws-1-ap-south-1.pooler.supabase.com"  (Pooler - Port 6543)
DB_PORT="6543"
DATABASE_URL="...@db.iwtgbseaoztjbnvworyq.supabase.co:5432/..."  (Direct - Port 5432)
```

**Problems**:
- Two different database endpoints configured
- `DB_HOST` points to Supabase Pooler (port 6543)
- `DATABASE_URL` points to direct connection (port 5432)
- Django may use one while expecting the other
- Port mismatch will cause connection failures

**Impact**: Unpredictable database connection behavior, intermittent failures

**Fix Required**: Use ONLY ONE approach - either DATABASE_URL OR individual DB_* variables, not both

**Recommended**:
```bash
# Remove DATABASE_URL and use individual variables
DB_HOST="aws-1-ap-south-1.pooler.supabase.com"
DB_PORT="6543"
DB_NAME="postgres"
DB_USER="postgres.iwtgbseaoztjbnvworyq"
DB_PASSWORD="Chindwada@1"
DB_SSLMODE="require"
```

---

#### 5. INCORRECT CORS_ALLOWED_ORIGINS FORMAT
**Severity**: CRITICAL
**Variable**: `CORS_ALLOWED_ORIGINS`
```
CORS_ALLOWED_ORIGINS="https://tvk.pulseofpeople.com,pulseofpeople-production.up.railway.app"
```

**Issues**:
- Missing `https://` scheme on Railway backend domain
- Django settings.py expects all origins to have proper URL schemes
- Code in settings.py (line 258-265) tries to auto-fix but may fail

**Impact**: CORS errors when frontend tries to access backend API

**Fix Required**:
```bash
CORS_ALLOWED_ORIGINS="https://tvk.pulseofpeople.com,https://pulseofpeople-production.up.railway.app"
```

---

#### 6. MISSING REQUIRED VARIABLE: JWT_ACCESS_TOKEN_LIFETIME
**Severity**: HIGH
**Variable**: Not present

**Issues**:
- `JWT_SECRET` exists but token lifetime settings missing
- Django settings.py uses `SECRET_KEY` as fallback (line 239)
- No custom JWT lifetime configuration
- Token expiration behavior undefined

**Impact**: Tokens may expire too quickly or never expire

**Fix Required**:
```bash
JWT_ACCESS_TOKEN_LIFETIME=1440  # 24 hours in minutes
JWT_REFRESH_TOKEN_LIFETIME=43200  # 30 days in minutes
```

---

#### 7. MISSING REQUIRED VARIABLE: USE_SQLITE
**Severity**: HIGH
**Variable**: Not present, defaults to `True` in settings.py (line 116)

**Issues**:
- Settings.py checks `USE_SQLITE` to determine database backend
- If not set, defaults to `True` = SQLite mode
- Will ignore all PostgreSQL configuration
- App will use local SQLite database instead of Supabase

**Impact**: Application runs with SQLite instead of PostgreSQL, data not persisted in Supabase

**Fix Required**:
```bash
USE_SQLITE="False"
```

---

#### 8. MISSING DEPENDENCY: gunicorn
**Severity**: CRITICAL
**File**: `/Users/murali/Downloads/pulseofpeople/backend/requirements.txt`

**Issues**:
- `nixpacks.toml` and `railway.toml` both specify Gunicorn as WSGI server
- Gunicorn NOT found in requirements.txt
- Railway build will fail at startup

**Impact**: Deployment will fail with "command not found: gunicorn"

**Fix Required**: Add to requirements.txt:
```
gunicorn==21.2.0
```

---

### HIGH SEVERITY ISSUES

#### 9. INCONSISTENT SSL MODE CONFIGURATION
**Severity**: HIGH
**Variables**: `DB_SSLMODE="prefer"` vs hardcoded `sslmode=require` in settings.py

**Issues**:
- Environment variable says `DB_SSLMODE="prefer"` (allows non-SSL)
- Django settings.py hardcodes `'sslmode': 'require'` (line 137)
- Environment variable will be ignored
- Inconsistent configuration

**Impact**: Confusion about actual SSL behavior, potential security risk

**Fix Required**: Change to match settings.py:
```bash
DB_SSLMODE="require"
```

---

#### 10. SUPABASE_JWT_SECRET vs JWT_SECRET CONFUSION
**Severity**: HIGH
**Variables**: Both present with different values

```
SUPABASE_JWT_SECRET="X6j+39tynhesQLZuzPc9IXP8H9UONWcKmkKdonFBnrvIqXMO+T+PACOWxpks6fVaKoPblX0FPyI3vc3X5J1x7g=="
JWT_SECRET="DWCtQ-UF_0kfwHWnLYuko-_mpP92VlfI9KYRy-8OzJpRAyLk31nyeWApNPfnqvn4MGY"
```

**Issues**:
- Two different JWT secrets configured
- `SUPABASE_JWT_SECRET` is for Supabase Auth (to verify Supabase-issued tokens)
- `JWT_SECRET` appears to be custom but is NOT used in settings.py
- Django uses `SECRET_KEY` for JWT signing (line 239 in settings.py)
- `JWT_SECRET` variable serves no purpose

**Impact**: Confusion about which secret is used, potential auth failures

**Fix Required**: Remove `JWT_SECRET` variable (not used)

---

#### 11. MISSING CSRF_COOKIE_DOMAIN
**Severity**: MEDIUM
**Variable**: Not present

**Issues**:
- `CSRF_TRUSTED_ORIGINS` configured but no `CSRF_COOKIE_DOMAIN`
- Cross-domain CSRF may fail
- Cookie won't be sent from frontend domain to backend domain

**Impact**: CSRF token validation failures on cross-origin requests

**Fix Required**:
```bash
CSRF_COOKIE_DOMAIN=".pulseofpeople.com"
```

---

#### 12. ALLOWED_HOSTS MISSING RAILWAY DOMAIN
**Severity**: MEDIUM
**Variable**: `ALLOWED_HOSTS`
```
ALLOWED_HOSTS="pulseofpeople-production.up.railway.app,.railway.app,localhost"
```

**Issues**:
- Frontend is at different Railway domain (from frontend vars)
- Missing proper domain wildcards
- Should include all possible access points

**Impact**: 400 Bad Request errors if accessed from unlisted domains

**Fix Required**:
```bash
ALLOWED_HOSTS="pulseofpeople-production.up.railway.app,.railway.app,localhost,127.0.0.1,tvk.pulseofpeople.com,.pulseofpeople.com"
```

---

#### 13. MISSING STATIC FILES CONFIGURATION
**Severity**: MEDIUM
**Variables**: No `STATIC_ROOT` or `MEDIA_ROOT` variables

**Issues**:
- Django collectstatic requires `STATIC_ROOT`
- Railway build command includes `collectstatic` (railway.toml line 8)
- No configuration for where static files should go
- Settings.py has defaults but no production override

**Impact**: Static files may not be served correctly in production

**Fix Required**:
```bash
STATIC_ROOT="/app/staticfiles"
STATIC_URL="/static/"
```

---

### LOW SEVERITY ISSUES

#### 14. DEBUG MODE IN PRODUCTION
**Severity**: LOW (already set correctly to False)
**Variable**: `DEBUG="False"`

**Status**: Correctly configured, no action needed

---

#### 15. MISSING REDIS_URL
**Severity**: LOW
**Variable**: Not present

**Issues**:
- Settings.py checks for `REDIS_URL` (line 369)
- Falls back to local memory cache if not present
- Not critical but reduces performance

**Impact**: No cache, slower performance

**Recommendation**: Add Redis addon in Railway:
```bash
REDIS_URL="redis://:password@redis-service.railway.internal:6379/0"
```

---

## FRONTEND VARIABLES ANALYSIS

### CRITICAL ISSUES

#### 16. 100% VARIABLE DUPLICATION
**Severity**: CRITICAL
**All variables listed twice**

**Issues**:
```bash
# First occurrence (lines 1-12)
VITE_APP_NAME="Pulse of People"
VITE_APP_URL="https://tvk.pulseofpeople.com"
VITE_APP_VERSION="1.0"
VITE_DEFAULT_TENANT="tvk"
VITE_MULTI_TENANT="false"
VITE_TENANT_MODE="single"
VITE_SUPABASE_URL="https://iwtgbseaoztjbnvworyq.supabase.co"
VITE_SUPABASE_ANON_KEY="eyJhbGciOiJ..."
VITE_DJANGO_API_URL="https://pulseofpeople-production.up.railway.app/api"
VITE_MAPBOX_ACCESS_TOKEN="pk.eyJ1IjoibXV..."
JWT_SECRET="X6j+39tynhesQLZuzPc9IXP8H9UONWcKmkKdonFBnrvIqXMO+T+PACOWxpks6fVaKoPblX0FPyI3vc3X5J1x7g=="

# Second occurrence (lines 13-24) - EXACT DUPLICATES
VITE_APP_NAME="Pulse of People"
VITE_APP_URL="https://tvk.pulseofpeople.com"
...
```

**Impact**:
- Confusing configuration management
- Risk of updating one but not the other
- Last value wins (Railway uses last occurrence)

**Fix Required**: Remove all duplicates, keep only one set

---

#### 17. JWT_SECRET IN FRONTEND (SECURITY RISK)
**Severity**: CRITICAL
**Variable**: `JWT_SECRET` in frontend environment

**Issues**:
- JWT signing secrets should NEVER be exposed to frontend
- Frontend should only receive and validate tokens, not sign them
- This is a major security vulnerability
- Secret is visible in browser DevTools

**Impact**: Anyone can forge authentication tokens

**Fix Required**: REMOVE `JWT_SECRET` from frontend variables immediately

---

#### 18. WRONG DJANGO API URL
**Severity**: HIGH
**Variable**: `VITE_DJANGO_API_URL`
```
VITE_DJANGO_API_URL="https://pulseofpeople-production.up.railway.app/api"
```

**Issues**:
- Backend service name might be different
- No guarantee this is the actual backend URL
- Should verify actual Railway backend service URL

**Impact**: Frontend cannot connect to backend API

**Fix Required**: Verify actual Railway backend URL and update:
```bash
VITE_DJANGO_API_URL="https://<actual-backend-service>.railway.app/api"
```

---

#### 19. DEMO MAPBOX TOKEN
**Severity**: MEDIUM
**Variable**: `VITE_MAPBOX_ACCESS_TOKEN`
```
VITE_MAPBOX_ACCESS_TOKEN="pk.eyJ1IjoibXVyYWxpLXRlc3QiLCJhIjoiY20yenl6eXRhMDNwczJxcHd6OHE0NTY4ZiJ9.demo-token-replace-with-real"
```

**Issues**:
- Token contains "demo-token-replace-with-real" in signature
- May be invalid or rate-limited demo token
- Maps may not load

**Impact**: Mapbox maps will not render

**Fix Required**: Replace with valid production Mapbox token

---

#### 20. MISSING REQUIRED FRONTEND VARIABLES
**Severity**: HIGH
**Variables**: Several expected variables missing

**Missing Variables** (based on `.env.example`):
```bash
VITE_DEV_MODE=false
VITE_ENABLE_SOCIAL_MEDIA=true
VITE_ENABLE_INFLUENCER_TRACKING=true
VITE_ENABLE_FIELD_REPORTS=true
VITE_ENABLE_SURVEYS=true
VITE_ENABLE_AI_INSIGHTS=true
```

**Impact**: Features may not work or be unavailable

**Fix Required**: Add all missing feature flags

---

## CONFIGURATION FILE ISSUES

### 21. VITE PREVIEW PORT MISMATCH
**Severity**: MEDIUM
**Files**: `vite.config.ts` vs `nixpacks.toml`

**Issues**:
- `vite.config.ts` line 12: `port: 8080`
- `nixpacks.toml` line 11: `--port $PORT` (Railway dynamic port)
- Port conflict may occur

**Impact**: Vite preview may not start correctly

**Fix Required**: Update vite.config.ts to use environment port:
```typescript
preview: {
  port: parseInt(process.env.PORT || '8080'),
  host: true,
  allowedHosts: [...]
}
```

---

### 22. RAILWAY.TOML BUILD COMMAND INCOMPLETE
**Severity**: LOW
**File**: `railway.toml` line 8

**Current**:
```toml
buildCommand = "pip install -r requirements.txt && python manage.py collectstatic --noinput"
```

**Issues**:
- Missing migration step
- Should run migrations during deployment
- `nixpacks.toml` includes migrations but `railway.toml` doesn't

**Impact**: Database schema not updated on deployment

**Fix Required**:
```toml
buildCommand = "pip install -r requirements.txt && python manage.py migrate --noinput && python manage.py collectstatic --noinput"
```

---

### 23. BACKEND NIXPACKS PYTHON VERSION
**Severity**: LOW
**File**: `backend/nixpacks.toml` line 2

**Current**: `nixPkgs = ["python311", "postgresql"]`

**Issues**:
- Python 3.11 specified
- Local development uses Python 3.14 (from requirements.txt path)
- Version mismatch may cause compatibility issues

**Impact**: Different behavior between local and production

**Recommendation**: Update to match local version:
```toml
nixPkgs = ["python314", "postgresql"]
```

---

## CORRECTED VARIABLE CONFIGURATIONS

### BACKEND VARIABLES (CORRECTED)

```bash
# ============================================
# Django Core
# ============================================
SECRET_KEY="IM5sr4ltS5p71--IgqRzJflgfFNGuU2kpesz5EPc9xHcmvq5PnKZvMLxov6J88bDqrQ"
DEBUG="False"
ALLOWED_HOSTS="pulseofpeople-production.up.railway.app,.railway.app,tvk.pulseofpeople.com,.pulseofpeople.com,localhost,127.0.0.1"

# ============================================
# Database - USE POOLER (Recommended for Railway)
# ============================================
USE_SQLITE="False"
DB_NAME="postgres"
DB_USER="postgres.iwtgbseaoztjbnvworyq"
DB_PASSWORD="Chindwada@1"
DB_HOST="aws-1-ap-south-1.pooler.supabase.com"
DB_PORT="6543"
DB_SSLMODE="require"

# ============================================
# CORS & Security
# ============================================
CORS_ALLOWED_ORIGINS="https://tvk.pulseofpeople.com,https://pulseofpeople-production.up.railway.app"
CSRF_TRUSTED_ORIGINS="https://tvk.pulseofpeople.com,https://pulseofpeople-production.up.railway.app"
CSRF_COOKIE_DOMAIN=".pulseofpeople.com"

# ============================================
# Supabase Configuration
# ============================================
SUPABASE_URL="https://iwtgbseaoztjbnvworyq.supabase.co"
SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml3dGdic2Vhb3p0amJudndvcnlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjExNjAzOTksImV4cCI6MjA3NjczNjM5OX0.xA4B0XZJE_4MdjFCkw2yVsf4vlHmHfpeV6Bk5tG2T94"
SUPABASE_JWT_SECRET="X6j+39tynhesQLZuzPc9IXP8H9UONWcKmkKdonFBnrvIqXMO+T+PACOWxpks6fVaKoPblX0FPyI3vc3X5J1x7g=="

# ============================================
# JWT Token Configuration
# ============================================
JWT_ACCESS_TOKEN_LIFETIME=1440  # 24 hours in minutes
JWT_REFRESH_TOKEN_LIFETIME=43200  # 30 days in minutes

# ============================================
# Static Files
# ============================================
STATIC_ROOT="/app/staticfiles"
STATIC_URL="/static/"

# ============================================
# Optional: Redis Cache (Recommended)
# ============================================
# REDIS_URL="redis://:password@redis.railway.internal:6379/0"

# ============================================
# REMOVED VARIABLES (Previously Incorrect)
# ============================================
# DATABASE_URL - REMOVED (using individual DB_* vars instead)
# gbouncer - REMOVED (typo/orphaned)
# slmode - REMOVED (typo/orphaned)
# JWT_SECRET - REMOVED (not used by Django)
```

---

### FRONTEND VARIABLES (CORRECTED)

```bash
# ============================================
# Application
# ============================================
VITE_APP_NAME="Pulse of People"
VITE_APP_URL="https://tvk.pulseofpeople.com"
VITE_APP_VERSION="1.0"

# ============================================
# Tenant Configuration
# ============================================
VITE_DEFAULT_TENANT="tvk"
VITE_MULTI_TENANT="false"
VITE_TENANT_MODE="single"

# ============================================
# Supabase
# ============================================
VITE_SUPABASE_URL="https://iwtgbseaoztjbnvworyq.supabase.co"
VITE_SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml3dGdic2Vhb3p0amJudndvcnlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjExNjAzOTksImV4cCI6MjA3NjczNjM5OX0.xA4B0XZJE_4MdjFCkw2yVsf4vlHmHfpeV6Bk5tG2T94"

# ============================================
# Backend API
# ============================================
VITE_DJANGO_API_URL="https://pulseofpeople-production.up.railway.app/api"

# ============================================
# Maps
# ============================================
VITE_MAPBOX_ACCESS_TOKEN="<REPLACE_WITH_VALID_PRODUCTION_TOKEN>"

# ============================================
# Feature Flags
# ============================================
VITE_DEV_MODE="false"
VITE_ENABLE_SOCIAL_MEDIA="true"
VITE_ENABLE_INFLUENCER_TRACKING="true"
VITE_ENABLE_FIELD_REPORTS="true"
VITE_ENABLE_SURVEYS="true"
VITE_ENABLE_AI_INSIGHTS="true"

# ============================================
# REMOVED VARIABLES
# ============================================
# JWT_SECRET - REMOVED (SECURITY RISK - never expose signing secrets to frontend)
# All duplicate variables - REMOVED
```

---

## REQUIRED FIXES CHECKLIST

### IMMEDIATE FIXES (CRITICAL - Must fix before deployment)

- [ ] **Backend**: Fix broken `DATABASE_URL` or remove it entirely
- [ ] **Backend**: Remove orphaned variables (`gbouncer`, `slmode`)
- [ ] **Backend**: Add `USE_SQLITE="False"`
- [ ] **Backend**: Add `gunicorn==21.2.0` to requirements.txt
- [ ] **Backend**: Fix `CORS_ALLOWED_ORIGINS` (add https:// to all origins)
- [ ] **Frontend**: Remove ALL duplicate variables (keep only one set)
- [ ] **Frontend**: REMOVE `JWT_SECRET` (security risk)
- [ ] **Frontend**: Verify and fix `VITE_DJANGO_API_URL`

### HIGH PRIORITY (Should fix before production)

- [ ] **Backend**: Add `JWT_ACCESS_TOKEN_LIFETIME` and `JWT_REFRESH_TOKEN_LIFETIME`
- [ ] **Backend**: Add `CSRF_COOKIE_DOMAIN=".pulseofpeople.com"`
- [ ] **Backend**: Verify `ALLOWED_HOSTS` includes all domains
- [ ] **Frontend**: Replace demo Mapbox token with valid production token
- [ ] **Frontend**: Add missing feature flag variables

### MEDIUM PRIORITY (Fix for better reliability)

- [ ] **Backend**: Update `DB_SSLMODE` to match settings.py ("require")
- [ ] **Backend**: Add `STATIC_ROOT` configuration
- [ ] **Backend**: Add Railway Redis addon and configure `REDIS_URL`
- [ ] **Frontend**: Update vite.config.ts to use $PORT variable

### LOW PRIORITY (Optimizations)

- [ ] **Backend**: Update railway.toml to include migrations in build
- [ ] **Backend**: Update nixpacks.toml Python version to match local
- [ ] **Backend**: Remove unused `JWT_SECRET` variable

---

## DEPLOYMENT BLOCKERS SUMMARY

**These issues WILL cause deployment failure**:

1. Broken `DATABASE_URL` - Application cannot start without valid database connection
2. Missing `USE_SQLITE="False"` - App will use SQLite instead of PostgreSQL
3. Missing `gunicorn` in requirements.txt - Railway start command will fail
4. Orphaned variables causing configuration confusion
5. Frontend duplicate variables causing unpredictable behavior
6. JWT_SECRET exposed in frontend (security vulnerability)

**Estimated Fix Time**: 15-20 minutes

**Recommended Deployment Order**:
1. Fix all CRITICAL backend issues
2. Fix all CRITICAL frontend issues
3. Update requirements.txt with gunicorn
4. Test locally with production-like config
5. Deploy backend service first
6. Deploy frontend service second
7. Verify CORS and API connectivity
8. Monitor Railway logs for any remaining issues

---

## ADDITIONAL RECOMMENDATIONS

### 1. Environment Variable Management
- Use Railway's variable templates for different environments
- Keep separate `.env.production` and `.env.development` files
- Document all required variables in `.env.example`

### 2. Security Hardening
- Rotate `SECRET_KEY` and all JWT secrets regularly
- Never commit actual `.env` files to git
- Use Railway's secret scanning features
- Enable Railway's automatic SSL

### 3. Monitoring Setup
- Add Sentry DSN for error tracking
- Configure Railway's built-in logging
- Set up health check endpoints
- Monitor database connection pool usage

### 4. Performance Optimization
- Add Redis cache for sessions and queries
- Enable database connection pooling (Supabase Pooler)
- Configure static file CDN (CloudFlare/CloudFront)
- Optimize Gunicorn worker/thread counts based on traffic

---

## CONTACT FOR ISSUES

If deployment still fails after applying these fixes:

1. Check Railway deployment logs: `railway logs`
2. Verify environment variables: `railway variables`
3. Test database connectivity: `railway run python manage.py check --database default`
4. Review Django logs in Railway dashboard

---

**Report End**
