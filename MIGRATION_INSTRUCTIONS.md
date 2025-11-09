# 🚀 Apply Supabase Migrations - Step by Step

Follow these exact steps to apply both Phase 1 and Phase 2 migrations.

---

## ⚡ Quick Start (3 Steps)

### Step 1: Open Supabase SQL Editor

1. Go to: **https://app.supabase.com/project/iwtgbseaoztjbnvworyq/sql**
   *(This is a direct link to your project's SQL Editor)*

2. You should see the SQL Editor interface
   - If it asks you to log in, use your Supabase account credentials

### Step 2: Run Phase 1 Migration

**Copy this entire file:**
```
supabase/migrations/20251109_phase1_core_entities.sql
```

**Steps:**
1. Open the file in your editor (VS Code, etc.)
2. Press **Cmd+A** (Mac) or **Ctrl+A** (Windows) to select all
3. Press **Cmd+C** or **Ctrl+C** to copy
4. Go back to Supabase SQL Editor
5. Click the editor area and paste with **Cmd+V** or **Ctrl+V**
6. Click the **"RUN"** button (or press **Cmd+Enter** / **Ctrl+Enter**)

**Wait for it to finish.** You should see output like:
```
✅ CREATE EXTENSION
✅ CREATE TABLE organizations
✅ CREATE TABLE users
✅ CREATE TABLE user_permissions
✅ CREATE TABLE audit_logs
✅ INSERT 0 3 (organizations)
✅ INSERT 0 8 (users)
✅ INSERT 0 7 (permissions)
```

### Step 3: Run Phase 2 Migration

**Copy this entire file:**
```
supabase/migrations/20251109_phase2_geography_territory.sql
```

**Steps:**
1. In Supabase SQL Editor, click **"New query"** (top right, + icon)
2. Open the Phase 2 file in your editor
3. Press **Cmd+A** or **Ctrl+A** to select all
4. Press **Cmd+C** or **Ctrl+C** to copy
5. Go back to Supabase SQL Editor
6. Paste with **Cmd+V** or **Ctrl+V**
7. Click the **"RUN"** button

**Wait for it to finish.** You should see output like:
```
✅ CREATE TABLE constituencies
✅ CREATE TABLE wards
✅ CREATE TABLE polling_booths
✅ CREATE TABLE voters
✅ INSERT 0 5 (constituencies)
✅ INSERT 0 3 (wards)
✅ INSERT 0 10 (polling booths)
```

---

## ✅ Verification

After both migrations complete, run this verification query:

```sql
-- Copy and paste this into SQL Editor and run it
SELECT
    schemaname,
    tablename,
    (SELECT COUNT(*) FROM information_schema.columns
     WHERE table_name = tablename) as column_count
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename IN (
    'organizations', 'users', 'user_permissions', 'audit_logs',
    'constituencies', 'wards', 'polling_booths', 'voters'
  )
ORDER BY tablename;
```

**Expected Result:** 8 rows (one for each table)

---

## 🎉 Success Indicators

You'll know everything worked if you see:

✅ **8 tables listed** in the verification query
✅ **No error messages** during migration
✅ **Sample data counts:**
   - 3 organizations
   - 8 users
   - 5 constituencies
   - 10 polling booths

---

## 🚨 Common Issues & Solutions

### Issue: "relation already exists"
**Meaning:** Tables were already created before
**Solution:** Either skip migration or delete existing tables first

### Issue: "permission denied"
**Meaning:** Not logged in or wrong project
**Solution:** Make sure you're at https://app.supabase.com/project/iwtgbseaoztjbnvworyq/sql

### Issue: "syntax error"
**Meaning:** Part of the SQL didn't copy correctly
**Solution:** Re-copy the entire file and paste again

---

## 📞 Need Help?

If you encounter any errors:
1. Take a screenshot of the error message
2. Tell me which step failed (Phase 1 or Phase 2)
3. I'll help you fix it

---

**Ready?** Start with Step 1 above! 🚀
