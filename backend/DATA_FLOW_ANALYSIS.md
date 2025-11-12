# Data Flow & Connection Analysis - Hybrid Architecture

## Executive Summary

**Will it work?** ⚠️ **Yes, but with PERFORMANCE ISSUES and DATA SYNC problems**

The data flow has **architectural bottlenecks** that will cause problems at scale.

---

## 🔄 Current Data Flow Architecture

### Scenario 1: User Login (Frontend → Supabase → Django)

```
┌─────────────────┐
│  React Frontend │
└────────┬────────┘
         │
         │ 1. User enters email/password
         │
         ↓
┌─────────────────────────────────────┐
│  Supabase Auth API                  │
│  POST /auth/v1/token                │
│  { email, password }                │
└────────┬────────────────────────────┘
         │
         │ 2. Returns JWT + user metadata
         │    {
         │      access_token: "eyJ...",
         │      user: { id: "uuid...", email: "..." }
         │    }
         │
         ↓
┌─────────────────┐
│  React Frontend │
│  stores token   │
└────────┬────────┘
         │
         │ 3. Fetch user profile
         │    GET /api/auth/profile/
         │    Authorization: Bearer eyJ...
         │
         ↓
┌─────────────────────────────────────┐
│  Django Backend                     │
│  HybridAuthentication validates JWT │
└────────┬────────────────────────────┘
         │
         │ 4. Extract supabase_uid from JWT
         │    supabase_uid = jwt_payload['sub']
         │
         ↓
┌─────────────────────────────────────┐
│  PostgreSQL Query                   │
│  SELECT * FROM api_userprofile      │
│  WHERE supabase_uid = 'uuid...'     │
└────────┬────────────────────────────┘
         │
         │ 5. Return user profile data
         │
         ↓
┌─────────────────┐
│  React Frontend │
│  displays data  │
└─────────────────┘
```

**Performance:** ✅ **Good** (1 auth request + 1 DB query)

**Issues:**
- ⚠️ JWT validation happens on EVERY request (no caching)
- ⚠️ No connection pooling if not configured

---

### Scenario 2: Fetch Campaigns (Django Backend API)

```
┌─────────────────┐
│  React Frontend │
│  GET /api/campaigns/ │
│  Authorization: Bearer <jwt>
└────────┬────────┘
         │
         ↓
┌─────────────────────────────────────┐
│  Django View                        │
│  1. Authenticate user (JWT)         │
│  2. Get user's organization         │
│  3. Query campaigns                 │
└────────┬────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────┐
│  PostgreSQL                         │
│  SELECT * FROM api_campaign         │
│  WHERE organization_id = ?          │
└────────┬────────────────────────────┘
         │
         ↓
┌─────────────────┐
│  JSON Response  │
└─────────────────┘
```

**Performance:** ✅ **Good** (1 DB query with index)

**Issues:**
- ✅ No issues if organization_id is indexed
- ⚠️ Could return too much data if no pagination

---

### Scenario 3: Real-Time Notifications (Supabase Direct)

```
┌─────────────────┐
│  React Frontend │
│  useEffect(() => {
│    supabase.channel('notifications')
│      .on('INSERT', callback)
│  })
└────────┬────────┘
         │
         │ WebSocket connection
         │
         ↓
┌─────────────────────────────────────┐
│  Supabase Realtime Server           │
│  Listens to PostgreSQL changes      │
└────────┬────────────────────────────┘
         │
         │ PostgreSQL LISTEN/NOTIFY
         │
         ↓
┌─────────────────────────────────────┐
│  PostgreSQL                         │
│  NOTIFY notifications_channel       │
└────────┬────────────────────────────┘
         │
         │ Triggered by INSERT
         │
         ↓
┌─────────────────────────────────────┐
│  Django Backend                     │
│  Notification.objects.create(...)   │
└─────────────────────────────────────┘
```

**Performance:** ✅ **Excellent** (real-time, no polling)

**Issues:**
- ⚠️ RLS policies MUST be configured correctly
- ⚠️ Each client = 1 WebSocket connection (scales well up to 10k connections)

---

## 🚨 Critical Data Flow Issues

### Issue #1: **No Connection Pooling (Default Django)**

**Problem:**

```python
# Django settings.py (current)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': '...',
        'HOST': 'db.iwtgbseaoztjbnvworyq.supabase.co',
        # ❌ No connection pool settings!
    }
}
```

