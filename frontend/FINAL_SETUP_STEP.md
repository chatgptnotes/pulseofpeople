# Final Setup Step - Run This One SQL File!

## What Happened So Far

✅ **Auth users created:** All 11 test users exist in Supabase Authentication
✅ **Code ready:** All mock code removed, using real Supabase
✅ **Dev server running:** http://localhost:3000

⚠️ **Remaining:** Need to add RBAC columns to users table and link to auth users

---

## One Simple Step

### Run the Quick RBAC Setup SQL

1. **Open:** https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq/sql/new

2. **Copy the entire file:**
   ```
   /Users/apple/Downloads/Pulseofpeoplevoter23oct/supabase/quick_rbac_setup.sql
   ```

3. **Paste** into the SQL Editor

4. **Click "Run"** (green button)

5. **Wait** for success message (should show 11 users in results)

---

## What This Does

This simplified SQL:
- ✅ Adds RBAC columns to your existing `users` table
- ✅ Links database users to the auth users we created
- ✅ Assigns proper roles and permissions
- ✅ No circular dependency issues

---

## After Running

**Immediately login at:** http://localhost:3000/login

Try any of these accounts:
```
superadmin@pulseofpeople.com / password
admin@bettroi.com / password
manager@bettroi.com / password
analyst@bettroi.com / password
user@bettroi.com / password
viewer@bettroi.com / password
... and 5 more
```

---

## Why This Version?

The original migration had a circular dependency error:
- `organizations` table referenced `users(id)`
- `users` table referenced `organizations(id)`
- This caused: "ERROR: column reference organization_id is ambiguous"

This quick setup:
- Skips creating extra tables for now
- Just adds RBAC to existing users table
- Gets you up and running immediately
- You can add other RBAC tables later if needed

---

## Troubleshooting

### If you get "column already exists":
✅ **Good!** Just continue - it means some columns already exist

### If you get "relation users does not exist":
❌ **Problem:** Your users table doesn't exist
**Solution:** Create it first or check if you're in the right project

### After running, still can't login:
1. Check: http://localhost:3000/login (make sure dev server is running)
2. Try: Clear localStorage: `localStorage.clear()` in browser console
3. Verify: Check users in Supabase Dashboard → Table Editor → users

---

**This is the last step! Run the SQL and you're done!** 🎉
