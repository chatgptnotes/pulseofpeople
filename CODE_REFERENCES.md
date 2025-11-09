# Code References & File Locations - Data Requirements

## Frontend Services Using Data

### 1. Core Supabase Service
**File**: `/frontend/src/services/supabase/index.ts`
- Supabase client initialization
- Auth helpers (signIn, signOut, isAuthenticated)
- Real-time subscription setup
- Storage file operations
- RPC function calls

**Tables Referenced**:
- organizations, users, user_permissions, audit_logs

---

### 2. User Service
**File**: `/frontend/src/services/supabase/users.service.ts` (308 lines)

**Methods**:
- `getUsersByRole(role)` - Get users by single or multiple roles
- `getUsersByOrganization(organizationId)` - Filter by organization
- `getUserWithOrganization(userId)` - Join with organization details
- `getUserWithPermissions(userId)` - Include permissions array
- `searchUsers(query, organizationId?)` - Full-text search
- `getFilteredUsers(filters)` - Advanced filtering
- `createUser(userData)` - Create new user with defaults
- `updateUserProfile(userId, updates)` - Update profile fields
- `deactivateUser(userId)` - Set is_active = false
- `activateUser(userId)` - Set is_active = true
- `verifyEmail(userId)` - Mark email as verified
- `updateRole(userId, newRole)` - Change user role
- `recordLogin(userId, success)` - Track login attempts/lockout
- `isAccountLocked(userId)` - Check account lock status
- `unlockAccount(userId)` - Reset lock and failed attempts
- `getUserPermissions(userId)` - Get all permissions via RPC
- `hasPermission(userId, permission)` - Single permission check via RPC
- `grantPermission(userId, permission, grantedBy)` - Add permission
- `revokePermission(userId, permission)` - Remove permission
- `getUserStats(organizationId)` - Count users by role

---

### 3. Voter Service
**File**: `/frontend/src/services/supabase/voters.service.ts` (350 lines)

**Methods**:
- `getByBooth(boothId, filters?)` - Get voters in polling booth
- `getBySentiment(sentiment)` - Filter by voter sentiment
- `getByCategory(category)` - Filter by voter category
- `getWithBooth(voterId)` - Join with booth details
- `searchVoters(searchTerm)` - Search by name/id/phone/epic
- `getByAgeRange(minAge, maxAge)` - Age filtering with ordering
- `getVerified(filters?)` - Only verified voters
- `getByTags(tags)` - Array overlaps on tags
- `getFirstTimeVoters(boothId?)` - New voter identification
- `getSwingVoters(boothId?)` - Undecided voters with high influence score
- `getInfluencers(minScore)` - High influence score voters (default 70+)
- `updateSentiment(voterId, sentiment, score)` - Update voter sentiment
- `updateCategory(voterId, category)` - Change voter category
- `markAsContacted(voterId, method, notes?)` - Track outreach
- `addTags(voterId, newTags)` - Add voter tags
- `removeTags(voterId, tagsToRemove)` - Remove voter tags
- `getStatistics(organizationId, boothId?)` - Aggregated stats (gender, sentiment, age, influencer score)
- `bulkUpdateSentiment(voterIds, sentiment, score)` - Batch update
- `bulkVerify(voterIds, verifiedBy)` - Batch verification
- `getFiltered(filters)` - Apply all filter types

**Voter Sentiment Values**:
- strong_support, support, neutral, oppose, strong_oppose, undecided

**Voter Categories**:
- core_supporter, swing_voter, opponent

---

### 4. Polling Booths Service
**File**: `/frontend/src/services/supabase/polling-booths.service.ts` (300 lines)

**Methods**:
- `getByConstituency(constituencyId)` - Get booths in constituency (sorted by booth_number)
- `getByWard(wardId)` - Get booths in ward
- `getActive(filters?)` - Only active booths
- `getHighPriority(constituencyId?, minPriority)` - Filter by priority >= minPriority
- `getWithConstituency(boothId)` - Join with constituency
- `findNearby(lat, lng, radiusMeters)` - Geospatial query using find_booths_near() RPC
- `getBySwingPotential(potential)` - Filter by swing_potential (high/medium/low)
- `getByType(type)` - Filter by booth_type (regular/auxiliary/special)
- `searchBooths(searchTerm)` - Search by name, booth_number, address
- `getConstituencySummary(constituencyId)` - Aggregated stats (total/active/voters, type distribution, swing distribution, avg priority)
- `setPriority(boothId, priorityLevel)` - Update single booth priority
- `setSwingPotential(boothId, potential)` - Update single booth swing assessment
- `bulkSetPriority(boothIds, priorityLevel)` - Batch priority update
- `getMapData(constituencyId?)` - Get booth locations for Mapbox (lat/lng + metadata)

**Booth Types**: regular, auxiliary, special

**Swing Potential**: high, medium, low

---

