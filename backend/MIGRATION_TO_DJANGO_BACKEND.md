# Complete Migration: Supabase Hybrid → Pure Django Backend

**Decision Date:** 2025-11-10
**Target Completion:** 3-4 weeks
**Team Size:** 2-3 developers

---

## Executive Summary

**FROM:** Hybrid Supabase Auth + Django Backend
**TO:** Pure Django Backend (Authentication, Database, APIs)

**Benefits:**
- ✅ Eliminates 12 critical production issues
- ✅ Single source of truth (Django)
- ✅ Full control over authentication flow
- ✅ No JWT validation latency
- ✅ Simpler architecture (easier to maintain)
- ✅ Standard Django ecosystem tools
- ✅ Better security (no dual-system gaps)
- ✅ Lower complexity (one system, not two)

**Trade-offs:**
- ⚠️ Need to implement email verification
- ⚠️ Need to implement password reset
- ⚠️ Lose Supabase's built-in real-time features (can use Django Channels)
- ⚠️ Need proper SMTP service for emails

---

## Migration Phases

### Phase 1: Planning & Preparation (Week 1)
### Phase 2: Core Backend Changes (Week 2)
### Phase 3: Cleanup & Testing (Week 3)
### Phase 4: Frontend Updates (Week 4)

---

## 📋 COMPLETE TODO LIST (150+ Items)

---

## PHASE 1: PLANNING & PREPARATION (Week 1)

### 1.1 Environment & Dependencies Setup (15 items)

- [ ] 1. Review current authentication flow documentation
- [ ] 2. Document all Supabase Auth touchpoints in codebase
- [ ] 3. Create migration timeline and milestones
- [ ] 4. Set up development environment for testing
- [ ] 5. Create feature branch: `migration/django-auth`
- [ ] 6. Install Django REST Framework SimpleJWT: `djangorestframework-simplejwt`
- [ ] 7. Install Django Email Backend dependencies
- [ ] 8. Install connection pooling: `django-db-connection-pool`
- [ ] 9. Install rate limiting: `django-ratelimit`
- [ ] 10. Install Redis for caching: `django-redis`
- [ ] 11. Install Celery for async tasks: `celery`
- [ ] 12. Set up email service (SendGrid/AWS SES/Mailgun)
- [ ] 13. Configure environment variables for Django auth
- [ ] 14. Update requirements.txt with new dependencies
- [ ] 15. Document rollback plan in case of issues

### 1.2 Database Schema Planning (10 items)

- [ ] 16. Audit all models using `supabase_uid`
- [ ] 17. Plan migration to remove `supabase_uid` field
- [ ] 18. Design email verification token model
- [ ] 19. Design password reset token model
- [ ] 20. Design API key model for third-party auth
- [ ] 21. Design audit log model
- [ ] 22. Plan user profile fields (phone verification, 2FA)
- [ ] 23. Review indexes needed for performance
- [ ] 24. Create ER diagram for new auth flow
- [ ] 25. Document data migration strategy

### 1.3 Architecture Documentation (10 items)

- [ ] 26. Document new authentication flow diagram
- [ ] 27. Document JWT token lifecycle (access + refresh)
- [ ] 28. Document API endpoint changes
- [ ] 29. Document user registration flow
- [ ] 30. Document password reset flow
- [ ] 31. Document email verification flow
- [ ] 32. Document API key authentication for third parties
- [ ] 33. Create security checklist for new architecture
- [ ] 34. Document rate limiting strategy
- [ ] 35. Create deployment checklist

---

## PHASE 2: CORE BACKEND CHANGES (Week 2)

### 2.1 Remove Supabase Dependencies (15 items)

