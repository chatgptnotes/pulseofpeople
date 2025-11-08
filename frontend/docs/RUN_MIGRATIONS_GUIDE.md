# Migration Execution Guide
## Step-by-Step Instructions to Set Up TVK Database

**Date**: 2025-11-08
**Status**: Ready to execute

---

## Quick Overview

You have **6 migration files** to run in a specific order:

1. ✅ States table (2 records: TN, PY)
2. ✅ Districts table (42 records: 38 TN + 4 PY)
3. ✅ Constituency master tables (structure ready)
4. ✅ Political parties (14 parties including TVK)
5. ✅ Voter segments (40+ segments)
6. ✅ Issue categories (25+ issues)

---

## Method 1: Automated Script (Recommended) ⚡

### Step 1: Set Your Database URL

Get your Supabase connection string:

1. Go to https://supabase.com/dashboard
2. Select your project
3. Click **Settings** → **Database**
4. Copy **Connection String** → **URI**

It looks like:
```
postgresql://postgres.xxxxxxxxxxxx:[YOUR-PASSWORD]@aws-0-ap-south-1.pooler.supabase.com:5432/postgres
```

### Step 2: Export the Database URL

**macOS/Linux**:
```bash
export DATABASE_URL='postgresql://postgres.xxxxxxxxxxxx:YOUR_PASSWORD@aws-0-ap-south-1.pooler.supabase.com:5432/postgres'
```

**Windows (Command Prompt)**:
```cmd
set DATABASE_URL=postgresql://postgres.xxxxxxxxxxxx:YOUR_PASSWORD@aws-0-ap-south-1.pooler.supabase.com:5432/postgres
```

**Windows (PowerShell)**:
```powershell
$env:DATABASE_URL="postgresql://postgres.xxxxxxxxxxxx:YOUR_PASSWORD@aws-0-ap-south-1.pooler.supabase.com:5432/postgres"
```

### Step 3: Run the Automated Script

```bash
cd /Users/murali/1backup/pulseofpeople6nov/voter

# Make the script executable
chmod +x scripts/run_all_migrations.sh

# Run the script
./scripts/run_all_migrations.sh
```

**What the script does**:
- ✅ Tests database connection
- ✅ Checks all migration files exist
- ✅ Runs all 6 migrations in order
- ✅ Verifies all tables created
- ✅ Checks seed data counts
- ✅ Validates TVK party data
- ✅ Shows critical segments
- ✅ Shows top issues
- ✅ Runs final validation

**Expected output**:
```
=================================================
TVK PARTY DATABASE MIGRATION SCRIPT
=================================================
ℹ️  Database: postgresql://postgres:[HIDDEN]@...

✅ Database connection successful

=================================================
STEP 1: CHECKING MIGRATION FILES
=================================================
✅ Found: supabase/migrations/20251107_create_states_table.sql
✅ Found: supabase/migrations/20251107_create_districts_table.sql
✅ Found: supabase/migrations/20251106_create_constituency_master.sql
✅ Found: supabase/migrations/20251108_create_political_parties.sql
✅ Found: supabase/migrations/20251108_create_voter_segments.sql
✅ Found: supabase/migrations/20251108_create_issue_categories.sql

[... continues with all steps ...]

✅ All migrations completed successfully!
✅ Your TVK Party database is ready!
```

---

## Method 2: Manual Step-by-Step 📝

If you prefer manual control or the script doesn't work:

### Prerequisites

Install PostgreSQL client tools:

**macOS**:
```bash
brew install postgresql
```

**Ubuntu/Debian**:
```bash
sudo apt-get install postgresql-client
```

**Windows**:
Download from https://www.postgresql.org/download/windows/

### Migration Order

Navigate to your project:
```bash
cd /Users/murali/1backup/pulseofpeople6nov/voter
```

#### Migration 1: States Table

```bash
psql "$DATABASE_URL" -f supabase/migrations/20251107_create_states_table.sql
```

**Verify**:
```bash
psql "$DATABASE_URL" -c "SELECT code, name, total_districts FROM states;"
```

**Expected output**:
```
 code |    name     | total_districts
------+-------------+-----------------
 TN   | Tamil Nadu  |              38
 PY   | Puducherry  |               4
(2 rows)
```

#### Migration 2: Districts Table

```bash
psql "$DATABASE_URL" -f supabase/migrations/20251107_create_districts_table.sql
```

**Verify**:
```bash
psql "$DATABASE_URL" -c "SELECT state_code, COUNT(*) FROM districts GROUP BY state_code;"
```

**Expected output**:
```
 state_code | count
------------+-------
 TN         |    38
 PY         |     4
(2 rows)
```

#### Migration 3: Constituency Master Tables