### 5. Constituencies Service
**File**: `/frontend/src/services/supabase/constituencies.service.ts` (206 lines)

**Methods**:
- `getByType(type)` - Filter by parliament/assembly/municipal/panchayat
- `getByState(state)` - Get all in state
- `getByDistrict(state, district)` - Two-level filter
- `getWithStats(constituencyId)` - Join with get_constituency_stats() RPC
- `getAllWithStats(filters?)` - Get all with stats in parallel
- `searchConstituencies(searchTerm)` - Search by name or code
- `getOrganizationSummary(organizationId)` - Aggregated org-wide stats (total constituencies, population, voters, booths, type/state distribution)
- `refreshStats(constituencyId)` - Manually trigger update_constituency_voter_count() RPC
- `getFiltered(filters)` - Apply ConstituencyFilters

**Constituency Types**: parliament, assembly, municipal, panchayat

---

### 6. Organizations Service
**File**: `/frontend/src/services/supabase/organizations.service.ts` (211 lines)

**Methods**:
- `getBySlug(slug)` - Get org by slug identifier
- `getByType(type)` - Filter by org type (political_party, campaign, ngo, advocacy_group)
- `getActiveOrganizations()` - Only is_active = true
- `getBySubscriptionStatus(status)` - Filter by subscription (trial/active/suspended/cancelled)
- `createOrganization(orgData)` - Auto-generate slug from name
- `updateSettings(organizationId, settings)` - Merge settings JSON
- `activate(organizationId)` - Set is_active = true
- `deactivate(organizationId)` - Set is_active = false
- `updateSubscription(organizationId, status, startDate?, endDate?)` - Manage subscription lifecycle
- `isSubscriptionActive(organizationId)` - Boolean subscription check with date validation
- `getExpiringSubscriptions(withinDays)` - Find expiring subscriptions
- `getStats(organizationId)` - Total/active users, subscription status, days until expiry

**Subscription Statuses**: trial, active, suspended, cancelled

---

### 7. Dashboard Service
**File**: `/frontend/src/services/dashboardService.ts` (500+ lines)

**CRITICAL: This service queries tables NOT in type definitions!**

**Functions**:
- `getDashboardMetrics()` - Queries sentiment_data, social_posts, field_reports, alerts (last 24h)
- `getLocationSentiment()` - Queries sentiment_data by district/state (last 7 days)
- `getIssueSentiment()` - Queries sentiment_data aggregated by issue
- `getTrendingTopics()` - Queries trending_topics table
- `getActiveAlerts()` - Queries alerts with severity >= medium
- `getSocialPostsActivity()` - Queries social_posts with engagement metrics
- `getSentimentByDemographic()` - Queries sentiment_data aggregated by demographics
- `getLocationHeatmap()` - Queries sentiment_data by location grid

**Tables Queried**:
1. sentiment_data - Core dashboard data (MISSING FROM TYPES)
2. social_posts - Social engagement tracking (MISSING FROM TYPES)
3. field_reports - Volunteer reports count
4. alerts - Crisis detection (MISSING FROM TYPES)
5. trending_topics - Real-time keywords (MISSING FROM TYPES)

---

### 8. Django API Service
**File**: `/frontend/src/services/djangoApi.ts` (657 lines)

**Configuration**:
- Base URL: `VITE_DJANGO_API_URL` or default `http://127.0.0.1:8000/api`
- Headers: Supabase JWT token in Authorization bearer

**API Groups**:

#### Authentication
- `register(email, password, name, role?)`
- `login(emailOrUsername, password)`
- `getUserProfile()`
- `refreshToken(refreshToken)`
- `logout(refreshToken)`
- `getUsers()` - Paginated

#### Master Data (Public)
- `getStates()`
- `getDistricts(stateCode?)`
- `getConstituencies(stateCode?, type?)`
- `getPollingBooths(constituencyName?, districtName?, stateCode?)`
- `getIssueCategories()` - Returns 9 TVK priorities
- `getIssues()` - Alias for above
- `getVoterSegments()` - Voter demographic segments
- `getPoliticalParties()` - Political party registry

#### Citizen Feedback (Public submission)
- `submitFeedback(feedbackData)` - PUBLIC endpoint (no auth required)
- `getFeedbackList(filters?)` - AUTH required (role-filtered)
- `getFeedbackDetail(id)` - AUTH required
- `markFeedbackReviewed(id)` - AUTH required
- `escalateFeedback(id)` - AUTH required
- `getFeedbackStats()` - AUTH required

#### Field Reports (Auth required)
- `submitFieldReport(reportData)` - Create field report
- `getFieldReports(myReportsOnly?)` - List reports
- `verifyFieldReport(id, notes?)` - Admin only

#### Analytics (Auth required)
- `getAnalyticsOverview()` - Dashboard metrics
- `getConstituencyAnalytics(constituencyCode)`
- `getDistrictAnalytics(districtId)`
- `getStateAnalytics(stateCode)`

