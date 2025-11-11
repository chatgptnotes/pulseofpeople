# Quick Start Guide: Master Data Setup
## Pulse of People - TVK Party Project

**Date**: 2025-11-06
**Status**: ✅ Foundation Ready

---

## What's Been Completed ✅

### 1. Database Migrations Created
- ✅ `20251106_create_constituency_master.sql` - Complete with:
  - `assembly_constituencies` table (264 constituencies)
  - `elected_members` table (election history)
  - `polling_booths` table (70,000+ booths)
  - RLS policies
  - Helper functions
  - Views for analytics

### 2. TypeScript Types Updated
- ✅ `/src/types/geography.ts` enhanced with:
  - `ReservationType` enum (12 reservation categories)
  - Enhanced `AssemblyConstituency` interface
  - `ElectedMember` interface
  - Full geographic hierarchy types

### 3. Seed Data Templates
- ✅ `/supabase/seeds/01_constituency_seed_template.sql`
  - Structure for 234 TN + 30 PY constituencies
  - Sample elected members
  - Sample polling booths

### 4. Documentation
- ✅ `/docs/MASTER_DATA_ARCHITECTURE.md` (Comprehensive architecture)
- ✅ `/docs/SEED_DATA_RECOMMENDATIONS.md` (All seed files needed)
- ✅ `/docs/QUICK_START_GUIDE.md` (This file)

---

## Run Database Migrations

### Step 1: Apply the Migration

```bash
# Navigate to your project directory
cd /Users/murali/1backup/pulseofpeople6nov/voter

# Apply the migration to your Supabase database
# Option A: Using Supabase CLI
supabase db push

# Option B: Using psql directly (if you have DATABASE_URL)
psql $DATABASE_URL -f supabase/migrations/20251106_create_constituency_master.sql

# Option C: Using Supabase Dashboard
# 1. Go to https://supabase.com/dashboard
# 2. Select your project
# 3. Go to SQL Editor
# 4. Copy and paste the migration file contents
# 5. Run the SQL
```

### Step 2: Verify Migration

```sql
-- Check if tables were created
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('assembly_constituencies', 'elected_members', 'polling_booths');

-- Should return 3 rows

-- Check table structure
\d assembly_constituencies
\d elected_members
\d polling_booths
```

---

## Next Immediate Tasks

### Priority 1: Create Missing Master Tables (Today)

You need to create 2 more migration files:

#### A. Create States Table

Create: `/supabase/migrations/20251107_create_states_table.sql`

```sql
CREATE TABLE IF NOT EXISTS states (
    code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    name_tamil TEXT,
    total_districts INTEGER DEFAULT 0,
    total_constituencies INTEGER DEFAULT 0,
    total_voters BIGINT DEFAULT 0,
    area_km2 DECIMAL(10,2),
    center_lat DECIMAL(10,8),
    center_lng DECIMAL(11,8),
    center_point GEOGRAPHY(POINT, 4326),
    geojson JSONB,
    tenant_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO states (code, name, name_tamil, total_districts, total_constituencies, center_lat, center_lng) VALUES
('TN', 'Tamil Nadu', 'தமிழ்நாடு', 38, 234, 11.1271, 78.6569),
('PY', 'Pondicherry', 'புதுச்சேரி', 4, 30, 11.9416, 79.8083);

-- Enable RLS
ALTER TABLE states ENABLE ROW LEVEL SECURITY;

CREATE POLICY states_select_policy ON states
    FOR SELECT USING (auth.role() = 'authenticated');
```

#### B. Create Districts Table

Create: `/supabase/migrations/20251107_create_districts_table.sql`

```sql
CREATE TABLE IF NOT EXISTS districts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    name_tamil TEXT,
    state_code TEXT NOT NULL REFERENCES states(code),
    center_lat DECIMAL(10,8),
    center_lng DECIMAL(11,8),
    center_point GEOGRAPHY(POINT, 4326),
    area_km2 DECIMAL(10,2),
    geojson JSONB,
    total_constituencies INTEGER DEFAULT 0,
    total_voters BIGINT DEFAULT 0,
    total_polling_booths INTEGER DEFAULT 0,
    headquarters TEXT,
    formation_year INTEGER,
    tenant_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_districts_state ON districts(state_code);
CREATE INDEX idx_districts_code ON districts(code);

-- Insert Tamil Nadu districts (38)
INSERT INTO districts (code, name, name_tamil, state_code, headquarters) VALUES
('TN01', 'Ariyalur', 'அரியலூர்', 'TN', 'Ariyalur'),
('TN02', 'Chengalpattu', 'செங்கல்பட்டு', 'TN', 'Chengalpattu'),
('TN03', 'Chennai', 'சென்னை', 'TN', 'Chennai'),
-- ... (add all 38 districts - see enum in geography.ts)

-- Insert Pondicherry districts (4)
('PY01', 'Puducherry', 'புதுச்சேரி', 'PY', 'Puducherry'),
('PY02', 'Karaikal', 'காரைக்கால்', 'PY', 'Karaikal'),
('PY03', 'Mahe', 'மாஹே', 'PY', 'Mahe'),
('PY04', 'Yanam', 'ஆனம்', 'PY', 'Yanam');

-- Enable RLS
ALTER TABLE districts ENABLE ROW LEVEL SECURITY;

CREATE POLICY districts_select_policy ON districts
    FOR SELECT USING (auth.role() = 'authenticated');
```