- [ ] 36. Remove `supabase-py` from requirements.txt
- [ ] 37. Remove Supabase client initialization code
- [ ] 38. Remove `SUPABASE_URL` from settings
- [ ] 39. Remove `SUPABASE_SERVICE_ROLE_KEY` from settings
- [ ] 40. Remove `SUPABASE_ANON_KEY` from settings
- [ ] 41. Remove `SUPABASE_JWT_SECRET` from settings
- [ ] 42. Delete `api/utils/supabase_sync.py`
- [ ] 43. Delete `api/authentication.py` (SupabaseJWTAuthentication)
- [ ] 44. Delete `supabase_rls_policies.sql`
- [ ] 45. Remove Supabase client from management commands
- [ ] 46. Remove `cleanup_test_users.py` Supabase calls
- [ ] 47. Remove Supabase imports from views
- [ ] 48. Update .env.example to remove Supabase variables
- [ ] 49. Update .gitignore to remove Supabase-related files
- [ ] 50. Remove Supabase documentation references

### 2.2 Implement Django Authentication (25 items)

- [ ] 51. Configure `REST_FRAMEWORK` settings for JWT auth
- [ ] 52. Configure `SIMPLE_JWT` settings (access/refresh tokens)
- [ ] 53. Set token expiration: access=1h, refresh=7days
- [ ] 54. Create `api/authentication/jwt_auth.py`
- [ ] 55. Implement custom JWT claims (organization, role)
- [ ] 56. Create `TokenObtainPairView` with user data
- [ ] 57. Create `TokenRefreshView` endpoint
- [ ] 58. Create `TokenBlacklistView` (logout)
- [ ] 59. Install token blacklist: `rest_framework_simplejwt.token_blacklist`
- [ ] 60. Configure token blacklist in settings
- [ ] 61. Create user registration endpoint `/api/auth/register/`
- [ ] 62. Add email validation in registration
- [ ] 63. Add password strength validation
- [ ] 64. Create email verification model `EmailVerificationToken`
- [ ] 65. Generate verification tokens on registration
- [ ] 66. Create email verification endpoint `/api/auth/verify-email/<token>/`
- [ ] 67. Send verification email via Celery task
- [ ] 68. Create password reset model `PasswordResetToken`
- [ ] 69. Create password reset request endpoint `/api/auth/password-reset/`
- [ ] 70. Send password reset email via Celery task
- [ ] 71. Create password reset confirm endpoint `/api/auth/password-reset-confirm/`
- [ ] 72. Implement rate limiting on auth endpoints (5 attempts/hour)
- [ ] 73. Add CAPTCHA on registration (django-recaptcha)
- [ ] 74. Create user profile endpoint `/api/auth/me/`
- [ ] 75. Implement 2FA with TOTP (django-otp)

### 2.3 Database Migrations (20 items)

- [ ] 76. Create migration to remove `supabase_uid` from UserProfile
- [ ] 77. Create EmailVerificationToken model migration
- [ ] 78. Create PasswordResetToken model migration
- [ ] 79. Create APIKey model migration (third-party auth)
- [ ] 80. Create AuditLog model migration
- [ ] 81. Create RefreshToken blacklist migration
- [ ] 82. Add indexes on User.email (unique lookup)
- [ ] 83. Add indexes on UserProfile.organization (filtering)
- [ ] 84. Add indexes on AuditLog.timestamp (queries)
- [ ] 85. Add indexes on APIKey.key (authentication)
- [ ] 86. Create data migration: copy existing user emails
- [ ] 87. Ensure all users have is_active=True flag
- [ ] 88. Ensure all users have email_verified=False initially
- [ ] 89. Set admin users as email_verified=True
- [ ] 90. Run makemigrations for all changes
- [ ] 91. Run migrate on development database
- [ ] 92. Test rollback of migrations
- [ ] 93. Backup production database before migration
- [ ] 94. Run migrations on staging environment
- [ ] 95. Verify data integrity after migration

### 2.4 User Management Commands (10 items)

