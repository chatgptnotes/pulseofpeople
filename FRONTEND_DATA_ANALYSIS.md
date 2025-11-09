# Frontend Data Requirements Analysis - Pulse of People

## Executive Summary
The frontend application requires data from both **Supabase** (PostgreSQL) and **Django API**, with a focus on political sentiment analysis, voter data, polling booths, and geographic hierarchies. The system supports role-based access control and multi-organization tenancy.

---

## 1. SUPABASE TABLES BEING QUERIED

### Phase 1: Core Entities (Implemented via Type Definitions)
From `/frontend/src/types/database.ts`, the following tables are defined:

#### 1.1 Authentication & User Management
**Table: `organizations`**
- Purpose: Multi-tenant organization data
- Key Fields: id, name, slug, type, subscription_status, is_active, settings, metadata
- Operations: CRUD, get by slug, filter by type/status
- Service: `organizationService`

**Table: `users`**
- Purpose: User accounts with role-based access
- Key Fields: id, email, username, full_name, role, organization_id, is_active, is_verified, preferences, failed_login_attempts, locked_until
- Roles: superadmin, admin, manager, analyst, user, viewer, volunteer
- Operations: CRUD, search, filter by role/organization, update status, manage permissions
- Service: `userService`

**Table: `user_permissions`**
- Purpose: Fine-grained permission assignments
- Key Fields: id, user_id, permission_key, granted_at, granted_by, expires_at
- Operations: Grant, revoke, check permissions via RPC function
- Service: `userService`

**Table: `audit_logs`**
- Purpose: Track all administrative actions
- Key Fields: id, organization_id, user_id, action, resource_type, resource_id, changes, ip_address, user_agent
- Read-Only: Cannot be updated
- Audit Actions: create, update, delete, view, login, logout, export, import, permission changes
- Service: Built-in Supabase table

#### 1.2 Geographic & Territory Management
**Table: `constituencies`**
- Purpose: Electoral constituency boundaries and metadata
- Key Fields: id, organization_id, name, code, type, state, district, boundaries (GeoJSON), geom (PostGIS), population, voter_count, total_booths, reserved_category, current_representative, current_party
- Types: parliament, assembly, municipal, panchayat
- Operations: Get by state/type/district, search, get stats via RPC
- Service: `constituenciesService`

**Table: `wards`**
- Purpose: Sub-constituency ward divisions
- Key Fields: id, organization_id, constituency_id, name, code, ward_number, boundaries, geom, population, voter_count, total_booths, demographics, income_level, urbanization, literacy_rate
- Operations: Get by constituency, search, demographics filtering
- Service: Not explicitly exposed (implied in geography)

**Table: `polling_booths`**
- Purpose: Actual voting locations with voter details
- Key Fields: id, organization_id, constituency_id, ward_id, booth_number, name, address, latitude, longitude, location (PostGIS), total_voters, male_voters, female_voters, transgender_voters, booth_type, is_accessible, swing_potential, priority_level, party_strength (JSON), facilities (JSON), metadata
- Booth Types: regular, auxiliary, special
- Swing Potential: high, medium, low
- Operations: Get by constituency/ward, find nearby (geospatial), filter by swing/priority, get summary stats, update priorities, map data
- Service: `pollingBoothsService`

**Table: `voters`**
- Purpose: Individual voter records with sentiment tracking
- Key Fields: 
  - Identity: voter_id_number, epic_number, aadhaar_hash, full_name, gender, age, dob
  - Contact: address, phone, email, whatsapp_number
  - Demographics: religion, caste, caste_category, occupation, education, monthly_income
  - Sentiment: sentiment (strong_support/support/neutral/oppose/strong_oppose/undecided), sentiment_score, preferred_party, previous_party_support
  - Engagement: contacted_by_party, last_contact_date, contact_method, meeting_attendance, rally_participation
  - Categorization: voter_category (core_supporter/swing_voter/opponent), tags, top_issues
  - Data Quality: verified, verified_by, verified_at, consent_given, consent_date, data_retention_until
- Operations: 
  - Search by name/voter_id/phone
  - Filter by sentiment/category/gender/age/verification
  - Get by polling booth
  - Get by tags, first-time voters, swing voters, influencers
  - Update sentiment, category, contact status
  - Bulk verify, bulk sentiment update
  - Get statistics aggregated
- Service: `votersService`

### Phase 2: Analytics & Sentiment Data (Dashboard Tables)
These tables are queried in `dashboardService.ts` but NOT defined in the type definitions:

**Table: `sentiment_data`** [MISSING FROM DATABASE TYPES]
- Purpose: Aggregated sentiment records from all sources
- Fields Used In Code: sentiment, issue, district, state, ward, timestamp
- Operations: Get by date range, aggregate by location/issue, calculate trends
- Data Sources: social_posts, field_reports, surveys
- Note: This appears to be a denormalized/aggregated view or materialized view

**Table: `social_posts`** [MISSING FROM DATABASE TYPES]
- Purpose: Social media posts with engagement metrics
- Fields Used In Code: platform, content, author_name, sentiment_polarity, likes, shares, comments, timestamp, sentiment_score
- Platforms: twitter, facebook, instagram, youtube, whatsapp, news, blog
- Operations: Get by timestamp, filter by sentiment
- Engagement Tracking: likes, shares, comments, reach
- Note: Defined in `/types/index.ts` as `SocialPost` interface

**Table: `trending_topics`** [MISSING FROM DATABASE TYPES]
- Purpose: Real-time trending keywords
- Fields Used In Code: keyword, volume, growth_rate, sentiment_score, platforms
- Operations: Get trending topics
- Note: Defined in `/types/index.ts` as `TrendingTopic` interface

**Table: `alerts`** [MISSING FROM DATABASE TYPES]
- Purpose: Sentiment alerts and crisis detection
- Fields Used In Code: severity, status (active/acknowledged/resolved), timestamp, ward, district
- Severity Levels: low, medium, high, critical
- Operations: Get critical/high alerts, filter by status
- Note: Defined in `/types/index.ts` as `AlertData` interface

**Table: `field_reports`** [MISSING FROM DATABASE TYPES]
- Purpose: Ground-level volunteer reports
- Fields Used In Code: timestamp, location
- Operations: Count recent field reports, filter by timestamp
- Note: Defined in `/types/index.ts` as `FieldReport` interface

**Table: `demo_requests`** [CUSTOM TABLE]
- Purpose: Demo access tracking
- Operations: CRUD operations on demo requests
- Service: `demoService`

---

## 2. DJANGO API ENDPOINTS BEING CALLED

All Django endpoints defined in `/frontend/src/services/djangoApi.ts`:

### Authentication Endpoints
```
POST /api/auth/signup/          - Register new user
POST /api/auth/login/           - Login (email or username)
GET  /api/auth/profile/         - Get current user profile
POST /api/auth/refresh/         - Refresh access token
POST /api/auth/logout/          - Logout (blacklist token)
GET  /api/auth/users/           - Get list of users (paginated)
```

### Master Data Endpoints (Public, No Auth)
```
GET  /api/states/               - Get all states
GET  /api/districts/?state={code}  - Get districts by state
GET  /api/constituencies/       - Get constituencies (with optional filters)
GET  /api/polling-booths/       - Get polling booths (with optional filters)
GET  /api/issue-categories/     - Get 9 priority issue categories
GET  /api/issues/               - Alias for issue-categories
GET  /api/voter-segments/       - Get voter segmentation data
GET  /api/political-parties/    - Get political party list
```

### Citizen Feedback Endpoints
```
POST /api/feedback/             - Submit citizen feedback (PUBLIC)
GET  /api/feedback/             - Get feedback list (AUTH REQUIRED, filtered by role)
GET  /api/feedback/{id}/        - Get feedback details
POST /api/feedback/{id}/mark_reviewed/  - Mark feedback as reviewed
POST /api/feedback/{id}/escalate/       - Escalate feedback
GET  /api/feedback/stats/       - Get feedback statistics
```

### Field Reports Endpoints
```
POST /api/field-reports/        - Submit field report (AUTH REQUIRED)
GET  /api/field-reports/        - Get all field reports
GET  /api/field-reports/my_reports/  - Get user's own reports
POST /api/field-reports/{id}/verify/ - Verify report (Admin only)
```

### Analytics Endpoints
```
GET  /api/analytics/overview/   - Dashboard overview analytics
GET  /api/analytics/constituency/{code}/  - Constituency-level analytics
GET  /api/analytics/district/{id}/        - District-level analytics
GET  /api/analytics/state/{code}/         - State-level analytics
```

### Bulk Upload Endpoints
```
POST /api/users/bulk-upload/    - Upload CSV for bulk user creation
GET  /api/users/bulk-upload/{jobId}/status/  - Get upload job status
GET  /api/users/bulk-upload/{jobId}/errors/  - Download error report
DELETE /api/users/bulk-upload/{jobId}/       - Cancel upload job
GET  /api/users/bulk-upload/template/        - Download CSV template
GET  /api/users/bulk-upload/jobs/            - Get list of bulk jobs
```