Then run:
```bash
psql $DATABASE_URL -f supabase/migrations/20251107_create_states_table.sql
psql $DATABASE_URL -f supabase/migrations/20251107_create_districts_table.sql
```

### Priority 2: Create Political Parties Tables (This Week)

Create: `/supabase/migrations/20251108_create_political_parties.sql`

This should include:
- `political_parties` table (TVK, DMK, AIADMK, BJP, etc.)
- `political_alliances` table
- `party_members` table (TVK leadership)
- `party_district_units` table

**See**: `/docs/SEED_DATA_RECOMMENDATIONS.md` Section 2 for complete SQL

### Priority 3: Import Real Constituency Data

The template in `01_constituency_seed_template.sql` has only 5 sample constituencies.

You need to import all 264 constituencies:
- 234 from Tamil Nadu
- 30 from Pondicherry

**Data Source**:
- Tamil Nadu CEO: https://www.elections.tn.gov.in
- Download constituency list with:
  - Constituency number
  - Name (English & Tamil)
  - District
  - Reservation type (SC/ST/General)
  - Parliamentary constituency
  - Current MLA details

**Import Process**:
1. Get official data from EC India
2. Clean and format in Excel/CSV
3. Convert to SQL INSERT statements
4. Run seed file

---

## Verify Your Setup

### Test Queries

```sql
-- 1. Check hierarchy
SELECT
    s.name as state,
    COUNT(DISTINCT d.code) as districts,
    COUNT(DISTINCT ac.code) as constituencies
FROM states s
LEFT JOIN districts d ON s.code = d.state_code
LEFT JOIN assembly_constituencies ac ON d.code = ac.district_code
GROUP BY s.name;

-- Expected output:
-- Tamil Nadu    | 38 | 234
-- Pondicherry   | 4  | 30


-- 2. Check reservation distribution
SELECT
    reservation_type,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as percentage
FROM assembly_constituencies
WHERE state_code = 'TN'
GROUP BY reservation_type;

-- Expected (approximate):
-- Scheduled Castes  | 44  | 18.8%
-- Scheduled Tribes  | 3   | 1.3%
-- Unreserved       | 187 | 79.9%


-- 3. Check current MLAs (2021 election)
SELECT
    ac.name as constituency,
    em.member_name,
    em.political_party,
    em.vote_percentage
FROM assembly_constituencies ac
LEFT JOIN elected_members em ON ac.code = em.constituency_code
WHERE em.is_current_member = TRUE
ORDER BY ac.constituency_number
LIMIT 10;


-- 4. Test spatial queries (nearby booths)
SELECT * FROM find_nearby_booths(13.0827, 80.2707, 5000, 10);
-- This finds polling booths within 5km of Chennai center


-- 5. Test election history function
SELECT * FROM get_constituency_election_history('TN001');
-- Shows all past elections for constituency TN001
```

---

## Frontend Integration Roadmap

Once your database is ready, follow this sequence:

### Week 1: Data Layer
1. ✅ Database migrations applied
2. ⏳ Create Supabase service files:
   - `/src/services/api/constituencyService.ts`
   - `/src/services/api/districtService.ts`
   - `/src/services/api/stateService.ts`

### Week 2: State Management
3. Create context providers:
   - `/src/contexts/GeographyContext.tsx`
   - `/src/contexts/DrillDownContext.tsx`

4. Create custom hooks:
   - `/src/hooks/useGeography.ts`
   - `/src/hooks/useDrillDown.ts`
   - `/src/hooks/useConstituencies.ts`

### Week 3: UI Components
5. Create selector components:
   - `/src/components/geography/StateSelector.tsx`
   - `/src/components/geography/DistrictSelector.tsx`
   - `/src/components/geography/ConstituencySelector.tsx`
   - `/src/components/geography/GeoBreadcrumb.tsx`

6. Create map components:
   - `/src/components/maps/DrillDownMap.tsx` (Main component)
   - `/src/components/maps/StateMap.tsx`
   - `/src/components/maps/DistrictMap.tsx`
   - `/src/components/maps/ConstituencyMap.tsx`

### Week 4: Dashboard Integration
7. Integrate with existing dashboards
8. Add sentiment visualization by geography
9. Performance optimization
10. Testing

---

## Project Structure (Updated)

