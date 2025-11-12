# Security Analysis - Hybrid Supabase + Django Architecture

## Executive Summary

**Your teammates are RIGHT to question this approach.**

The hybrid architecture has **significant security concerns** for production use, especially when exposing APIs to third-party clients.

---

## 🔍 Current Architecture Security Assessment

### Current Flow

```
┌─────────────────┐
│  User/Client    │
│  (Frontend/API) │
└────────┬────────┘
         │
         │ 1. Login with Supabase
         ↓
┌─────────────────┐
│  Supabase Auth  │ ← Authentication provider
│  (auth.users)   │
└────────┬────────┘
         │
         │ 2. Returns JWT with UUID
         │
         ↓
┌─────────────────┐
│  Django Backend │
│  + UserProfile  │ ← Application logic
│  (auth_user)    │
└─────────────────┘
         │
         │ 3. Lookup by supabase_uid
         │
         ↓
┌─────────────────┐
│  PostgreSQL     │
│  + RLS Policies │ ← Data layer
└─────────────────┘
```

---

## ⚠️ Security Vulnerabilities

### 1. **JWT Token Validation Gap**

**Issue:**
When clients call your API with a Supabase JWT token, you need to validate it. But there's a critical gap:

```python
# Current authentication (api/authentication.py)
class HybridAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # Validates JWT signature with SUPABASE_JWT_SECRET
        jwt_payload = jwt.decode(token, SUPABASE_JWT_SECRET, ...)

        # Problem: What if the JWT is expired?
        # Problem: What if the user was deleted in Supabase but JWT still valid?
        # Problem: What if JWT was issued for different app?
```

**Attack Vector:**
- Attacker steals a valid JWT token
- User is deleted/banned in Supabase
- Token still validates because you're only checking signature
- **Attacker has access until token expires (default: 1 hour)**

**Fix Required:**
```python
# Verify token with Supabase (real-time check)
from supabase import create_client

def authenticate(self, request):
    token = self.get_token_from_header(request)

    # Option 1: Verify with Supabase (secure but slow)
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        user = supabase.auth.get_user(token)  # ← Real-time verification
        if not user:
            raise AuthenticationFailed('Invalid token')
    except Exception:
        raise AuthenticationFailed('Token validation failed')

    # Now lookup in Django
    profile = UserProfile.objects.get(supabase_uid=user.id)
    return (profile.user, None)
```

**Performance Impact:**
- Every API request makes a call to Supabase
- Latency: +100-300ms per request
- Supabase rate limits apply

---

### 2. **Two Sources of Truth = Race Conditions**

**Issue:**
User data exists in TWO places:

```
Supabase auth.users:
- email
- password hash
- email_confirmed
- phone
- metadata

Django auth_user + UserProfile:
- email (duplicate!)
- role
- organization
- permissions
```

**Attack Scenario:**
1. Admin changes user email in Django: `old@email.com` → `new@email.com`
2. Supabase still has `old@email.com`
3. Attacker logs in with `old@email.com` (still works in Supabase!)
4. Django sees `supabase_uid` and loads profile
5. **Attacker accesses data with old, revoked email**

**Fix Required:**
- Sync email changes to Supabase immediately
- OR use Supabase as single source of truth for email

---

### 3. **RLS Policies Don't Apply to Django**

**Critical Issue:**

```sql
-- RLS policies filter by organization_id from JWT
CREATE POLICY "Users can view organization data"
  ON api_campaign
  FOR SELECT
  USING (organization_id = auth.get_user_organization_id());
```

**But when Django queries the database:**
- Django uses a **service connection** (not user connection)
- Service connection **bypasses RLS policies**!
- Django sees ALL data across ALL organizations

**This means:**
```python
# In Django view
Campaign.objects.all()  # ← Returns ALL campaigns (no RLS filtering!)

# RLS only works when:
# - Querying through Supabase client (frontend)
# - Using user's JWT token for connection
```

**Fix Options:**

**Option A: Apply filters manually in Django**
```python
# Every query must filter by organization
def get_campaigns(request):
    user_org = request.user.profile.organization
    campaigns = Campaign.objects.filter(organization=user_org)
```

**Option B: Use Supabase RLS from Django (complex)**
```python
# Create a new DB connection per request with user's JWT
# This is extremely complex and not recommended
```

---

### 4. **Third-Party API Access - Major Security Hole**

**The Big Problem:**

When third-party clients call your API, they can't use Supabase Auth!

```
Third-Party Client (e.g., mobile app, partner system)
   │
   │ How do they authenticate?
   │
   ↓
Your Django API
   │
   │ Expects Supabase JWT?
   │ OR API key?
   │ OR OAuth?
   └→ UNCLEAR!
```

**Current Issues:**

1. **If using Supabase JWT:**
   - Third-party needs Supabase credentials (security risk!)
   - They see your Supabase project structure
   - Can potentially access Supabase directly