**What happens:**
1. Each Django worker opens connections to PostgreSQL
2. Default: 100 max connections per PostgreSQL database
3. Each gunicorn worker = ~2-5 connections
4. With 10 workers: 10 × 5 = **50 connections**
5. Under load: **connection exhaustion** → `FATAL: too many connections`

**Fix Required:**

```python
# Install pgbouncer or use connection pooling
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': '...',
        'HOST': 'db.iwtgbseaoztjbnvworyq.supabase.co',
        'PORT': 5432,
        'CONN_MAX_AGE': 600,  # ← Keep connections alive for 10 minutes
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000'  # 30s query timeout
        }
    }
}

# Or use django-db-connection-pool
DATABASES = {
    'default': {
        'ENGINE': 'dj_db_conn_pool.backends.postgresql',
        'POOL_OPTIONS': {
            'POOL_SIZE': 10,
            'MAX_OVERFLOW': 20,
        }
    }
}
```

**Performance Impact:**
- Without pooling: **5-20ms per request** (connection setup)
- With pooling: **<1ms per request**

---

### Issue #2: **JWT Validation on Every Request (No Cache)**

**Problem:**

```python
# Current: api/authentication.py
class HybridAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = self.get_token_from_header(request)

        # ❌ Decode JWT on EVERY request (no caching!)
        jwt_payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=['HS256']
        )

        # ❌ Query database on EVERY request
        user = User.objects.get(email=jwt_payload['email'])
        return (user, None)
```

**What happens:**
1. Request comes in with JWT token
2. Decode JWT (crypto operations = CPU intensive)
3. Query database to get user
4. **Repeat for EVERY API call**

**At scale:**
- 100 requests/sec × 5ms JWT decode = **500ms CPU time/sec**
- 100 requests/sec × 10ms DB query = **1 second DB time/sec**

**Fix Required:**

```python
# Use Django cache
from django.core.cache import cache
import hashlib

class HybridAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = self.get_token_from_header(request)

        # Cache key based on token hash
        token_hash = hashlib.sha256(token.encode()).hexdigest()[:16]
        cache_key = f'auth_user_{token_hash}'

        # Try to get from cache
        user = cache.get(cache_key)
        if user:
            return (user, None)  # ✅ Cache hit (fast!)

        # Cache miss - validate token
        jwt_payload = jwt.decode(token, SUPABASE_JWT_SECRET, ...)

        # Get user from DB
        supabase_uid = jwt_payload['sub']
        profile = UserProfile.objects.select_related('user').get(
            supabase_uid=supabase_uid
        )
        user = profile.user

        # Cache for token lifetime (1 hour)
        exp = jwt_payload.get('exp', 0)
        ttl = max(exp - time.time(), 0)
        cache.set(cache_key, user, timeout=int(ttl))

        return (user, None)
```

**Performance Impact:**
- Without cache: **15ms per request** (JWT + DB)
- With cache: **<1ms per request** (99% cache hit rate)

---

### Issue #3: **N+1 Query Problem**

**Problem:**

```python
# views.py (bad - N+1 queries)
def get_campaigns(request):
    campaigns = Campaign.objects.filter(
        organization=request.user.profile.organization
    )
    # ❌ Returns campaigns without related data

    serializer = CampaignSerializer(campaigns, many=True)
    return Response(serializer.data)

# serializers.py
class CampaignSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name')
    # ❌ This triggers a query for EACH campaign!

    class Meta:
        model = Campaign
        fields = ['id', 'name', 'created_by_name', ...]
```

**What happens:**
1. Query campaigns: `SELECT * FROM api_campaign WHERE organization_id = ?` (1 query)
2. For each campaign, get creator: `SELECT * FROM auth_user WHERE id = ?` (N queries)
3. **Total: 1 + N queries** (if 100 campaigns = 101 queries!)

**Database logs:**
```sql
SELECT * FROM api_campaign WHERE organization_id = 1;  -- 1 query
SELECT * FROM auth_user WHERE id = 5;  -- Query #2
SELECT * FROM auth_user WHERE id = 8;  -- Query #3
SELECT * FROM auth_user WHERE id = 12;  -- Query #4
-- ... 97 more queries!
```

**Fix Required:**

```python
# Use select_related() and prefetch_related()
def get_campaigns(request):
    campaigns = Campaign.objects.filter(
        organization=request.user.profile.organization
    ).select_related(
        'created_by',          # JOIN auth_user
        'target_district',      # JOIN api_district
        'target_constituency'   # JOIN api_constituency
    ).prefetch_related(
        'voter_interactions'    # Separate query for M2M
    )
    # ✅ Now only 2-3 queries total instead of 101!

    serializer = CampaignSerializer(campaigns, many=True)
    return Response(serializer.data)
```