```
voter/
├── supabase/
│   ├── migrations/
│   │   ├── 20251027_create_all_tables.sql
│   │   ├── 20251028_add_rbac_system.sql
│   │   ├── 20251029_single_db_multi_tenant.sql
│   │   ├── 20251106_create_constituency_master.sql ✅
│   │   ├── 20251107_create_states_table.sql       ⏳ TODO
│   │   ├── 20251107_create_districts_table.sql    ⏳ TODO
│   │   └── 20251108_create_political_parties.sql  ⏳ TODO
│   │
│   └── seeds/
│       ├── 01_constituency_seed_template.sql ✅
│       ├── 02_states_seed.sql       ⏳ TODO (2 records)
│       ├── 03_districts_seed.sql    ⏳ TODO (42 records)
│       ├── 04_constituencies_seed.sql ⏳ TODO (264 records)
│       ├── 10_tvk_party_structure.sql ⏳ TODO
│       ├── 20_all_parties_seed.sql    ⏳ TODO
│       ├── 40_voter_segments.sql      ⏳ TODO
│       └── 50_issue_categories.sql    ⏳ TODO
│
├── src/
│   ├── types/
│   │   └── geography.ts ✅ (Updated)
│   │
│   ├── services/
│   │   └── api/
│   │       ├── constituencyService.ts ⏳ TODO
│   │       ├── districtService.ts     ⏳ TODO
│   │       └── stateService.ts        ⏳ TODO
│   │
│   ├── contexts/
│   │   ├── GeographyContext.tsx      ⏳ TODO
│   │   └── DrillDownContext.tsx      ⏳ TODO
│   │
│   ├── hooks/
│   │   ├── useGeography.ts           ⏳ TODO
│   │   ├── useDrillDown.ts           ⏳ TODO
│   │   └── useConstituencies.ts      ⏳ TODO
│   │
│   └── components/
│       ├── geography/                 ⏳ TODO (Week 3)
│       └── maps/                      ⏳ TODO (Week 3)
│
└── docs/
    ├── MASTER_DATA_ARCHITECTURE.md ✅
    ├── SEED_DATA_RECOMMENDATIONS.md ✅
    └── QUICK_START_GUIDE.md ✅ (This file)
```

---

## Common Issues & Solutions

### Issue 1: Migration fails with "relation already exists"

**Solution**: Drop and recreate:
```sql
DROP TABLE IF EXISTS assembly_constituencies CASCADE;
DROP TABLE IF EXISTS elected_members CASCADE;
DROP TABLE IF EXISTS polling_booths CASCADE;
-- Then run migration again
```

### Issue 2: RLS policies blocking data access

**Solution**: Check your user's role:
```sql
SELECT auth.role();
-- Should return 'authenticated'

-- Temporarily disable RLS for testing:
ALTER TABLE assembly_constituencies DISABLE ROW LEVEL SECURITY;
-- (Re-enable after testing)
```

### Issue 3: PostGIS functions not working

**Solution**: Ensure PostGIS extension is enabled:
```sql
CREATE EXTENSION IF NOT EXISTS "postgis";
```

---

## Success Criteria

✅ **You're ready to proceed when:**

1. All 3 core tables exist:
   - [ ] `states` (2 records)
   - [ ] `districts` (42 records)
   - [ ] `assembly_constituencies` (264 records)

2. Sample data loaded:
   - [ ] At least 10 constituencies with complete data
   - [ ] At least 5 elected members
   - [ ] At least 20 polling booths

3. All queries work:
   - [ ] Can fetch constituencies by district
   - [ ] Can get election history
   - [ ] Can find nearby booths (spatial query)

4. RLS policies work:
   - [ ] Authenticated users can read data
   - [ ] Admins can write data

---

## Next Actions (In Order)

1. ✅ Review this guide
2. ⏳ Run the constituency master migration
3. ⏳ Create states table migration
4. ⏳ Create districts table migration
5. ⏳ Verify all tables with test queries
6. ⏳ Import real constituency data
7. ⏳ Create political parties tables
8. ⏳ Start building API services

---

## Resources

- **Architecture**: `/docs/MASTER_DATA_ARCHITECTURE.md`
- **Seed Data Guide**: `/docs/SEED_DATA_RECOMMENDATIONS.md`
- **TypeScript Types**: `/src/types/geography.ts`
- **Migration File**: `/supabase/migrations/20251106_create_constituency_master.sql`
- **Seed Template**: `/supabase/seeds/01_constituency_seed_template.sql`

---

## Questions?

If you encounter any issues or need clarification:
1. Check the architecture document
2. Review the migration SQL comments
3. Test with the provided SQL queries
4. Check Supabase logs in dashboard

---

**Status**: ✅ Foundation complete, ready for data import

**Last Updated**: 2025-11-06

**Next Milestone**: Import all 264 constituencies + Create political parties tables
