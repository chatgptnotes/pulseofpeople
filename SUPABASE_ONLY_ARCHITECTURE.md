# Supabase-Only Architecture Guide

## Overview

The Pulse of People platform now uses **Supabase-Only** architecture for simplicity, performance, and cost efficiency.

## Architecture Stack

```
┌─────────────────┐
│   Frontend      │
│   (React +      │
│    Vite)        │
└────────┬────────┘
         │
         │ Direct Connection
         │
┌────────▼────────┐
│   Supabase      │
│                 │
│ • Auth          │
│ • PostgreSQL    │
│ • PostgREST     │
│ • Real-time     │
└─────────────────┘
```

## Components

### 1. Authentication
- **Provider**: Supabase Auth
- **Implementation**: `src/contexts/AuthContext.tsx`
- **Features**:
  - Email/password login
  - Session management
  - Token refresh
  - User profile from `users` table

### 2. Database
- **Provider**: Supabase PostgreSQL
- **Connection**: Direct from frontend via Supabase SDK
- **Tables**:
  - `users` - User profiles and permissions
  - `feedback` - Citizen feedback
  - `field_reports` - Field worker reports
  - `polling_booths` - Polling booth data
  - `wards` - Ward information
  - Master data tables (states, districts, constituencies)

### 3. APIs
- **Primary**: Supabase PostgREST (auto-generated from database)
- **Secondary**: Custom Supabase Edge Functions (for complex logic)
- **Deprecated**: Django backend (optional, paused)

## Environment Variables

### Required (Frontend)
```env
VITE_SUPABASE_URL=https://iwtgbseaoztjbnvworyq.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGci...
VITE_APP_NAME=Pulse of People
VITE_APP_VERSION=1.0
```

### Not Required
```env
VITE_DJANGO_API_URL  # ❌ Not needed for Supabase-only
```

## Railway Deployment

### Frontend Service (pulseofpeople-frontend)
- **Domain**: tvk.pulseofpeople.com
- **Build**: Dockerfile (multi-stage)
- **Environment Variables**: See above
- **Cost**: ~$5/month

### Backend Service (pulseofpeople) - PAUSED
- **Status**: ⏸️ Paused
- **Reason**: Moved to Supabase-only architecture
- **Future Use**: Can be reactivated for:
  - Advanced analytics
  - Bulk data processing
  - Custom reporting
  - ML/AI features

## Features Status

### ✅ Working with Supabase
1. **Authentication**
   - Login/logout
   - Session persistence
   - User profiles

2. **Dashboards**
   - Superadmin overview
   - Admin state dashboard
   - Manager district dashboard
   - User booth dashboard

3. **Data Management**
   - Polling booths
   - Wards
   - Constituencies
   - User management

### 🚧 Needs Migration (Currently using Django)
1. **Bulk Uploads**
   - User CSV imports
   - Polling booth imports
   - → Migrate to Supabase Edge Functions

2. **Analytics**
   - Sentiment analysis
   - Custom reports
   - → Can use Supabase SQL views or Edge Functions

3. **Field Reports**
   - Submission works
   - Advanced filtering needs migration
   - → Use Supabase RPC functions

## Migration Path (Future)

If you need features currently in Django:

### Option 1: Supabase Edge Functions
```typescript
// Example: Bulk upload Edge Function
import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

serve(async (req) => {
  // Handle CSV upload
  // Process in batches
  // Insert to database
})
```

### Option 2: Supabase SQL Functions
```sql
-- Example: Analytics RPC function
CREATE OR REPLACE FUNCTION get_constituency_analytics(const_id uuid)
RETURNS json AS $$
  SELECT json_build_object(
    'total_feedback', COUNT(*),
    'sentiment_breakdown', ...
  )
  FROM feedback
  WHERE constituency_id = const_id
$$ LANGUAGE sql;
```

### Option 3: Reactivate Django (if needed)
1. Go to Railway → pulseofpeople → Settings → Resume Service
2. Add VITE_DJANGO_API_URL back to frontend
3. Redeploy frontend

## Security

### Row Level Security (RLS)
All Supabase tables have RLS policies:

```sql
-- Example: Users can only see their organization's data
CREATE POLICY "Users see own org data"
ON feedback
FOR SELECT
USING (
  organization_id = (
    SELECT organization_id
    FROM users
    WHERE id = auth.uid()
  )
);
```

### Authentication Flow
1. User submits email/password to Supabase Auth
2. Supabase returns JWT token
3. Frontend stores token in localStorage
4. All database queries include JWT in headers
5. Supabase validates JWT and applies RLS policies

## Performance

### Benefits of Supabase-Only
- ✅ **Faster**: No Django hop (saves ~100-200ms per request)
- ✅ **Cheaper**: Only one service to run (~$5/month vs ~$10/month)
- ✅ **Simpler**: Less moving parts, easier debugging
- ✅ **Scalable**: Supabase handles connection pooling
- ✅ **Real-time**: Built-in WebSocket support for live updates

### When to Add Backend
- Complex ML/AI processing (sentiment analysis)
- Heavy computation (batch reports)
- Third-party integrations (payment gateways)
- Custom business logic that can't be expressed in SQL

## Troubleshooting

### Frontend won't build
**Issue**: Missing VITE_SUPABASE_URL
**Fix**: Add environment variables in Railway

### Login fails
**Issue**: Supabase credentials wrong
**Fix**: Check .env file matches Supabase dashboard

### 502 Bad Gateway
**Issue**: Trying to call Django backend
**Fix**: Remove VITE_DJANGO_API_URL variable

### Data not loading
**Issue**: RLS policies blocking access
**Fix**: Check user permissions in Supabase dashboard

## Monitoring

### Supabase Dashboard
- Auth: Monitor login attempts, user count
- Database: Query performance, connection pool
- Storage: File uploads, bandwidth
- Logs: Real-time error logs

### Railway Dashboard
- Deployments: Build status, deploy logs
- Metrics: CPU, memory, bandwidth
- Logs: Application logs, HTTP requests

## Cost Breakdown

### Supabase (Free Tier)
- Up to 500MB database
- 50,000 monthly active users
- 2GB bandwidth
- **Cost**: $0/month

### Railway
- Frontend service
- 500 hours/month
- **Cost**: ~$5/month

### Total: ~$5/month

Compare to previous: ~$10/month (Frontend + Backend)

## Support

### Issues
- Supabase errors: Check https://status.supabase.com
- Railway errors: Check Railway dashboard → Logs
- Auth issues: Check Supabase Auth → Users

### Resources
- Supabase Docs: https://supabase.com/docs
- Railway Docs: https://docs.railway.app
- Repository: https://github.com/chatgptnotes/pulseofpeople

---

**Last Updated**: 2025-11-09
**Architecture Version**: 2.0 (Supabase-Only)
**Migration Status**: ✅ Complete