**Performance Impact:**
- Without optimization: **101 queries × 10ms = 1010ms** (1 second!)
- With optimization: **2 queries × 10ms = 20ms**
- **50x faster!**

---

### Issue #4: **Supabase API Rate Limits**

**Problem:**

If you use Supabase client directly from frontend for real-time features:

```typescript
// Frontend code
const { data } = await supabase
  .from('api_campaign')
  .select('*')
  .eq('organization_id', orgId)
```

**Supabase Free Tier Limits:**
- **500 MB database**
- **50,000 monthly active users**
- **2 GB egress** (data transfer out)
- **200 concurrent realtime connections**

**What happens at scale:**
- 1000 users × 100 API calls/day = 100,000 requests/day
- Each response = 5 KB average
- **500 MB data transfer/day**
- **15 GB/month** → Exceeds 2 GB limit!

**Costs:**
- Overage: **$0.09/GB** = **$1.17/day** = **$35/month** extra

**Fix Required:**

Use Django backend for heavy queries, Supabase only for real-time:

```typescript
// ❌ Don't do this (expensive)
const campaigns = await supabase.from('api_campaign').select('*')

// ✅ Do this (cheaper)
const campaigns = await fetch('/api/campaigns/', {
  headers: { Authorization: `Bearer ${token}` }
})

// ✅ Only use Supabase for real-time
supabase.channel('notifications')
  .on('postgres_changes', { ... }, callback)
  .subscribe()
```

---

### Issue #5: **Data Sync Lag Between Supabase & Django**

**Problem:**

When you update data via Django, Supabase real-time doesn't notify immediately:

```python
# Django view - update campaign
def update_campaign(request, campaign_id):
    campaign = Campaign.objects.get(id=campaign_id)
    campaign.status = 'completed'
    campaign.save()  # ← Saves to PostgreSQL

    # ❌ Real-time subscribers NOT notified immediately!
    # PostgreSQL NOTIFY happens, but takes 100-500ms
    return Response({'status': 'ok'})
```

**Timeline:**
1. Django saves to PostgreSQL: **T=0ms**
2. PostgreSQL triggers NOTIFY: **T=10ms**
3. Supabase Realtime picks up change: **T=100ms**
4. Frontend receives update: **T=150ms**

**Total lag: 150ms** (acceptable for most cases)

**But if you have:**
- High-frequency updates (e.g., live voting counts)
- Multiple users editing simultaneously
- **Race conditions** can occur!

**Example Race Condition:**

```
User A (Frontend)                    User B (Frontend)
│                                    │
├─ Read campaign.vote_count = 100   │
│                                    ├─ Read campaign.vote_count = 100
├─ Increment to 101                 │
│                                    ├─ Increment to 101
├─ Save to backend                  │
│                                    ├─ Save to backend
│                                    │
└─ Result: vote_count = 101 ❌      └─ Result: vote_count = 101 ❌
   (Should be 102!)
```

**Fix Required:**

Use atomic updates:

```python
# ❌ Bad (race condition)
campaign.vote_count += 1
campaign.save()

# ✅ Good (atomic)
from django.db.models import F

Campaign.objects.filter(id=campaign_id).update(
    vote_count=F('vote_count') + 1
)
```

---

## 📊 Complete Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          FRONTEND (React)                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   Login      │  │  API Calls   │  │  Real-time   │              │
│  │              │  │              │  │  Updates     │              │
│  └───────┬──────┘  └──────┬───────┘  └──────┬───────┘              │
└──────────┼─────────────────┼──────────────────┼────────────────────┘
           │                 │                  │
           │                 │                  │
           ↓                 ↓                  ↓