- [ ] 96. Rewrite `setup_supabase_users.py` → `setup_users.py` (Django only)
- [ ] 97. Remove Supabase Auth API calls
- [ ] 98. Use Django User.objects.create_user() only
- [ ] 99. Update cleanup command to use Django only
- [ ] 100. Create command: `send_verification_emails.py` (bulk)
- [ ] 101. Create command: `reset_user_password.py` (admin tool)
- [ ] 102. Create command: `generate_api_key.py` (third-party)
- [ ] 103. Create command: `revoke_api_key.py`
- [ ] 104. Update user creation to send welcome emails
- [ ] 105. Test all commands in development

### 2.5 API Endpoints & Views (20 items)

- [ ] 106. Update authentication class on all ViewSets to `JWTAuthentication`
- [ ] 107. Remove `HybridAuthentication` references
- [ ] 108. Create `AuthViewSet` with register/login/logout
- [ ] 109. Create `PasswordResetViewSet`
- [ ] 110. Create `EmailVerificationViewSet`
- [ ] 111. Create `UserProfileViewSet` with update endpoint
- [ ] 112. Implement organization-based filtering in all queries
- [ ] 113. Add `.filter(organization=request.user.profile.organization)` everywhere
- [ ] 114. Create custom QuerySet mixin `OrganizationFilterMixin`
- [ ] 115. Apply mixin to all models with organization field
- [ ] 116. Add permission classes to all endpoints
- [ ] 117. Implement role-based permissions (IsAdmin, IsManager, etc.)
- [ ] 118. Add pagination to all list endpoints (PageNumberPagination)
- [ ] 119. Add filtering, searching, ordering to ViewSets
- [ ] 120. Implement rate limiting on all endpoints
- [ ] 121. Add throttling: 1000 req/hour per user, 100/hour anon
- [ ] 122. Create health check endpoint `/api/health/`
- [ ] 123. Create API documentation with drf-spectacular
- [ ] 124. Update URL routing for new auth endpoints
- [ ] 125. Test all endpoints with Postman/Insomnia

### 2.6 Third-Party API Authentication (15 items)

- [ ] 126. Create APIKey model (key, secret_hash, organization, scopes)
- [ ] 127. Create APIKeyAuthentication class
- [ ] 128. Implement API key generation (secure random 64-char)
- [ ] 129. Hash API secrets with bcrypt before storing
- [ ] 130. Create API key management endpoints (create, list, revoke)
- [ ] 131. Add scopes system: ['read:campaigns', 'write:voters', etc.]
- [ ] 132. Implement scope validation in views
- [ ] 133. Create APIKeyPermission class
- [ ] 134. Track last_used_at for API keys
- [ ] 135. Implement API key expiration
- [ ] 136. Create API key rotation mechanism
- [ ] 137. Add rate limiting per API key (separate from user)
- [ ] 138. Log all API key usage in AuditLog
- [ ] 139. Create admin interface for API key management
- [ ] 140. Document API key usage in API docs

### 2.7 Email System Setup (10 items)

- [ ] 141. Configure Django email backend (SMTP/SendGrid/SES)
- [ ] 142. Set `EMAIL_BACKEND` in settings
- [ ] 143. Configure `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`
- [ ] 144. Set `DEFAULT_FROM_EMAIL` and `SERVER_EMAIL`
- [ ] 145. Create email templates: registration_verification.html
- [ ] 146. Create email templates: password_reset.html
- [ ] 147. Create email templates: welcome.html
- [ ] 148. Create email templates: password_changed.html
- [ ] 149. Set up Celery for async email sending
- [ ] 150. Create Celery tasks: send_verification_email
- [ ] 151. Create Celery tasks: send_password_reset_email
- [ ] 152. Test email delivery in development (console backend)
- [ ] 153. Test email delivery in staging (real SMTP)
- [ ] 154. Configure email rate limiting (prevent spam)
- [ ] 155. Add email bounce handling

### 2.8 Performance Optimizations (10 items)

