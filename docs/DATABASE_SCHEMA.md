# Database Schema Documentation

## Table of Contents
1. [Overview](#overview)
2. [Entity Relationship Diagram](#entity-relationship-diagram)
3. [Core Tables](#core-tables)
4. [Master Data Tables](#master-data-tables)
5. [Operational Tables](#operational-tables)
6. [System Tables](#system-tables)
7. [Relationships](#relationships)
8. [Indexes](#indexes)
9. [Constraints](#constraints)
10. [Data Types](#data-types)

---

## Overview

The Pulse of People platform uses a **PostgreSQL** database (with **SQLite** for development). The schema supports:

- Multi-tenancy via Organizations
- Role-Based Access Control (RBAC) with 7 roles
- Electoral data (States, Districts, Constituencies, Wards, Booths)
- Citizen feedback and field reports
- Sentiment analysis and analytics
- Audit logging

**Database Engine:** PostgreSQL 13+ (Production), SQLite 3+ (Development)

**Total Tables:** 24

**Key Extensions:**
- PostGIS (for geographic data - optional)
- UUID (for unique identifiers)

---

## Entity Relationship Diagram

```
Organizations
    ├── UserProfiles (members)
    ├── Wards
    └── Polling Booths

States
    ├── Districts
    ├── Constituencies
    └── Polling Booths

Constituencies
    ├── Wards (if applicable)
    └── Polling Booths

Users
    ├── UserProfile (1-to-1)
    ├── Permissions (many-to-many)
    ├── AuditLogs
    ├── Notifications
    ├── Tasks
    └── UploadedFiles

Feedback
    ├── Citizen Info
    ├── Issue Category (foreign key)
    └── Voter Segment (foreign key)

Field Reports
    ├── Volunteer (foreign key to User)
    └── Verification Info
```

---

## Core Tables

### 1. Organization

**Purpose:** Multi-tenant organization management

**Table:** `api_organization`

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| `id` | INTEGER/SERIAL | No | Auto | Primary key |
| `name` | VARCHAR(200) | No | | Organization name |
| `slug` | VARCHAR(50) | No | | URL-safe unique identifier |
| `subscription_status` | VARCHAR(20) | No | 'active' | Subscription status |
| `subscription_tier` | VARCHAR(20) | No | 'basic' | Tier: basic/pro/enterprise |
| `max_users` | INTEGER | No | 10 | Maximum user count |
| `settings` | JSONB | Yes | {} | Organization settings |
| `created_at` | TIMESTAMP | No | NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP | No | NOW() | Last update timestamp |

**Indexes:**
- PRIMARY KEY (`id`)
- UNIQUE (`slug`)
- INDEX (`name`)

**Relationships:**
- Has many `UserProfile` (members)
- Has many `Ward`
- Has many `PollingBooth`

---

### 2. User (Django Auth)

**Purpose:** User authentication and basic info

**Table:** `auth_user` (Django built-in)

| Column | Type | Null | Description |
|--------|------|------|-------------|
| `id` | INTEGER | No | Primary key |
| `username` | VARCHAR(150) | No | Unique username |
| `email` | VARCHAR(254) | No | Email address |
| `first_name` | VARCHAR(150) | Yes | First name |
| `last_name` | VARCHAR(150) | Yes | Last name |
| `password` | VARCHAR(128) | No | Hashed password |
| `is_staff` | BOOLEAN | No | Django admin access |
| `is_active` | BOOLEAN | No | Account active status |
| `is_superuser` | BOOLEAN | No | Django superuser |
| `date_joined` | TIMESTAMP | No | Registration date |
| `last_login` | TIMESTAMP | Yes | Last login time |

**Indexes:**
- PRIMARY KEY (`id`)
- UNIQUE (`username`)
- UNIQUE (`email`)

---

### 3. UserProfile

**Purpose:** Extended user information and role management

**Table:** `api_userprofile`

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| `id` | INTEGER | No | Auto | Primary key |
| `user_id` | INTEGER | No | | Foreign key to auth_user |
| `role` | VARCHAR(20) | No | 'user' | User role |
| `organization_id` | INTEGER | Yes | | Foreign key to organization |
| `bio` | TEXT | Yes | | User biography |
| `avatar` | VARCHAR(100) | Yes | | Avatar file path |
| `avatar_url` | VARCHAR(200) | Yes | | Avatar URL (Supabase) |
| `phone` | VARCHAR(20) | Yes | | Phone number |
| `date_of_birth` | DATE | Yes | | Date of birth |
| `must_change_password` | BOOLEAN | No | False | Force password change |
| `assigned_state_id` | INTEGER | Yes | | For Admin1 (state level) |
| `assigned_district_id` | INTEGER | Yes | | For Admin2 (district level) |
| `city` | VARCHAR(100) | Yes | | User city |
| `constituency` | VARCHAR(200) | Yes | | User constituency |
| `created_at` | TIMESTAMP | No | NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP | No | NOW() | Last update |

**Role Choices:**
- `superadmin` - Super Admin (Platform owner)
- `admin` - Admin (Organization owner)
- `manager` - Manager
- `analyst` - Analyst
- `user` - Standard User
- `viewer` - Read-only Viewer
- `volunteer` - Volunteer (field worker)

**Indexes:**
- PRIMARY KEY (`id`)
- UNIQUE (`user_id`)
- INDEX (`role`)
- INDEX (`organization_id`)
- INDEX (`assigned_state_id`)
- INDEX (`assigned_district_id`)

---

### 4. Permission

**Purpose:** Granular permissions for RBAC

**Table:** `api_permission`

| Column | Type | Null | Description |
|--------|------|------|-------------|
| `id` | INTEGER | No | Primary key |
| `name` | VARCHAR(100) | No | Unique permission name |
| `category` | VARCHAR(50) | No | Permission category |
| `description` | TEXT | No | Permission description |
| `created_at` | TIMESTAMP | No | Creation timestamp |

**Categories:**
- `users` - User Management
- `data` - Data Access
- `analytics` - Analytics
- `settings` - Settings
- `system` - System

**Indexes:**
- PRIMARY KEY (`id`)
- UNIQUE (`name`)
- INDEX (`category`)

**Example Permissions:**
- `view_analytics`
- `manage_users`
- `upload_data`
- `export_data`
- `manage_settings`

---

### 5. RolePermission

**Purpose:** Map roles to default permissions

**Table:** `api_rolepermission`

| Column | Type | Null | Description |
|--------|------|------|-------------|
| `id` | INTEGER | No | Primary key |
| `role` | VARCHAR(20) | No | User role |
| `permission_id` | INTEGER | No | Foreign key to permission |

**Constraints:**
- UNIQUE (`role`, `permission_id`)

---

### 6. UserPermission

**Purpose:** User-specific permission overrides

**Table:** `api_userpermission`

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| `id` | INTEGER | No | Auto | Primary key |
| `user_profile_id` | INTEGER | No | | Foreign key to user_profile |
| `permission_id` | INTEGER | No | | Foreign key to permission |
| `granted` | BOOLEAN | No | True | Permission granted/revoked |
| `created_at` | TIMESTAMP | No | NOW() | Timestamp |

**Constraints:**
- UNIQUE (`user_profile_id`, `permission_id`)

---

## Master Data Tables

### 7. State

**Purpose:** Indian states/union territories

**Table:** `api_state`

| Column | Type | Null | Description |
|--------|------|------|-------------|
| `id` | INTEGER | No | Primary key |
| `name` | VARCHAR(100) | No | State name |
| `code` | VARCHAR(10) | No | 2-letter code (TN, PY) |
| `capital` | VARCHAR(100) | Yes | Capital city |
| `region` | VARCHAR(50) | Yes | Geographic region |
| `total_districts` | INTEGER | No | Number of districts |
| `total_constituencies` | INTEGER | No | Number of constituencies |
| `created_at` | TIMESTAMP | No | Creation timestamp |
| `updated_at` | TIMESTAMP | No | Last update |

**Indexes:**
- PRIMARY KEY (`id`)
- UNIQUE (`code`)
- INDEX (`name`)

**Example Data:**
- Tamil Nadu (TN)
- Puducherry (PY)

---

### 8. District

**Purpose:** Electoral districts

**Table:** `api_district`

| Column | Type | Null | Description |
|--------|------|------|-------------|
| `id` | INTEGER | No | Primary key |
| `state_id` | INTEGER | No | Foreign key to state |
| `name` | VARCHAR(100) | No | District name |
| `code` | VARCHAR(20) | No | District code |
| `headquarters` | VARCHAR(100) | Yes | District HQ |
| `population` | INTEGER | Yes | Total population |
| `area_sq_km` | DECIMAL(10,2) | Yes | Area in sq km |
| `created_at` | TIMESTAMP | No | Creation timestamp |
| `updated_at` | TIMESTAMP | No | Last update |

**Indexes:**
- PRIMARY KEY (`id`)
- UNIQUE (`state_id`, `code`)
- INDEX (`state_id`)
- INDEX (`name`)

---

### 9. Constituency

**Purpose:** Electoral constituencies (assembly/parliamentary)

**Table:** `api_constituency`

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| `id` | INTEGER | No | Auto | Primary key |
| `state_id` | INTEGER | No | | Foreign key to state |
| `district_id` | INTEGER | Yes | | Foreign key to district |
| `name` | VARCHAR(200) | No | | Constituency name |
| `code` | VARCHAR(20) | No | | Unique code (e.g., TN-AC-001) |
| `constituency_type` | VARCHAR(20) | No | 'assembly' | Type: assembly/parliamentary |
| `number` | INTEGER | No | | Constituency number |
| `reserved_for` | VARCHAR(20) | No | 'general' | Reservation: general/sc/st |
| `total_voters` | INTEGER | Yes | | Total registered voters |
| `total_wards` | INTEGER | No | 0 | Number of wards |
| `total_booths` | INTEGER | No | 0 | Number of booths |
| `area_sq_km` | DECIMAL(10,2) | Yes | | Area in sq km |
| `center_lat` | DECIMAL(10,8) | Yes | | Center latitude |
| `center_lng` | DECIMAL(11,8) | Yes | | Center longitude |
| `geojson_data` | JSONB | Yes | | GeoJSON boundaries |
| `metadata` | JSONB | No | {} | Additional metadata |
| `created_at` | TIMESTAMP | No | NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP | No | NOW() | Last update |

**Indexes:**
- PRIMARY KEY (`id`)
- UNIQUE (`code`)
- UNIQUE (`state_id`, `code`)
- INDEX (`state_id`, `constituency_type`)
- INDEX (`district_id`)

---

### 10. Ward (New - Phase 2)

**Purpose:** Wards within constituencies

**Table:** `api_ward`

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| `id` | UUID | No | Auto | Primary key |
| `organization_id` | INTEGER | No | | Foreign key to organization |
| `constituency_id` | INTEGER | No | | Foreign key to constituency |
| `name` | VARCHAR(255) | No | | Ward name |
| `code` | VARCHAR(50) | No | | Unique ward code |
| `ward_number` | INTEGER | No | | Ward number within constituency |
| `boundaries` | JSONB | Yes | | GeoJSON polygon boundaries |
| `geom` | GEOGRAPHY | Yes | | PostGIS geometry (auto-populated) |
| `population` | INTEGER | Yes | | Total population |
| `voter_count` | INTEGER | No | 0 | Registered voters |
| `total_booths` | INTEGER | No | 0 | Number of polling booths |
| `demographics` | JSONB | No | {} | Demographic breakdown |
| `income_level` | VARCHAR(50) | Yes | | low/medium/high |
| `urbanization` | VARCHAR(50) | Yes | | urban/semi-urban/rural |
| `literacy_rate` | DECIMAL(5,2) | Yes | | Literacy percentage |
| `created_at` | TIMESTAMP | No | NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP | No | NOW() | Last update |

**Indexes:**
- PRIMARY KEY (`id`)
- UNIQUE (`code`)
- INDEX (`organization_id`)
- INDEX (`constituency_id`)
- INDEX (`ward_number`)
- INDEX (`urbanization`)
- INDEX (`income_level`)

---

### 11. PollingBooth

**Purpose:** Polling booths/stations

**Table:** `api_pollingbooth`

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| `id` | INTEGER | No | Auto | Primary key |
| `state_id` | INTEGER | No | | Foreign key to state |
| `district_id` | INTEGER | No | | Foreign key to district |
| `constituency_id` | INTEGER | No | | Foreign key to constituency |
| `booth_number` | VARCHAR(20) | No | | Official booth number |
| `name` | VARCHAR(300) | No | | Booth name/location |
| `building_name` | VARCHAR(200) | Yes | | School/building name |
| `address` | TEXT | Yes | | Full address |
| `area` | VARCHAR(200) | Yes | | Locality/area name |
| `landmark` | VARCHAR(200) | Yes | | Nearby landmark |
| `pincode` | VARCHAR(10) | Yes | | PIN code |
| `latitude` | DECIMAL(10,8) | Yes | | GPS latitude |
| `longitude` | DECIMAL(11,8) | Yes | | GPS longitude |
| `total_voters` | INTEGER | No | 0 | Total registered voters |
| `male_voters` | INTEGER | No | 0 | Male voters |
| `female_voters` | INTEGER | No | 0 | Female voters |
| `other_voters` | INTEGER | No | 0 | Other/transgender voters |
| `is_active` | BOOLEAN | No | True | Active booth |
| `is_accessible` | BOOLEAN | No | True | Wheelchair accessible |
| `metadata` | JSONB | No | {} | Additional info |
| `created_at` | TIMESTAMP | No | NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP | No | NOW() | Last update |

**Indexes:**
- PRIMARY KEY (`id`)
- UNIQUE (`constituency_id`, `booth_number`)
- INDEX (`state_id`, `district_id`)
- INDEX (`constituency_id`)
- INDEX (`booth_number`)
- INDEX (`is_active`)

---

### 12. PoliticalParty

**Purpose:** Political parties

**Table:** `api_politicalparty`

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| `id` | INTEGER | No | Auto | Primary key |
| `name` | VARCHAR(200) | No | | Full party name |
| `short_name` | VARCHAR(50) | No | | Abbreviation (e.g., TVK) |
| `symbol` | VARCHAR(100) | Yes | | Election symbol |
| `symbol_image` | VARCHAR(200) | Yes | | Symbol image URL |
| `status` | VARCHAR(20) | No | 'state' | national/state/regional |
| `headquarters` | VARCHAR(200) | Yes | | HQ location |
| `website` | VARCHAR(200) | Yes | | Official website |
| `founded_date` | DATE | Yes | | Foundation date |
| `ideology` | VARCHAR(200) | Yes | | Political ideology |
| `description` | TEXT | Yes | | Party description |
| `created_at` | TIMESTAMP | No | NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP | No | NOW() | Last update |

**Indexes:**
- PRIMARY KEY (`id`)
- UNIQUE (`name`)
- INDEX (`short_name`)
- INDEX (`status`)

---

### 13. IssueCategory

**Purpose:** Issue categories (based on TVK's 9 priorities)

**Table:** `api_issuecategory`

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| `id` | INTEGER | No | Auto | Primary key |
| `name` | VARCHAR(100) | No | | Issue name |
| `description` | TEXT | Yes | | Issue description |
| `parent_id` | INTEGER | Yes | | Foreign key to self (for subcategories) |
| `color` | VARCHAR(7) | No | '#3B82F6' | Hex color code |
| `icon` | VARCHAR(50) | Yes | | Icon name |
| `priority` | INTEGER | No | 0 | Priority level (1-9) |
| `is_active` | BOOLEAN | No | True | Active status |
| `created_at` | TIMESTAMP | No | NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP | No | NOW() | Last update |

**Indexes:**
- PRIMARY KEY (`id`)
- UNIQUE (`name`)
- INDEX (`parent_id`)
- INDEX (`priority`)

**Example Data:**
1. Social Justice & Caste Issues (Priority 9)
2. Women's Safety & Empowerment (Priority 8)
3. Youth Employment & Education (Priority 7)
4. Farmers & Agriculture (Priority 6)
... and 5 more

---

### 14. VoterSegment

**Purpose:** Voter demographic segments

**Table:** `api_votersegment`

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| `id` | INTEGER | No | Auto | Primary key |
| `name` | VARCHAR(100) | No | | Segment name |
| `description` | TEXT | Yes | | Segment description |
| `priority_level` | INTEGER | No | 5 | Priority (1-10) |
| `estimated_population` | INTEGER | Yes | | Estimated size |
| `characteristics` | JSONB | No | {} | Segment characteristics |
| `is_active` | BOOLEAN | No | True | Active status |
| `created_at` | TIMESTAMP | No | NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP | No | NOW() | Last update |

**Indexes:**
- PRIMARY KEY (`id`)
- UNIQUE (`name`)
- INDEX (`priority_level`)

**Example Segments:**
- Fishermen Community
- Farmers
- Youth (18-25)
- Women
- Senior Citizens

---

## Operational Tables

### 15. DirectFeedback

**Purpose:** Citizen feedback submissions

**Table:** `api_directfeedback`

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| `id` | INTEGER | No | Auto | Primary key |
| `feedback_id` | UUID | No | Auto | Public feedback ID |
| `citizen_name` | VARCHAR(200) | No | | Citizen name |
| `citizen_age` | INTEGER | Yes | | Age |
| `citizen_phone` | VARCHAR(20) | Yes | | Phone number |
| `citizen_email` | VARCHAR(254) | Yes | | Email |
| `state_id` | INTEGER | No | | Foreign key to state |
| `district_id` | INTEGER | No | | Foreign key to district |
| `constituency_id` | INTEGER | Yes | | Foreign key to constituency |
| `ward` | VARCHAR(200) | Yes | | Ward name/number |
| `booth_number` | VARCHAR(50) | Yes | | Booth number |
| `detailed_location` | TEXT | Yes | | Location details |
| `issue_category_id` | INTEGER | No | | Foreign key to issue_category |
| `message_text` | TEXT | No | | Feedback message |
| `expectations` | TEXT | Yes | | Citizen expectations |
| `voter_segment_id` | INTEGER | Yes | | Foreign key to voter_segment |
| `status` | VARCHAR(20) | No | 'pending' | pending/reviewed/escalated/resolved |
| `ai_sentiment_polarity` | VARCHAR(20) | Yes | | positive/negative/neutral |
| `ai_urgency` | VARCHAR(20) | Yes | | low/medium/high/urgent |
| `review_notes` | TEXT | Yes | | Admin review notes |
| `reviewed_by_id` | INTEGER | Yes | | Foreign key to auth_user |
| `reviewed_at` | TIMESTAMP | Yes | | Review timestamp |
| `submitted_at` | TIMESTAMP | No | NOW() | Submission timestamp |
| `created_at` | TIMESTAMP | No | NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP | No | NOW() | Last update |

**Indexes:**
- PRIMARY KEY (`id`)
- UNIQUE (`feedback_id`)
- INDEX (`state_id`, `district_id`)
- INDEX (`constituency_id`)
- INDEX (`issue_category_id`)
- INDEX (`status`)
- INDEX (`ai_urgency`)
- INDEX (`submitted_at`)

---

### 16. FieldReport

**Purpose:** Field reports from volunteers

**Table:** `api_fieldreport`

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| `id` | INTEGER | No | Auto | Primary key |
| `volunteer_id` | INTEGER | No | | Foreign key to auth_user |
| `state_id` | INTEGER | No | | Foreign key to state |
| `district_id` | INTEGER | No | | Foreign key to district |
| `constituency_id` | INTEGER | Yes | | Foreign key to constituency |
| `ward` | VARCHAR(200) | Yes | | Ward name |
| `booth_number` | VARCHAR(50) | Yes | | Booth number |
| `report_type` | VARCHAR(50) | No | | daily_summary/event_feedback/issue_report/competitor_activity |
| `title` | VARCHAR(300) | No | | Report title |
| `positive_reactions` | JSONB | No | [] | Array of positive observations |
| `negative_reactions` | JSONB | No | [] | Array of negative observations |
| `key_issues` | JSONB | No | [] | Array of issue category IDs |
| `voter_segments_met` | JSONB | No | [] | Array of segment IDs |
| `crowd_size` | INTEGER | Yes | | Estimated crowd size |
| `quotes` | JSONB | No | [] | Notable quotes |
| `notes` | TEXT | Yes | | Additional notes |
| `verification_status` | VARCHAR(20) | No | 'pending' | pending/verified/rejected |
| `verified_by_id` | INTEGER | Yes | | Foreign key to auth_user |
| `verified_at` | TIMESTAMP | Yes | | Verification timestamp |
| `verification_notes` | TEXT | Yes | | Verification notes |
| `submitted_at` | TIMESTAMP | No | NOW() | Submission timestamp |
| `created_at` | TIMESTAMP | No | NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP | No | NOW() | Last update |

**Indexes:**
- PRIMARY KEY (`id`)
- INDEX (`volunteer_id`)
- INDEX (`state_id`, `district_id`)
- INDEX (`constituency_id`)
- INDEX (`report_type`)
- INDEX (`verification_status`)
- INDEX (`submitted_at`)

---

### 17. SentimentData

**Purpose:** Aggregated sentiment analysis data

**Table:** `api_sentimentdata`

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| `id` | INTEGER | No | Auto | Primary key |
| `source_type` | VARCHAR(50) | No | | feedback/field_report/social_media |
| `source_id` | INTEGER | No | | ID of source record |
| `state_id` | INTEGER | No | | Foreign key to state |
| `district_id` | INTEGER | Yes | | Foreign key to district |
| `constituency_id` | INTEGER | Yes | | Foreign key to constituency |
| `sentiment_score` | DECIMAL(5,2) | No | 0 | Sentiment score (-1 to 1) |
| `polarity` | VARCHAR(20) | Yes | | positive/negative/neutral |
| `emotion` | VARCHAR(50) | Yes | | Detected emotion |
| `confidence` | DECIMAL(5,2) | Yes | | AI confidence (0-1) |
| `keywords` | JSONB | No | [] | Extracted keywords |
| `analyzed_at` | TIMESTAMP | No | NOW() | Analysis timestamp |
| `created_at` | TIMESTAMP | No | NOW() | Creation timestamp |

**Indexes:**
- PRIMARY KEY (`id`)
- INDEX (`source_type`, `source_id`)
- INDEX (`state_id`, `district_id`)
- INDEX (`polarity`)
- INDEX (`analyzed_at`)

---

## System Tables

### 18. AuditLog

**Purpose:** System audit trail

**Table:** `api_auditlog`

| Column | Type | Null | Description |
|--------|------|------|-------------|
| `id` | INTEGER | No | Primary key |
| `user_id` | INTEGER | Yes | Foreign key to auth_user |
| `action` | VARCHAR(50) | No | Action type |
| `target_model` | VARCHAR(100) | Yes | Target model name |
| `target_id` | VARCHAR(100) | Yes | Target record ID |
| `changes` | JSONB | No | Changed fields |
| `ip_address` | VARCHAR(45) | Yes | IP address |
| `user_agent` | TEXT | Yes | Browser user agent |
| `timestamp` | TIMESTAMP | No | Action timestamp |

**Action Types:**
- create, read, update, delete
- login, logout
- permission_change, role_change

**Indexes:**
- PRIMARY KEY (`id`)
- INDEX (`user_id`, `timestamp`)
- INDEX (`action`)
- INDEX (`target_model`, `target_id`)

---

### 19. Notification

**Purpose:** User notifications

**Table:** `api_notification`

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| `id` | INTEGER | No | Auto | Primary key |
| `user_id` | INTEGER | No | | Foreign key to auth_user |
| `title` | VARCHAR(200) | No | | Notification title |
| `message` | TEXT | No | | Notification message |
| `notification_type` | VARCHAR(20) | No | 'info' | info/success/warning/error/task/user/system |
| `is_read` | BOOLEAN | No | False | Read status |
| `read_at` | TIMESTAMP | Yes | | Read timestamp |
| `related_model` | VARCHAR(100) | Yes | | Related model name |
| `related_id` | VARCHAR(100) | Yes | | Related record ID |
| `metadata` | JSONB | No | {} | Additional data |
| `supabase_id` | UUID | Yes | | Supabase sync ID |
| `synced_to_supabase` | BOOLEAN | No | False | Sync status |
| `created_at` | TIMESTAMP | No | NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP | No | NOW() | Last update |

**Indexes:**
- PRIMARY KEY (`id`)
- INDEX (`user_id`, `-created_at`)
- INDEX (`is_read`)
- INDEX (`notification_type`)
- UNIQUE (`supabase_id`)

---

### 20. BulkUploadJob

**Purpose:** Track CSV bulk upload jobs

**Table:** `api_bulkuploadjob`

| Column | Type | Null | Default | Description |
|--------|------|------|---------|-------------|
| `id` | INTEGER | No | Auto | Primary key |
| `uploaded_by_id` | INTEGER | No | | Foreign key to auth_user |
| `file_name` | VARCHAR(255) | No | | Original filename |
| `file_path` | VARCHAR(500) | Yes | | Stored file path |
| `upload_type` | VARCHAR(50) | No | | wards/booths/constituencies |
| `status` | VARCHAR(20) | No | 'pending' | pending/processing/completed/failed |
| `total_rows` | INTEGER | No | 0 | Total rows in file |
| `processed_rows` | INTEGER | No | 0 | Rows processed |
| `successful_rows` | INTEGER | No | 0 | Successfully imported |
| `failed_rows` | INTEGER | No | 0 | Failed to import |
| `error_summary` | JSONB | No | {} | Error summary |
| `started_at` | TIMESTAMP | Yes | | Processing start time |
| `completed_at` | TIMESTAMP | Yes | | Processing completion time |
| `created_at` | TIMESTAMP | No | NOW() | Creation timestamp |

**Indexes:**
- PRIMARY KEY (`id`)
- INDEX (`uploaded_by_id`)
- INDEX (`upload_type`)
- INDEX (`status`)
- INDEX (`created_at`)

---

### 21. BulkUploadError

**Purpose:** Track individual row errors in bulk uploads

**Table:** `api_bulkuploaderror`

| Column | Type | Null | Description |
|--------|------|------|-------------|
| `id` | INTEGER | No | Primary key |
| `job_id` | INTEGER | No | Foreign key to bulkuploadjob |
| `row_number` | INTEGER | No | Row number in CSV |
| `row_data` | JSONB | No | Original row data |
| `error_type` | VARCHAR(100) | No | Error category |
| `error_message` | TEXT | No | Error description |
| `created_at` | TIMESTAMP | No | Creation timestamp |

**Indexes:**
- PRIMARY KEY (`id`)
- INDEX (`job_id`)
- INDEX (`row_number`)
- INDEX (`error_type`)

---

## Relationships

### One-to-One
- `User` ↔ `UserProfile` (each user has exactly one profile)

### One-to-Many
- `Organization` → `UserProfile` (one org has many members)
- `Organization` → `Ward` (one org has many wards)
- `Organization` → `PollingBooth` (one org has many booths)
- `State` → `District` (one state has many districts)
- `State` → `Constituency` (one state has many constituencies)
- `District` → `Constituency` (one district has many constituencies)
- `Constituency` → `Ward` (one constituency has many wards)
- `Constituency` → `PollingBooth` (one constituency has many booths)
- `Ward` → `PollingBooth` (one ward has many booths)
- `User` → `DirectFeedback` (one user reviews many feedback)
- `User` → `FieldReport` (one user submits many reports)
- `User` → `AuditLog` (one user has many log entries)
- `IssueCategory` → `DirectFeedback` (one issue category has many feedback)
- `VoterSegment` → `DirectFeedback` (one segment has many feedback)

### Many-to-Many
- `UserProfile` ↔ `Permission` (via `UserPermission`)
- `PoliticalParty` ↔ `State` (parties active in multiple states)

---

## Indexes

### Performance-Critical Indexes

1. **Geographic Lookups:**
   - `api_constituency` (state_id, constituency_type)
   - `api_pollingbooth` (state_id, district_id)
   - `api_pollingbooth` (constituency_id)

2. **User Lookups:**
   - `auth_user` (username, email)
   - `api_userprofile` (role, organization_id)

3. **Feedback Queries:**
   - `api_directfeedback` (status, submitted_at)
   - `api_directfeedback` (constituency_id, status)
   - `api_directfeedback` (ai_urgency)

4. **Time-Series:**
   - `api_auditlog` (user_id, timestamp)
   - `api_notification` (user_id, created_at)

---

## Constraints

### Unique Constraints
- `Organization.slug` - URL-safe unique identifier
- `State.code` - 2-letter state code
- `Constituency.code` - Unique constituency code
- `Ward.code` - Unique ward code
- `PollingBooth (constituency_id, booth_number)` - Booth number unique per constituency
- `RolePermission (role, permission_id)` - One permission per role
- `UserPermission (user_profile_id, permission_id)` - One override per user-permission

### Foreign Key Constraints
- All foreign keys have `ON DELETE` behaviors:
  - `CASCADE` - Delete child records (e.g., deleting user deletes notifications)
  - `SET NULL` - Set to null (e.g., deleting district keeps constituency)
  - `PROTECT` - Prevent deletion if children exist (e.g., can't delete state with constituencies)

### Check Constraints
- `voter_count >= 0` - No negative voters
- `population >= voter_count` - Population must be greater than or equal to voter count
- `latitude BETWEEN -90 AND 90` - Valid latitude range
- `longitude BETWEEN -180 AND 180` - Valid longitude range
- `sentiment_score BETWEEN -1 AND 1` - Sentiment score range

---

## Data Types

### Common Data Types

**Identifiers:**
- `INTEGER` / `SERIAL` - Auto-incrementing primary keys
- `UUID` - Universally unique identifiers (for public IDs)

**Text:**
- `VARCHAR(n)` - Variable-length strings with max length
- `TEXT` - Unlimited text
- `CHAR(n)` - Fixed-length strings

**Numbers:**
- `INTEGER` - Whole numbers
- `DECIMAL(p,s)` - Precise decimals (e.g., coordinates, percentages)
- `FLOAT` - Approximate decimals

**Dates & Times:**
- `DATE` - Date only (YYYY-MM-DD)
- `TIMESTAMP` - Date and time with timezone

**Boolean:**
- `BOOLEAN` - True/False

**JSON:**
- `JSONB` - Binary JSON (indexed, searchable)

**Geographic (PostGIS):**
- `GEOGRAPHY(POINT, 4326)` - GPS coordinates
- `GEOGRAPHY(POLYGON, 4326)` - Boundaries

---

## Migration Notes

### Creating Tables

**Django:**
```bash
python manage.py makemigrations
python manage.py migrate
```

### Adding Wards Table (Phase 2)

```sql
CREATE TABLE api_ward (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id INTEGER NOT NULL REFERENCES api_organization(id),
    constituency_id INTEGER NOT NULL REFERENCES api_constituency(id),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    ward_number INTEGER NOT NULL,
    population INTEGER,
    voter_count INTEGER DEFAULT 0,
    total_booths INTEGER DEFAULT 0,
    urbanization VARCHAR(50),
    income_level VARCHAR(50),
    literacy_rate DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_ward_organization ON api_ward(organization_id);
CREATE INDEX idx_ward_constituency ON api_ward(constituency_id);
```

---

## Backup & Recovery

### Recommended Backup Schedule

**Daily:**
- Full database backup
- Transaction log backup

**Weekly:**
- Archive to cold storage

**Monthly:**
- Point-in-time recovery test

### PostgreSQL Backup Commands

```bash
# Full backup
pg_dump -U postgres -d pulseofpeople > backup.sql

# Restore
psql -U postgres -d pulseofpeople < backup.sql

# Backup specific table
pg_dump -U postgres -d pulseofpeople -t api_pollingbooth > booths_backup.sql
```

---

## Monitoring

### Key Metrics to Monitor

1. **Table Sizes:**
   ```sql
   SELECT
       tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
   FROM pg_tables
   WHERE schemaname = 'public'
   ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
   ```

2. **Index Usage:**
   ```sql
   SELECT * FROM pg_stat_user_indexes
   WHERE schemaname = 'public'
   ORDER BY idx_scan DESC;
   ```

3. **Slow Queries:**
   - Enable `pg_stat_statements` extension
   - Monitor queries taking > 1 second

---

## Support

For database questions:
- Email: support@pulseofpeople.com
- Documentation: https://docs.pulseofpeople.com
- Database migrations: Contact admin

---

**Last Updated**: November 9, 2025
**Schema Version**: 2.0 (with Wards support)
**For**: Pulse of People Platform
