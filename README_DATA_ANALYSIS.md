# Frontend Data Requirements Analysis - Index

## Overview

This directory contains a comprehensive analysis of the **Pulse of People** frontend application's data requirements, including all Supabase tables, Django API endpoints, services, and data structures.

## Documents

### 1. **FRONTEND_DATA_ANALYSIS.md** (Primary Reference)
**Size:** 17 KB | **Reading Time:** 30 minutes

Complete breakdown of:
- All 13 Supabase tables with full field documentation
- 25+ Django API endpoints with parameters and auth requirements
- Data structures and TypeScript interfaces
- **Critical Gap Analysis**: What's being queried but missing from database
- Recommendations for implementation

**Best for:**
- Understanding what data the frontend expects
- Identifying missing tables
- API endpoint reference
- Type definitions documentation

**Key Sections:**
- Section 1: Supabase tables (13 tables detailed)
- Section 2: Django API endpoints (25+ endpoints)
- Section 3: Data structures & interfaces
- Section 4: Mock vs real data
- Section 5: Gap analysis (CRITICAL)

---

### 2. **CODE_REFERENCES.md** (Developer Reference)
**Size:** 13 KB | **Reading Time:** 20 minutes

Exact code locations for:
- Every service file with line counts
- Complete method signatures for all 9 services
- Service descriptions and dependencies
- Database migration files in correct sequence

**Best for:**
- Finding where data is queried in the codebase
- Understanding service architecture
- Migration file ordering
- Development reference

**Services Documented:**
1. userService (308 lines, 19 methods)
2. votersService (350 lines, 20 methods)
3. pollingBoothsService (300 lines, 14 methods)
4. constituenciesService (206 lines, 8 methods)
5. organizationService (211 lines, 12 methods)
6. dashboardService (500+ lines)
7. djangoApi (657 lines)
8. demoService (130 lines)
9. CRUD base class

---

### 3. **DATA_ARCHITECTURE.txt** (Architecture Reference)
**Size:** 29 KB | **Reading Time:** 40 minutes

Visual documentation of:
- ASCII architecture diagrams
- Complete database schema with field types
- Data flow diagrams
- Authentication security model
- Performance considerations & indexes
- Deployment checklist

**Best for:**
- Understanding overall architecture
- Database schema visualization
- Data flow understanding
- Performance tuning reference
- Deployment planning

**Diagrams Included:**
- Frontend services layer
- Supabase database structure
- Django API endpoints
- User registration flow
- Voter data query flow
- Dashboard metrics flow
- Geospatial query flow

---

### 4. **DATA_ANALYSIS_SUMMARY.txt** (Executive Summary)
**Size:** 4.4 KB | **Reading Time:** 5 minutes

Quick overview of:
- Key findings (tables, endpoints, services)
- Critical gaps summary
- File analysis statistics
- Recommendations prioritized

**Best for:**
- Quick understanding of the system
- Status overview
- Stakeholder communication
- Initial orientation

---

## Quick Reference

### Tables by Status

#### Implemented (7/12)
- organizations
- users
- user_permissions
- audit_logs
- constituencies
- polling_booths
- voters

#### Missing - Critical (5/12)
- sentiment_data (blocking dashboards)
- social_posts (engagement metrics)
- trending_topics (real-time keywords)
- alerts (crisis detection)
- field_reports (volunteer reports)

#### Custom (1/12)
- demo_requests

### Services by Method Count
- votersService: 20 methods
- userService: 19 methods
- pollingBoothsService: 14 methods
- organizationService: 12 methods
- constituenciesService: 8 methods
- demoService: 6 methods

### Django API Endpoints by Category
- Master Data: 8 endpoints
- Authentication: 6 endpoints
- Bulk Upload: 6 endpoints
- Citizen Feedback: 6 endpoints
- Analytics: 4 endpoints
- Field Reports: 4 endpoints
- Utility: 1 endpoint

## Data Hierarchy

```
State
  ↓
District
  ↓
Constituency (parliament, assembly, municipal, panchayat)
  ↓
Ward
  ↓
Polling Booth (regular, auxiliary, special)
  ↓
Voters (60+ fields each)
```

## Permission Hierarchy

```
superadmin
  ↓
admin
  ↓
manager
  ↓
analyst
  ↓
user
  ↓
viewer
  ↓
volunteer
```

## Permission Categories (10 × 6 = 60 permissions)
- users.{view, create, update, delete, manage, export}
- voters.{view, create, update, delete, manage, export}
- booths.{view, create, update, delete, manage, export}
- social.{view, create, update, delete}
- media.{view, manage}
- analytics.{view, export}
- reports.{view, create, export}
- campaigns.{view, create, update, delete, manage}
- field_workers.{view, manage}
- alerts.{view, manage}

## Voter Sentiment States
- strong_support
- support
- neutral
- oppose
- strong_oppose
- undecided

## Voter Categories
- core_supporter
- swing_voter
- opponent

## Critical Gaps

### Blocking Dashboards
The `dashboardService` queries these tables that don't exist:
1. **sentiment_data** - Requires immediate implementation
2. **social_posts** - Type definitions exist but table may be missing
3. **trending_topics** - Required for trending features
4. **alerts** - Required for crisis detection
5. **field_reports** - Required for volunteer reports

### Fields Referenced
See FRONTEND_DATA_ANALYSIS.md Section 5 for complete field requirements.

## Authentication Model