- [ ] 156. Install django-db-connection-pool
- [ ] 157. Configure connection pooling (POOL_SIZE=10, MAX_OVERFLOW=10)
- [ ] 158. Install Redis for caching
- [ ] 159. Configure Django cache backend (Redis)
- [ ] 160. Cache JWT user lookups (1 hour TTL)
- [ ] 161. Add select_related() to all ForeignKey queries
- [ ] 162. Add prefetch_related() to all ManyToMany queries
- [ ] 163. Audit and optimize N+1 queries (django-debug-toolbar)
- [ ] 164. Add database indexes for common queries
- [ ] 165. Configure query optimization middleware

### 2.9 Security Implementations (15 items)

- [ ] 166. Implement CORS configuration (django-cors-headers)
- [ ] 167. Set CORS_ALLOWED_ORIGINS for frontend domain
- [ ] 168. Configure CSRF protection for session auth
- [ ] 169. Set SECURE_SSL_REDIRECT=True (production)
- [ ] 170. Set SECURE_HSTS_SECONDS=31536000
- [ ] 171. Set SESSION_COOKIE_SECURE=True
- [ ] 172. Set CSRF_COOKIE_SECURE=True
- [ ] 173. Implement Content Security Policy (CSP headers)
- [ ] 174. Add security headers middleware
- [ ] 175. Implement XSS protection headers
- [ ] 176. Add SQL injection protection checks
- [ ] 177. Implement input validation and sanitization
- [ ] 178. Add CAPTCHA on sensitive forms
- [ ] 179. Set up HTTPS certificate (Let's Encrypt)
- [ ] 180. Configure Django admin over HTTPS only

### 2.10 Audit Logging System (10 items)

- [ ] 181. Create AuditLog model (user, action, resource, timestamp)
- [ ] 182. Create AuditLogMiddleware to log all requests
- [ ] 183. Log authentication attempts (success/failure)
- [ ] 184. Log password changes
- [ ] 185. Log email changes
- [ ] 186. Log API key usage
- [ ] 187. Log data exports
- [ ] 188. Log permission changes
- [ ] 189. Create audit log viewer in Django admin
- [ ] 190. Add audit log search and filtering

---

## PHASE 3: CLEANUP & TESTING (Week 3)

### 3.1 Code Cleanup (15 items)

- [ ] 191. Delete `api/authentication.py` entirely
- [ ] 192. Delete `api/utils/supabase_sync.py` entirely
- [ ] 193. Delete `supabase_rls_policies.sql`
- [ ] 194. Delete old Supabase-related management commands
- [ ] 195. Remove Supabase imports from `__init__.py`
- [ ] 196. Clean up unused settings variables
- [ ] 197. Remove commented-out Supabase code
- [ ] 198. Update `INSTALLED_APPS` (add token_blacklist)
- [ ] 199. Update `MIDDLEWARE` (remove Supabase middleware)
- [ ] 200. Update `AUTHENTICATION_BACKENDS`
- [ ] 201. Remove Supabase environment variables from .env
- [ ] 202. Update .env.example with new Django-only variables
- [ ] 203. Clean up unused imports across all files
- [ ] 204. Run linters: `flake8`, `pylint`
- [ ] 205. Format code: `black`, `isort`

### 3.2 Testing - Unit Tests (20 items)

- [ ] 206. Write tests for user registration
- [ ] 207. Write tests for user login (JWT token generation)
- [ ] 208. Write tests for token refresh
- [ ] 209. Write tests for token blacklist (logout)
- [ ] 210. Write tests for email verification
- [ ] 211. Write tests for password reset request
- [ ] 212. Write tests for password reset confirm
- [ ] 213. Write tests for JWT token validation
- [ ] 214. Write tests for organization filtering
- [ ] 215. Write tests for role-based permissions
- [ ] 216. Write tests for API key authentication
- [ ] 217. Write tests for API key scope validation
- [ ] 218. Write tests for rate limiting
- [ ] 219. Write tests for pagination
- [ ] 220. Write tests for audit logging
- [ ] 221. Write tests for email sending (mock)
- [ ] 222. Write tests for password strength validation
- [ ] 223. Write tests for duplicate email prevention
- [ ] 224. Write tests for token expiration
- [ ] 225. Achieve 80%+ test coverage

### 3.3 Testing - Integration Tests (15 items)

- [ ] 226. Test full registration → verification → login flow
- [ ] 227. Test full password reset flow
- [ ] 228. Test JWT access + refresh token lifecycle
- [ ] 229. Test organization data isolation
- [ ] 230. Test role-based access control on endpoints
- [ ] 231. Test API key authentication flow
- [ ] 232. Test rate limiting enforcement
- [ ] 233. Test concurrent user requests (race conditions)
- [ ] 234. Test connection pooling under load
- [ ] 235. Test email delivery end-to-end
- [ ] 236. Test token blacklist (logout invalidation)
- [ ] 237. Test CORS configuration
- [ ] 238. Test HTTPS redirection
- [ ] 239. Test audit log creation
- [ ] 240. Test database transaction rollbacks

### 3.4 Performance Testing (10 items)

- [ ] 241. Set up Locust for load testing
- [ ] 242. Create load test scenarios (1000 concurrent users)
- [ ] 243. Test registration endpoint performance
- [ ] 244. Test login endpoint performance
- [ ] 245. Test list endpoints with pagination
- [ ] 246. Measure database query count per request
- [ ] 247. Measure cache hit rate
- [ ] 248. Test connection pool efficiency
- [ ] 249. Identify and fix bottlenecks
- [ ] 250. Document performance benchmarks

### 3.5 Security Testing (10 items)

- [ ] 251. Test SQL injection attempts
- [ ] 252. Test XSS attack vectors
- [ ] 253. Test CSRF protection
- [ ] 254. Test JWT token tampering
- [ ] 255. Test rate limiting bypass attempts
- [ ] 256. Test brute force login protection
- [ ] 257. Test password strength enforcement
- [ ] 258. Test email enumeration protection
- [ ] 259. Run OWASP ZAP security scan
- [ ] 260. Fix all identified vulnerabilities

---

## PHASE 4: FRONTEND UPDATES (Week 4)

### 4.1 Frontend Authentication (20 items)

- [ ] 261. Remove Supabase client from frontend
- [ ] 262. Remove `@supabase/supabase-js` dependency
- [ ] 263. Remove Supabase environment variables
- [ ] 264. Create `auth.service.ts` for Django API calls
- [ ] 265. Implement login() function with Django endpoint
- [ ] 266. Implement register() function
- [ ] 267. Implement logout() function (blacklist token)
- [ ] 268. Implement refreshToken() function
- [ ] 269. Implement verifyEmail() function
- [ ] 270. Implement requestPasswordReset() function
- [ ] 271. Implement confirmPasswordReset() function
- [ ] 272. Store JWT tokens in localStorage/sessionStorage
- [ ] 273. Implement token refresh interceptor (Axios/Fetch)
- [ ] 274. Handle token expiration (auto-refresh)
- [ ] 275. Handle 401 errors (redirect to login)
- [ ] 276. Update authentication state management (Redux/Context)
- [ ] 277. Update protected routes (check JWT token)
- [ ] 278. Create registration form component
- [ ] 279. Create login form component
- [ ] 280. Create password reset form component

### 4.2 API Integration Updates (15 items)

- [ ] 281. Update all API calls to use Django backend
- [ ] 282. Update base URL to Django API
- [ ] 283. Add Authorization header with JWT token
- [ ] 284. Remove Supabase RLS client queries
- [ ] 285. Update data fetching logic for all resources
- [ ] 286. Implement pagination handling
- [ ] 287. Implement filtering and search
- [ ] 288. Handle loading states
- [ ] 289. Handle error states
- [ ] 290. Implement optimistic updates
- [ ] 291. Add request caching (React Query/SWR)
- [ ] 292. Update WebSocket connections (if using real-time)
- [ ] 293. Test all CRUD operations
- [ ] 294. Test organization data isolation
- [ ] 295. Test role-based UI rendering

### 4.3 UI/UX Updates (10 items)

- [ ] 296. Design email verification success page
- [ ] 297. Design password reset success page
- [ ] 298. Add "Verify your email" banner
- [ ] 299. Add "Resend verification email" button
- [ ] 300. Update user profile page
- [ ] 301. Add 2FA setup UI (if implementing)
- [ ] 302. Add API key management UI (for admins)
- [ ] 303. Update navigation for authenticated users
- [ ] 304. Add loading skeletons for async operations
- [ ] 305. Update error messages for new auth flow

---

## PHASE 5: DEPLOYMENT & MONITORING (Ongoing)

### 5.1 Staging Deployment (10 items)

- [ ] 306. Deploy backend to staging environment
- [ ] 307. Deploy frontend to staging environment
- [ ] 308. Configure environment variables
- [ ] 309. Set up PostgreSQL database
- [ ] 310. Set up Redis instance
- [ ] 311. Set up Celery workers
- [ ] 312. Configure email service (SendGrid/SES)
- [ ] 313. Set up HTTPS certificates
- [ ] 314. Test full flow in staging
- [ ] 315. Fix any deployment issues

### 5.2 Production Deployment (10 items)

- [ ] 316. Create production deployment checklist
- [ ] 317. Backup production database
- [ ] 318. Run database migrations on production
- [ ] 319. Deploy backend to production
- [ ] 320. Deploy frontend to production
- [ ] 321. Update DNS records if needed
- [ ] 322. Configure CDN for static assets
- [ ] 323. Set up monitoring (Sentry, New Relic)
- [ ] 324. Set up logging aggregation (CloudWatch, Papertrail)
- [ ] 325. Set up uptime monitoring (Pingdom, StatusCake)

### 5.3 Monitoring & Maintenance (10 items)

- [ ] 326. Monitor error rates
- [ ] 327. Monitor API response times
- [ ] 328. Monitor database query performance
- [ ] 329. Monitor cache hit rates
- [ ] 330. Monitor email delivery rates
- [ ] 331. Set up alerts for critical errors
- [ ] 332. Set up alerts for high response times
- [ ] 333. Set up alerts for failed authentication attempts
- [ ] 334. Create runbook for common issues
- [ ] 335. Schedule regular security audits

### 5.4 Documentation (10 items)

- [ ] 336. Update API documentation
- [ ] 337. Document authentication flow for developers
- [ ] 338. Document API key generation for partners
- [ ] 339. Create user guide for password reset
- [ ] 340. Create admin guide for user management
- [ ] 341. Document deployment process
- [ ] 342. Document rollback procedure
- [ ] 343. Update README.md
- [ ] 344. Create CHANGELOG.md
- [ ] 345. Update onboarding docs for new developers

---

## FILES TO DELETE

### Backend Files to Remove:
```
backend/api/authentication.py                          # Supabase auth
backend/api/utils/supabase_sync.py                     # Supabase sync utilities
backend/supabase_rls_policies.sql                      # RLS policies
backend/api/management/commands/setup_supabase_users.py # Old user creation
backend/api/management/commands/cleanup_test_users.py  # Update to Django-only
```

### Environment Variables to Remove:
```
SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY
SUPABASE_ANON_KEY
SUPABASE_JWT_SECRET
```

### Dependencies to Remove:
```
supabase-py
```

---

## NEW FILES TO CREATE

### Backend:
```
backend/api/authentication/jwt_auth.py                 # Django JWT auth
backend/api/authentication/api_key_auth.py             # API key auth
backend/api/models/email_verification.py               # Email verification
backend/api/models/password_reset.py                   # Password reset
backend/api/models/api_key.py                          # API keys
backend/api/models/audit_log.py                        # Audit logging
backend/api/views/auth_views.py                        # Auth endpoints
backend/api/serializers/auth_serializers.py            # Auth serializers
backend/api/tasks/email_tasks.py                       # Celery email tasks
backend/api/permissions/role_permissions.py            # Role-based perms
backend/api/middleware/audit_middleware.py             # Audit logging
backend/api/middleware/rate_limit_middleware.py        # Rate limiting
```

### Tests:
```
backend/api/tests/test_auth.py
backend/api/tests/test_jwt.py
backend/api/tests/test_api_keys.py
backend/api/tests/test_permissions.py
backend/api/tests/test_email.py
backend/api/tests/test_audit_log.py
```

---

## ENVIRONMENT VARIABLES REQUIRED

### Django Authentication:
```bash
# JWT Settings
JWT_SECRET_KEY=<generate-secure-key>
JWT_ACCESS_TOKEN_LIFETIME=3600          # 1 hour
JWT_REFRESH_TOKEN_LIFETIME=604800       # 7 days
JWT_ALGORITHM=HS256

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=<sendgrid-api-key>
DEFAULT_FROM_EMAIL=noreply@pulseofpeople.com

# Redis (Caching & Celery)
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Security
SECRET_KEY=<django-secret-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com

# Database (Keep existing PostgreSQL)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=pulseofpeople
DB_USER=postgres
DB_PASSWORD=<password>
DB_HOST=localhost
DB_PORT=5432

# Connection Pooling
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=10
DB_RECYCLE=3600

# CAPTCHA (optional)
RECAPTCHA_PUBLIC_KEY=<public-key>
RECAPTCHA_PRIVATE_KEY=<private-key>
```

---

## MIGRATION TIMELINE

```
Week 1: Planning & Setup
├─ Days 1-2: Environment setup, dependency installation
├─ Days 3-4: Database schema design, documentation
└─ Day 5: Team review, finalize plan

Week 2: Core Implementation
├─ Days 1-2: Remove Supabase, implement Django JWT
├─ Days 3-4: Database migrations, email system
└─ Day 5: Third-party API keys, security

Week 3: Testing & Cleanup
├─ Days 1-2: Unit tests, integration tests
├─ Days 3-4: Performance testing, security testing
└─ Day 5: Code cleanup, linting

Week 4: Frontend & Deployment
├─ Days 1-2: Frontend authentication updates
├─ Days 3-4: Staging deployment, testing
└─ Day 5: Production deployment, monitoring setup
```

---

## ROLLBACK PLAN

If migration encounters critical issues:

1. **Immediate Rollback:**
   - Restore database from backup
   - Deploy previous version of backend
   - Deploy previous version of frontend
   - Re-enable Supabase Auth

2. **Partial Rollback:**
   - Keep database changes
   - Roll back to HybridAuthentication
   - Allow both Supabase and Django auth temporarily

3. **Data Safety:**
   - All migrations are reversible
   - Database backups before each phase
   - Feature flags for gradual rollout

---

## SUCCESS CRITERIA

- [ ] All 12 production issues resolved
- [ ] 100% user authentication through Django
- [ ] 0 Supabase dependencies remaining
- [ ] API response time <100ms (p50)
- [ ] Test coverage >80%
- [ ] Zero security vulnerabilities (OWASP scan)
- [ ] Email delivery rate >95%
- [ ] Zero downtime during migration
- [ ] All frontend features working
- [ ] Documentation complete

---

## TEAM ASSIGNMENTS

### Backend Lead:
- JWT implementation
- Database migrations
- API endpoint updates
- Security implementations

### Frontend Lead:
- Authentication service rewrite
- UI components update
- API integration
- Testing

### DevOps:
- Email service setup
- Redis/Celery configuration
- Deployment automation
- Monitoring setup

### QA:
- Test plan creation
- Manual testing
- Load testing
- Security testing

---

## NEXT STEPS

1. **Review this plan with team**
2. **Assign tasks to developers**
3. **Set up development environment**
4. **Create GitHub project board with all 345 tasks**
5. **Start Phase 1: Planning & Preparation**

---

**Status:** ✅ PLAN READY
**Estimated Effort:** 320-400 developer hours (2-3 developers × 4 weeks)
**Risk Level:** MEDIUM (well-documented migration path)
**Expected Outcome:** Clean, production-ready Django backend

---

Let's ship this! 🚀