```bash
psql "$DATABASE_URL" -f supabase/migrations/20251106_create_constituency_master.sql
```

**Verify**:
```bash
psql "$DATABASE_URL" -c "SELECT table_name FROM information_schema.tables WHERE table_name IN ('assembly_constituencies', 'elected_members', 'polling_booths');"
```

**Expected output**:
```
       table_name
-------------------------
 assembly_constituencies
 elected_members
 polling_booths
(3 rows)
```

#### Migration 4: Political Parties

```bash
psql "$DATABASE_URL" -f supabase/migrations/20251108_create_political_parties.sql
```

**Verify**:
```bash
psql "$DATABASE_URL" -c "SELECT code, name, current_leader FROM political_parties WHERE code IN ('TVK', 'DMK', 'AIADMK', 'BJP');"
```

**Expected output**:
```
 code |  name   |      current_leader
------+---------+---------------------------
 TVK  | TVK     | Vijay
 DMK  | DMK     | M. K. Stalin
 AIADMK | AIADMK | Edappadi K. Palaniswami
 BJP  | BJP     | K. Annamalai (TN President)
(4 rows)
```

#### Migration 5: Voter Segments

```bash
psql "$DATABASE_URL" -f supabase/migrations/20251108_create_voter_segments.sql
```

**Verify**:
```bash
psql "$DATABASE_URL" -c "SELECT COUNT(*) as total_segments FROM voter_segments;"
```

**Expected output**:
```
 total_segments
----------------
             40  (or more)
(1 row)
```

**Check critical segments**:
```bash
psql "$DATABASE_URL" -c "SELECT segment_name, tvk_priority, tvk_win_probability FROM voter_segments WHERE tvk_priority = 'Critical' LIMIT 5;"
```

#### Migration 6: Issue Categories

```bash
psql "$DATABASE_URL" -f supabase/migrations/20251108_create_issue_categories.sql
```

**Verify**:
```bash
psql "$DATABASE_URL" -c "SELECT COUNT(*) as total_issues FROM issue_categories;"
```

**Expected output**:
```
 total_issues
--------------
           25  (or more)
(1 row)
```

**Check top issues**:
```bash
psql "$DATABASE_URL" -c "SELECT name, tvk_priority FROM issue_categories WHERE tvk_priority = 'Top';"
```

---

## Method 3: Using Supabase SQL Editor 🌐

If you don't have `psql` installed:

1. Go to https://supabase.com/dashboard
2. Select your project
3. Click **SQL Editor**
4. Click **New query**
5. Copy and paste each migration file's contents (one at a time)
6. Click **Run** (or press Ctrl+Enter)
7. Repeat for all 6 files in order

**Important**: Run migrations in the exact order listed above!

---

## Validation Queries

After running all migrations, verify everything:

### 1. Check All Tables Exist

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
    'states',
    'districts',
    'assembly_constituencies',
    'elected_members',
    'polling_booths',
    'political_parties',
    'political_alliances',
    'party_members',
    'voter_segments',
    'issue_categories'
)
ORDER BY table_name;
```

**Expected**: 10 tables

### 2. Check Data Counts

```sql
SELECT
    'States' as entity,
    COUNT(*) as count,
    '2' as expected
FROM states
UNION ALL
SELECT 'Districts', COUNT(*), '42'
FROM districts
UNION ALL
SELECT 'Political Parties', COUNT(*), '14'
FROM political_parties
UNION ALL
SELECT 'Alliances', COUNT(*), '2'
FROM political_alliances
UNION ALL
SELECT 'Voter Segments', COUNT(*), '40+'
FROM voter_segments
UNION ALL
SELECT 'Issue Categories', COUNT(*), '25+'
FROM issue_categories
ORDER BY entity;
```

### 3. Check TVK Party Data

```sql
SELECT
    code,
    name,
    name_tamil,
    current_leader,
    alliance,
    states_present,
    is_active
FROM political_parties
WHERE code = 'TVK';
```

**Expected**:
```
code | name | name_tamil              | current_leader | alliance    | states_present | is_active
-----|------|-------------------------|----------------|-------------|----------------|----------
TVK  | TVK  | தமிழக வெற்றி கழகம்    | Vijay          | Independent | {TN,PY}        | t
```

### 4. Check Critical Voter Segments

```sql
SELECT * FROM tvk_priority_segments
LIMIT 10;
```

### 5. Check Top Campaign Issues

```sql
SELECT * FROM tvk_top_issues;
```

### 6. Calculate Addressable Voters

```sql
SELECT * FROM calculate_addressable_voters();
```

**Expected output**:
```
 priority_level | total_segments | total_voters | avg_win_probability