#### Bulk Upload (Auth required)
- `uploadBulkUsers(file)` - POST CSV for bulk creation
- `getBulkUploadStatus(jobId)` - Track job progress
- `downloadBulkErrors(jobId)` - Get CSV error report
- `cancelBulkUpload(jobId)` - Cancel job
- `downloadUserTemplate()` - Get CSV template
- `getBulkUploadJobs()` - List all jobs

#### Utility
- `isAuthenticated()` - Check auth status
- `healthCheck()` - API availability check

---

### 9. Demo Service
**File**: `/frontend/src/services/demoService.ts` (130 lines)

**Methods**:
- `submitDemoRequest(email)` - Create demo_requests record
- `getDemoRequests(options?)` - List with pagination
- `getDemoRequest(id)` - Get by ID
- `updateDemoRequest(id, updates)` - Update status
- `approveDemoRequest(id)` - Change status to approved
- `rejectDemoRequest(id)` - Change status to rejected

---

## Type Definitions

### Main Types
**File**: `/frontend/src/types/index.ts`
- SentimentData, TrendData, CompetitorData, HeatmapData, InfluencerData, AlertData
- MediaSource, SocialPost, TrendingTopic
- Survey, SurveyQuestion, SurveyResponse
- Recommendation, Volunteer, FieldReport

### Database Types (Supabase Schema)
**File**: `/frontend/src/types/database.ts` (730 lines)
- Defines all 8+ tables with full type safety
- Includes Insert/Update/Filter types
- Database interface with Functions
- Permission enums and categories

---

## Context Providers

### AuthContext
**File**: `/frontend/src/contexts/AuthContext.tsx`
- User authentication state
- Permission checking
- Login/logout/signup
- Session management

### Other Contexts
- FeatureFlagContext - Feature flags
- PermissionContext - RBAC enforcement
- TenantContext - Multi-tenancy
- RealTimeContext - Real-time subscriptions
- OnboardingContext - Onboarding flow

---

## Database Migrations

**Location**: `/frontend/supabase/migrations/`

**Files** (in order):
1. `20251027_create_all_tables.sql` - Main schema (20 tables)
2. `20251027_create_tenant_registry.sql` - Multi-tenancy
3. `20251028_add_rbac_system.sql` - Role-based access
4. `20251029_optimize_indexes.sql` - Performance indexes
5. `20251029_single_db_multi_tenant.sql` - Single-DB mode
6. `20251106_create_constituency_master.sql` - Electoral boundaries
7. `20251107_create_states_table.sql` - State master data
8. `20251107_create_districts_table.sql` - District master data
9. `20251108_create_issue_categories.sql` - TVK 9 priorities
10. `20251108_create_political_parties.sql` - Political party registry
11. `20251108_create_voter_segments.sql` - Voter demographics
12. `20251109_competitor_tracking.sql` - Competitor analysis
13. `20251109_tv_broadcast_schema.sql` - Media tracking

---

## CRUD Service Base Class

**File**: `/frontend/src/services/supabase/crud.ts` (200+ lines)

**Generic Class**: `SupabaseService<T, TInsert, TUpdate>`

**Core Methods**:
- `getAll(options)` - Pagination, filtering, sorting
- `getById(id)` - Single record
- `getOne(filters)` - Single record by filter
- `create(payload)` - Insert record
- `bulkCreate(items)` - Batch insert
- `update(id, updates)` - Update record
- `bulkUpdate(items)` - Batch update
- `delete(id)` - Delete record
- `bulkDelete(ids)` - Batch delete
- `search(columns, query, options)` - Full-text search
- `count()` - Record count
- `applyFilters(query, filters)` - Filter application

---

## Key Files Summary

| File | Type | Purpose | Size |
|------|------|---------|------|
| types/database.ts | Types | Database schema definition | 730 lines |
| types/index.ts | Types | Domain models | ~200 lines |
| services/supabase/index.ts | Service | Supabase client init | ~260 lines |
| services/supabase/crud.ts | Service | Generic CRUD base | ~200 lines |
| services/supabase/users.service.ts | Service | User operations | 308 lines |
| services/supabase/voters.service.ts | Service | Voter operations | 350 lines |
| services/supabase/polling-booths.service.ts | Service | Booth operations | 300 lines |
| services/supabase/constituencies.service.ts | Service | Constituency ops | 206 lines |
| services/supabase/organizations.service.ts | Service | Org operations | 211 lines |
| services/dashboardService.ts | Service | Analytics queries | 500+ lines |
| services/djangoApi.ts | Service | Django integration | 657 lines |
| services/demoService.ts | Service | Demo requests | 130 lines |
| contexts/AuthContext.tsx | Context | Auth state | ~200 lines |
| supabase/migrations/ | SQL | Database schema | 13 files |