┌──────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Supabase Auth   │  │  Django Backend │  │  Supabase       │
│  /auth/v1/token  │  │  /api/*         │  │  Realtime       │
└────────┬─────────┘  └────────┬────────┘  └────────┬────────┘
         │                     │                     │
         │                     │                     │
         └─────────────────────┼─────────────────────┘
                               │
                               ↓
                    ┌────────────────────┐
                    │    PostgreSQL      │
                    │   (Supabase DB)    │
                    │                    │
                    │  - auth.users      │
                    │  - auth_user       │
                    │  - api_userprofile │
                    │  - api_campaign    │
                    │  - ... (all tables)│
                    └────────────────────┘
```

**Connection Counts:**

```
Frontend (1000 concurrent users)
├─ Supabase Auth: 0 persistent connections (REST API)
├─ Django Backend: 0 persistent connections (REST API)
└─ Supabase Realtime: 200-1000 WebSocket connections

Django Backend (10 gunicorn workers)
└─ PostgreSQL: 10-50 connections (pooled)

Total PostgreSQL Connections: 10-50
(Well within 100 connection limit ✅)
```

---

## ⚡ Performance Benchmarks

### Expected Response Times

| Operation | Without Optimization | With Optimization | Target |
|-----------|---------------------|-------------------|--------|
| **User Login** | 200-500ms | 150-300ms | <300ms ✅ |
| **Get Profile** | 50-100ms | 10-20ms | <50ms ✅ |
| **List Campaigns** | 500-2000ms | 50-100ms | <200ms ✅ |
| **Create Campaign** | 100-300ms | 50-150ms | <200ms ✅ |
| **Real-time Update** | 100-500ms | 50-150ms | <200ms ✅ |

### Concurrent User Capacity

| Configuration | Max Users | Cost/Month |
|---------------|-----------|------------|
| **Free Tier** | 50-100 | $0 |
| **Supabase Pro** | 500-1000 | $25 |
| **Supabase Pro + Redis** | 2000-5000 | $50 |
| **Enterprise** | 10,000+ | $200+ |

---

## ✅ Recommended Optimizations

### Priority 1: Connection Pooling

```python
# settings.py
pip install django-db-connection-pool

DATABASES = {
    'default': {
        'ENGINE': 'dj_db_conn_pool.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': '...',
        'HOST': 'db.iwtgbseaoztjbnvworyq.supabase.co',
        'PORT': 5432,
        'POOL_OPTIONS': {
            'POOL_SIZE': 10,       # Connections per worker
            'MAX_OVERFLOW': 10,     # Extra connections if needed
            'RECYCLE': 3600,        # Recycle after 1 hour
        }
    }
}
```

### Priority 2: Authentication Caching

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'pulseofpeople',
        'TIMEOUT': 3600,  # 1 hour default
    }
}

# Or use in-memory cache (simpler, but doesn't scale across workers)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}
```

### Priority 3: Query Optimization

```python
# Create a base queryset manager
class OrganizationQuerySet(models.QuerySet):
    def for_user(self, user):
        """Filter by user's organization"""
        return self.filter(organization=user.profile.organization)

    def with_relations(self):
        """Eager load common relations"""
        return self.select_related(
            'created_by',
            'organization',
            'target_district'
        ).prefetch_related(
            'voter_interactions',
            'assigned_users'
        )

class Campaign(models.Model):
    # ... fields ...

    objects = OrganizationQuerySet.as_manager()

# Usage
def get_campaigns(request):
    campaigns = Campaign.objects.for_user(request.user).with_relations()
    # ✅ Optimized queries automatically!
```

### Priority 4: Response Pagination

```python
# views.py
from rest_framework.pagination import PageNumberPagination

class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class CampaignViewSet(viewsets.ModelViewSet):
    pagination_class = StandardPagination

    def get_queryset(self):
        return Campaign.objects.for_user(self.request.user).with_relations()
```

---

## 🎯 Final Answer

**Question:** "What about connection and the flow of data? Will it work or will we have issues?"

**Answer:**

### ✅ **It WILL work**, but you'll have these issues:

1. **Connection Exhaustion** 🔴
   - Django default = no connection pooling
   - Fix: Add `django-db-connection-pool`
   - **Critical for production**

2. **Slow API Responses** 🟠
   - JWT validation + DB query on every request
   - N+1 query problems
   - Fix: Add caching + query optimization
   - **Important for user experience**

3. **Data Sync Lag** 🟡
   - 100-500ms delay for real-time updates
   - Race conditions possible
   - Fix: Use atomic updates
   - **Monitor in production**

4. **Rate Limit Costs** 🟡
   - Free tier insufficient for production
   - Fix: Use Django for heavy queries
   - **Budget consideration**

### 📋 Implementation Checklist

**Before Production:**
- [ ] ✅ Add connection pooling
- [ ] ✅ Implement authentication caching
- [ ] ✅ Optimize queries (select_related, prefetch_related)
- [ ] ✅ Add pagination to all list endpoints
- [ ] ✅ Set up monitoring (response times, connection counts)
- [ ] ✅ Load testing (100-1000 concurrent users)

**The architecture is sound, but needs these optimizations to perform well at scale.**

Ready to implement the fixes? I can help with:
1. Connection pooling setup
2. Caching configuration
3. Query optimization
4. Performance monitoring

Which should we tackle first?