### Utility Endpoints
```
GET  /api/health/               - Health check
```

---

## 3. DATA STRUCTURES & INTERFACES

### Core User Interfaces
```typescript
interface User {
  id: string;
  organization_id: string;
  email: string;
  username: string;
  full_name: string;
  phone: string | null;
  avatar_url: string | null;
  role: UserRole;  // superadmin, admin, manager, analyst, user, viewer, volunteer
  is_active: boolean;
  is_verified: boolean;
  email_verified_at: string | null;
  last_login: string | null;
  preferences: Json;
  failed_login_attempts: number;
  locked_until: string | null;
  password_changed_at: string | null;
  created_at: string;
  updated_at: string;
  created_by: string | null;
}
```

### Sentiment Analysis Interfaces
```typescript
interface SentimentData {
  issue: string;
  sentiment: number;  // 0-1
  polarity: 'positive' | 'negative' | 'neutral';
  intensity: number;
  emotion?: 'anger' | 'trust' | 'fear' | 'hope' | 'pride' | 'joy' | 'sadness' | 'surprise' | 'disgust';
  confidence: number;
  language: 'en' | 'hi' | 'bn' | 'mr' | 'ta' | 'te' | 'gu' | 'kn' | 'ml' | 'or' | 'pa';
  source: 'social_media' | 'survey' | 'field_report' | 'news' | 'direct_feedback';
  timestamp: Date;
  location: {
    state: string;
    district?: string;
    ward?: string;
    coordinates?: [number, number];
  };
  demographic?: {
    age_group?: string;
    gender?: 'male' | 'female' | 'other';
    education?: string;
    income?: string;
  };
}
```

### Voter Interfaces
```typescript
interface Voter {
  id: string;
  organization_id: string;
  polling_booth_id: string | null;
  voter_id_number: string;
  epic_number: string | null;
  aadhaar_number_hash: string | null;
  full_name: string;
  gender: VoterGender;
  age: number | null;
  date_of_birth: string | null;
  sentiment: VoterSentiment;
  sentiment_score: number | null;
  preferred_party: string | null;
  voter_category: VoterCategory;  // core_supporter, swing_voter, opponent
  tags: string[] | null;
  verified: boolean;
  consent_given: boolean;
  // ... and 40+ other fields
}
```

### Geographic Hierarchy
```typescript
interface Constituency {
  id: string;
  name: string;
  code: string;
  type: ConstituencyType;  // parliament, assembly, municipal, panchayat
  state: string;
  district: string;
  population: number;
  voter_count: number;
  total_booths: number;
}

interface PollingBooth {
  id: string;
  booth_number: string;
  name: string;
  latitude: number;
  longitude: number;
  total_voters: number;
  swing_potential: SwingPotential;  // high, medium, low
  priority_level: number;
  // ... 25+ other fields
}
```

---

## 4. MOCK DATA vs REAL DATA

### Currently Using Mock Data:
- `sentiment_data` - Mock data in `/data/mockData.ts`
- Competitor analysis
- Heatmap data by ward
- Influencer data
- Trend data
- Alert data
- Sentiment distribution

### Actually Querying from Database:
- `sentiment_data` - Dashboard service queries real table
- `social_posts` - Real posts with engagement metrics
- `field_reports` - Real volunteer reports
- `alerts` - Real active alerts
- `trending_topics` - Real trending keywords

### Control Flag:
`api.ts` has `USE_MOCK_DATA = false` - This means real data is expected from API

---

## 5. GAP ANALYSIS: What's Being Queried but Might Not Exist

### CRITICAL GAPS:

1. **sentiment_data Table** - Dashboard heavily depends on this but it's not in the type definitions
   - Status: Needed for dashboards to work
   - Location: Should be created in Supabase migrations
   - Fields: sentiment, issue, district, state, ward, timestamp (minimum)

2. **social_posts Table** - Queries expect this table
   - Status: Defined in types but no migration file confirmed
   - Queries: By timestamp, sentiment filtering, engagement aggregation
   - Fields: platform, content, author_name, sentiment_polarity, engagement metrics

3. **trending_topics Table** - Dashboard queries for trending data
   - Status: Not in database types
   - Expected Fields: keyword, volume, growth_rate, sentiment_score, platforms

4. **alerts Table** - Real-time alert system
   - Status: Not in database types, partially defined
   - Expected Fields: severity, status, timestamp, ward, district, type