### Dual JWT System
- **Supabase JWT**: For RLS (Row-Level Security) enforcement
- **Django JWT**: For role-based access control

### Account Security
- Failed login tracking: `failed_login_attempts` field
- Account lockout: After 5 attempts, lock for 30 minutes
- Email verification: `email_verified_at` tracking
- Session persistence: localStorage with auto-refresh

## Geospatial Features

### PostGIS Integration
- Location type: GEOGRAPHY(POINT, 4326)
- Supported queries:
  - `find_booths_near(lat, lng, radius_meters)` - Find nearby polling booths
  - `get_constituency_stats(constituency_id)` - Aggregated statistics

### Indexes
- polling_booths GIST(location) - Spatial index
- sentiment_data GIST(location_point) - Spatial index for sentiment locations

## Real-Time Support

### Supabase Subscriptions
```typescript
subscribeToTable('voters', callback) // Watch all changes
subscribeToRecord('voters', voterId, callback) // Watch specific record
```

### Supported Events
- INSERT, UPDATE, DELETE
- Real-time permission changes
- Alert status updates
- Voter sentiment changes
- Field report submissions

## Database Functions (RPC)

### Implemented
- `get_user_permissions(user_id)` → Permission array
- `has_permission(user_id, permission_key)` → Boolean
- `find_booths_near(lat, lng, radius)` → Booth list with distances
- `get_constituency_stats(constituency_id)` → Aggregated stats

### Missing
- Sentiment aggregation functions
- Social post analytics functions
- Voter analysis functions
- Alert generation functions

## Recommendations Priority

### Immediate (Week 1)
1. Create missing tables (sentiment_data, social_posts, trending_topics, alerts, field_reports)
2. Run all 13 migrations in sequence
3. Test all dashboard queries

### Short-term (Sprint 1)
4. Add RPC functions for sentiment aggregation
5. Seed master tables
6. Initialize permission hierarchy
7. Implement missing type definitions

### Medium-term (Sprint 2)
8. Create required database indexes
9. Test geospatial queries
10. Set up real-time subscriptions
11. Implement caching strategy

## Migration Files (In Order)

Location: `/frontend/supabase/migrations/`

1. 20251027_create_all_tables.sql - Main schema
2. 20251027_create_tenant_registry.sql - Multi-tenancy
3. 20251028_add_rbac_system.sql - RBAC
4. 20251029_optimize_indexes.sql - Indexes
5. 20251029_single_db_multi_tenant.sql - Single DB mode
6. 20251106_create_constituency_master.sql - Constituencies
7. 20251107_create_states_table.sql - States
8. 20251107_create_districts_table.sql - Districts
9. 20251108_create_issue_categories.sql - Issues
10. 20251108_create_political_parties.sql - Parties
11. 20251108_create_voter_segments.sql - Segments
12. 20251109_competitor_tracking.sql - Competitors
13. 20251109_tv_broadcast_schema.sql - Media

## File Statistics

### Files Analyzed
- Service files: 19
- Context providers: 6
- Type definition files: 2 (730 lines)
- Migration files: 13
- Data files: 5

### Total Coverage
- Django endpoints: 25+
- Supabase methods: 90+
- Data fields: 60+
- Data entities: 7 major
- RPC functions: 10+

## Performance Metrics

### Indexes
- users(email) - Auth lookups
- users(role) - Role filtering
- users(organization_id) - Organization isolation
- sentiment_data(timestamp DESC) - Time-series
- sentiment_data(issue) - Issue filtering
- polling_booths(constituency_id) - Geographic queries
- social_posts(timestamp DESC) - Activity feeds

### Pagination
- Default: page 1, pageSize 50
- Returns: { data, count, page, pageSize, totalPages }

### Caching Recommendations
- Master data: Memory cache
- Permissions: 5-minute expiry
- Voter stats: 15-minute expiry
- Sentiment: No caching (real-time)

## Implementation Checklist

- [ ] Create missing 5 tables
- [ ] Run all 13 migrations
- [ ] Create indexes
- [ ] Seed master tables
- [ ] Initialize permissions
- [ ] Create RPC functions
- [ ] Configure RLS policies
- [ ] Test dashboard queries
- [ ] Set up real-time subscriptions
- [ ] Test geospatial queries
- [ ] Test permission enforcement
- [ ] Load test system

## Document Navigation

```
START HERE:
├─ Quick Overview (5 min)
│  └─ DATA_ANALYSIS_SUMMARY.txt
│
├─ Implementation Planning (30 min)
│  └─ FRONTEND_DATA_ANALYSIS.md
│     └─ Section 5: Gap Analysis
│
├─ Development (ongoing)
│  ├─ CODE_REFERENCES.md
│  └─ DATA_ARCHITECTURE.txt
│
└─ Architecture Review (60 min)
   └─ All documents in sequence
```

## Contact & Support

For questions about:
- **Data requirements**: See FRONTEND_DATA_ANALYSIS.md
- **Code locations**: See CODE_REFERENCES.md
- **Architecture**: See DATA_ARCHITECTURE.txt
- **Quick facts**: See DATA_ANALYSIS_SUMMARY.txt

## Version & Date

- **Analysis Date**: 2025-11-09
- **Frontend Framework**: React 18 + TypeScript + Vite
- **Backend**: Django + Supabase PostgreSQL
- **Coverage**: Comprehensive - All services, types, and endpoints documented

---

**Status**: Complete  
**Documents**: 4 files, 63.4 KB total  
**Quality**: Comprehensive analysis with architecture diagrams