----------------|----------------|--------------|--------------------
 Critical       |             15 |     45000000 |                0.68
 High           |             10 |     30000000 |                0.55
 Medium         |              8 |     15000000 |                0.45
 Low            |              7 |     10000000 |                0.30
```

---

## Troubleshooting

### Issue 1: "relation already exists"

**Cause**: Tables already exist from previous run

**Solution**:
```sql
-- Drop all tables and run migrations again
DROP TABLE IF EXISTS issue_categories CASCADE;
DROP TABLE IF EXISTS voter_segments CASCADE;
DROP TABLE IF EXISTS party_members CASCADE;
DROP TABLE IF EXISTS political_alliances CASCADE;
DROP TABLE IF EXISTS political_parties CASCADE;
DROP TABLE IF EXISTS polling_booths CASCADE;
DROP TABLE IF EXISTS elected_members CASCADE;
DROP TABLE IF EXISTS assembly_constituencies CASCADE;
DROP TABLE IF EXISTS districts CASCADE;
DROP TABLE IF EXISTS states CASCADE;
```

Then run migrations again.

### Issue 2: "permission denied"

**Cause**: Database user doesn't have CREATE permissions

**Solution**: Check your user has proper permissions in Supabase dashboard:
- Settings → Database → Roles
- Ensure your user has CREATEDB permission

### Issue 3: "psql: command not found"

**Cause**: PostgreSQL client not installed

**Solution**:
- Use Method 3 (Supabase SQL Editor) instead
- Or install PostgreSQL client tools (see Prerequisites)

### Issue 4: "could not connect to server"

**Cause**: Wrong DATABASE_URL or network issue

**Solution**:
1. Verify DATABASE_URL is correct
2. Check if your IP is allowed in Supabase (usually it is)
3. Test connection: `psql "$DATABASE_URL" -c "SELECT 1;"`

### Issue 5: "type geography does not exist"

**Cause**: PostGIS extension not enabled

**Solution**:
```sql
CREATE EXTENSION IF NOT EXISTS "postgis";
```

Then run migrations again.

### Issue 6: "function auth.uid() does not exist"

**Cause**: Running outside Supabase environment

**Solution**: This is normal if testing locally. RLS policies will work in Supabase.
To bypass for testing:
```sql
ALTER TABLE tablename DISABLE ROW LEVEL SECURITY;
```

---

## After Migration Success ✅

### What You Have Now:

1. ✅ **2 States** (Tamil Nadu, Pondicherry)
2. ✅ **42 Districts** (38 TN + 4 PY) with Tamil names and coordinates
3. ✅ **Tables ready** for 264 constituencies (import needed)
4. ✅ **14 Political Parties** including TVK
5. ✅ **2 Major Alliances** (DMK, AIADMK)
6. ✅ **40+ Voter Segments** with TVK strategy
7. ✅ **25+ Issue Categories** with TVK stance
8. ✅ **Helper functions** for analytics
9. ✅ **Views** for priority segments and issues
10. ✅ **RLS policies** for security

### Next Steps:

1. **Import Constituency Data**:
   - See `/docs/DATA_IMPORT_GUIDE.md`
   - Import all 234 TN + 30 PY constituencies
   - Import 2021 election results

2. **Add TVK Structure**:
   - District secretaries
   - Constituency organizers
   - Booth committees

3. **Build Frontend**:
   - Create API service layer
   - Build constituency selector
   - Create voter segment dashboard
   - Build issue tracker

4. **Start Campaign**:
   - Social media monitoring
   - Sentiment analysis
   - Targeted messaging

---

## Quick Reference Commands

### Connect to Database:
```bash
psql "$DATABASE_URL"
```

### List All Tables:
```sql
\dt
```

### Describe a Table:
```sql
\d table_name
```

### Count Records:
```sql
SELECT COUNT(*) FROM table_name;
```

### Exit psql:
```
\q
```

---

## Success Checklist ✅

After running migrations, verify:

- [ ] Can connect to database
- [ ] All 10 tables created
- [ ] States table has 2 records
- [ ] Districts table has 42 records
- [ ] Political parties has TVK
- [ ] Voter segments has 40+ records
- [ ] Issue categories has 25+ records
- [ ] TVK priority segments view works
- [ ] TVK top issues view works
- [ ] Addressable voters calculation works

---

**Ready to run migrations?**

Choose your method:
1. **Automated Script** (easiest): `./scripts/run_all_migrations.sh`
2. **Manual Commands** (step-by-step): Follow instructions above
3. **Supabase SQL Editor** (no tools needed): Copy-paste each file

---

**Last Updated**: 2025-11-08
**Status**: Ready to Execute
**Support**: Review this guide if any issues arise