5. **field_reports Table** - Volunteer reports
   - Status: Partially defined, dashboard queries for counts
   - Expected Fields: timestamp, location, ward, district

### MISSING PERMISSION ENUMS:
The permission system expects these categories:
- `users.view`, `users.create`, `users.update`, `users.delete`, `users.manage`, `users.export`
- `voters.view`, `voters.create`, `voters.update`, `voters.delete`, `voters.manage`, `voters.export`
- `booths.view`, `booths.create`, `booths.update`, `booths.delete`, `booths.manage`, `booths.export`
- `social.view`, `social.create`, `social.update`, `social.delete`
- `media.view`, `media.manage`
- `analytics.view`, `analytics.export`
- `reports.view`, `reports.create`, `reports.export`
- `campaigns.view`, `campaigns.create`, `campaigns.update`, `campaigns.delete`, `campaigns.manage`
- `field_workers.view`, `field_workers.manage`
- `alerts.view`, `alerts.manage`

---

## 6. REAL-TIME FEATURES

### Subscriptions Set Up:
```typescript
// Tables with real-time subscriptions available:
- subscribeToTable(tableName, callback)
- subscribeToRecord(tableName, recordId, callback)
```

### Expected Real-Time Events:
- User permission changes
- Alert status changes
- Voter sentiment updates
- Field report submissions
- Audit log entries

---

## 7. AUTHENTICATION FLOW

### Supabase Auth:
- JWT tokens from Supabase
- Session persistence in localStorage
- Auto-refresh token support
- Role-based access control (RBAC) stored in database

### Django Auth:
- Separate JWT token system
- Access + Refresh tokens
- Email or username login
- User profile endpoint

### Current Implementation:
Dual authentication - Supabase for main app, Django as fallback for bulk operations

---

## 8. CONTEXT DATA STRUCTURES

From `/contexts/AuthContext.tsx`:
```typescript
interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  avatar?: string;
  permissions: string[];
  ward?: string;
  constituency?: string;
  is_super_admin?: boolean;
  organization_id?: string;
  tenant_id?: string;
  status?: 'active' | 'inactive' | 'suspended';
}
```

---

## 9. STORAGE & FILE UPLOADS

### Supabase Storage Buckets:
- Used for: Profile avatars, organization logos, media attachments
- Methods: uploadFile(), deleteFile(), getPublicUrl()
- Buckets: (to be configured based on app usage)

---

## 10. DATABASE FUNCTIONS (RPC)

### Implemented:
```sql
get_user_permissions(p_user_id)          - Returns array of permissions
has_permission(p_user_id, p_permission)  - Boolean permission check
find_booths_near(p_latitude, p_longitude, p_radius_meters)  - Geospatial query
get_constituency_stats(p_constituency_id) - Aggregated constituency stats
```

### Missing:
- Sentiment aggregation functions
- Social post analytics functions
- Voter analysis functions
- Alert generation functions

---

## SUMMARY TABLE

| Component | Type | Status | Service | Critical |
|-----------|------|--------|---------|----------|
| organizations | Table | Implemented | organizationService | Yes |
| users | Table | Implemented | userService | Yes |
| user_permissions | Table | Implemented | userService | Yes |
| constituencies | Table | Implemented | constituenciesService | Yes |
| polling_booths | Table | Implemented | pollingBoothsService | Yes |
| voters | Table | Implemented | votersService | Yes |
| sentiment_data | Table | MISSING | dashboardService | Yes |
| social_posts | Table | Partial | dashboardService | Yes |
| trending_topics | Table | MISSING | dashboardService | Yes |
| alerts | Table | Partial | dashboardService | Yes |
| field_reports | Table | Partial | dashboardService | Yes |
| Django Auth | API | Implemented | djangoApi | Yes |
| Django Master Data | API | Implemented | djangoApi | Yes |
| Django Feedback | API | Implemented | djangoApi | Yes |
| Django Analytics | API | Implemented | djangoApi | Yes |

---

## RECOMMENDATIONS

1. **Create Missing Tables**: Implement sentiment_data, ensure social_posts, trending_topics, alerts, field_reports are properly defined
2. **Database Functions**: Add RPC functions for sentiment aggregation
3. **Indexes**: Ensure proper PostGIS and timestamp indexes for performance
4. **Migrations**: Run all migrations in `/frontend/supabase/migrations/` in sequence
5. **Seed Data**: Load initial data for master tables (states, districts, constituencies)
6. **Test Queries**: Verify all dashboardService queries return expected data
7. **Permission Setup**: Initialize permission hierarchy in user_permissions table