2. **If using API Keys:**
   - Where do you validate them? (No API key table exists)
   - How do you map API key → organization → permissions?
   - No rate limiting system

3. **If using OAuth:**
   - Need to implement full OAuth2 server
   - Complex token management
   - Refresh token rotation

---

## 🎯 Recommended Architecture for Production

### Option A: Supabase for Frontend, API Keys for Third-Party (Hybrid)

```
┌──────────────────┐
│  Web Frontend    │──→ Supabase Auth ──→ Supabase JWT ──→ Your API
└──────────────────┘

┌──────────────────┐
│  Mobile App      │──→ Supabase Auth ──→ Supabase JWT ──→ Your API
└──────────────────┘

┌──────────────────┐
│  Third-Party API │──→ API Key Auth  ──→ API Key Token ──→ Your API
└──────────────────┘
```

**Implementation:**

```python
# models.py
class APIKey(models.Model):
    key = models.CharField(max_length=64, unique=True)
    secret_hash = models.CharField(max_length=128)  # bcrypt hash
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    scopes = models.JSONField(default=list)  # ['read:campaigns', 'write:voters']
    is_active = models.BooleanField(default=True)
    last_used_at = models.DateTimeField(null=True)
    expires_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['key']),
        ]

# authentication.py
class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return None

        try:
            key_obj = APIKey.objects.select_related('organization').get(
                key=api_key,
                is_active=True
            )

            # Check expiration
            if key_obj.expires_at and key_obj.expires_at < timezone.now():
                raise AuthenticationFailed('API key expired')

            # Update last used
            key_obj.last_used_at = timezone.now()
            key_obj.save(update_fields=['last_used_at'])

            # Create a pseudo-user for permission checking
            user = AnonymousUser()
            user.organization = key_obj.organization
            user.api_key_scopes = key_obj.scopes

            return (user, key_obj)

        except APIKey.DoesNotExist:
            raise AuthenticationFailed('Invalid API key')

# views.py
class MultiAuthAPIView(APIView):
    authentication_classes = [HybridAuthentication, APIKeyAuthentication]

    def get(self, request):
        # Works with both Supabase JWT and API Keys
        user_org = request.user.profile.organization if hasattr(request.user, 'profile') \
                   else request.user.organization

        campaigns = Campaign.objects.filter(organization=user_org)
        return Response(...)
```

**Pros:**
- ✅ Frontend uses Supabase (easy, secure)
- ✅ Third-party uses API keys (standard practice)
- ✅ Fine-grained scopes/permissions
- ✅ Easy to revoke access

**Cons:**
- ⚠️ Need to build API key management
- ⚠️ Two authentication flows to maintain

---

### Option B: Full OAuth2 Provider (Enterprise-Grade)

**Use Django OAuth Toolkit:**

```bash
pip install django-oauth-toolkit
```

```python
# settings.py
INSTALLED_APPS = [
    'oauth2_provider',
]

OAUTH2_PROVIDER = {
    'SCOPES': {
        'read:campaigns': 'Read campaigns',
        'write:campaigns': 'Create/update campaigns',
        'read:voters': 'Read voters',
        'write:voters': 'Create/update voters',
    },
    'ACCESS_TOKEN_EXPIRE_SECONDS': 3600,
    'REFRESH_TOKEN_EXPIRE_SECONDS': 86400 * 30,
}
```

**Flow:**
```
1. Client registers application → Gets client_id + client_secret
2. Client requests token:
   POST /oauth/token/
   {
     "grant_type": "client_credentials",
     "client_id": "...",
     "client_secret": "...",
     "scope": "read:campaigns write:voters"
   }

3. Get access token:
   {
     "access_token": "...",
     "expires_in": 3600,
     "token_type": "Bearer"
   }

4. Use token:
   GET /api/campaigns/
   Authorization: Bearer <access_token>
```

**Pros:**
- ✅ Industry standard (OAuth2)
- ✅ Token refresh mechanism
- ✅ Scope-based permissions
- ✅ Works with any client

**Cons:**
- ⚠️ More complex to implement
- ⚠️ Requires client registration workflow

---

### Option C: Move Everything to Supabase (Simplest)

**Abandon Django auth entirely, use Supabase for everything:**

```python
# Remove Django auth_user dependency
class UserProfile(models.Model):
    supabase_uid = models.UUIDField(primary_key=True)  # No FK to auth_user
    email = models.EmailField(unique=True)
    role = models.CharField(...)
    organization = models.ForeignKey(...)
```

**All auth through Supabase:**
- Web: Supabase Auth
- Mobile: Supabase Auth
- Third-party: Supabase Service Role + RLS

**Pros:**
- ✅ Single source of truth
- ✅ RLS policies work everywhere
- ✅ Built-in token management

**Cons:**
- ❌ Lose Django admin (unless you rebuild it)
- ❌ Third-party gets direct DB access (security risk!)
- ❌ Can't easily add complex business logic

---

## 🔒 Security Best Practices Checklist

### Current Issues

- [ ] ❌ JWT tokens not verified with Supabase (real-time)
- [ ] ❌ No token revocation mechanism
- [ ] ❌ Email sync between Supabase ↔ Django missing
- [ ] ❌ RLS policies don't apply to Django queries
- [ ] ❌ No API key system for third-party clients
- [ ] ❌ No rate limiting on API endpoints
- [ ] ❌ No audit logging for API access
- [ ] ❌ Service role key stored in .env (not rotated)

### Required Fixes

- [ ] ✅ Implement real-time JWT verification
- [ ] ✅ Add API key authentication for third-party
- [ ] ✅ Manual organization filtering in all Django queries
- [ ] ✅ Add rate limiting (django-ratelimit)
- [ ] ✅ Implement audit logging
- [ ] ✅ Rotate service role keys quarterly
- [ ] ✅ Add CORS restrictions
- [ ] ✅ Implement request signing for sensitive operations

---

## 🎯 My Recommendation

**For your use case (political platform with third-party integrations), use:**

**Hybrid Architecture with API Keys:**

1. **Frontend/Mobile Apps** → Supabase Auth (existing)
2. **Third-Party APIs** → API Key Authentication (new)
3. **Django Backend** → Manual organization filtering (always)
4. **RLS** → Only for direct Supabase client queries (limited use)

**Implementation Priority:**

**Phase 1: Fix Current Issues (This Week)**
1. Add `supabase_uid` to UserProfile ✓ (already discussed)
2. Implement real-time JWT verification
3. Add organization filtering to all Django views
4. Test end-to-end auth flow

**Phase 2: API Key System (Next Week)**
1. Create APIKey model
2. Build API key generation endpoint
3. Add APIKeyAuthentication class
4. Document API key usage

**Phase 3: Security Hardening (Week 3)**
1. Add rate limiting
2. Implement audit logging
3. Add request signing for sensitive operations
4. Security audit and penetration testing

---

## 📊 Comparison: Is This Secure Enough?

### Industry Standards

| Feature | Your Current Setup | Industry Standard | Status |
|---------|-------------------|-------------------|--------|
| **Auth Provider** | Supabase Auth | Auth0, Cognito, Keycloak | ✅ Good |
| **Token Type** | JWT | JWT or OAuth2 | ✅ Good |
| **Token Validation** | Local signature check | Real-time verification | ❌ **Needs Fix** |
| **Multi-tenancy** | UUID in JWT | Organization filtering | ⚠️ **Partial** |
| **RLS Enforcement** | Supabase only | All layers | ❌ **Django bypasses** |
| **Third-Party Auth** | None | API Keys or OAuth2 | ❌ **Missing** |
| **Rate Limiting** | None | Token bucket / Sliding window | ❌ **Missing** |
| **Audit Logging** | Partial | All API calls logged | ❌ **Incomplete** |

**Verdict:** ⚠️ **NOT production-ready without fixes**

---

## 🚨 Critical Security Gaps

### 1. No Real-Time Token Verification
**Risk Level:** 🔴 **CRITICAL**

**Attack:** Stolen tokens remain valid until expiration (1 hour)

**Fix:** Add Supabase token verification:
```python
supabase.auth.get_user(token)  # Verifies in real-time
```

### 2. Django Bypasses RLS
**Risk Level:** 🔴 **CRITICAL**

**Attack:** SQL injection or compromised Django app accesses all orgs

**Fix:** Manual filtering EVERYWHERE:
```python
# EVERY Django query must include:
.filter(organization=request.user.profile.organization)
```

### 3. No Third-Party Auth
**Risk Level:** 🟠 **HIGH**

**Attack:** Can't safely expose APIs to partners

**Fix:** Implement API Key system (detailed above)

---

## ✅ Final Answer

**Question:** "Will this be secure? Will third-party APIs work?"

**Answer:**

1. **Current setup:** ❌ **NOT secure** for production
   - Missing real-time token verification
   - Django bypasses RLS policies
   - No third-party auth mechanism

2. **With fixes:** ✅ **Yes, can be secure**
   - Add real-time JWT verification
   - Implement API key auth for third-parties
   - Manual organization filtering in Django
   - Add rate limiting and audit logs

3. **Your teammates are correct:** ⚠️ **This needs work**
   - The architecture can work, but requires hardening
   - Third-party API access needs separate auth system
   - Current gaps are exploitable

**Recommendation:**
Proceed with hybrid architecture BUT implement the security fixes in Phase 1 and Phase 2 before launching to production.

---

**Ready to implement the fixes?** I can help you build:
1. Real-time JWT verification
2. API Key authentication system
3. Organization filtering helpers
4. Rate limiting middleware
5. Audit logging system

Let me know which to tackle first!
