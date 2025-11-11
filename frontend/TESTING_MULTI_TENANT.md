# Testing Multi-Tenant Setup

## ✅ Fixes Applied

I've fixed the issues you encountered:

1. **Fixed tenant config loader** - Now fetches from local Supabase database instead of external API
2. **Updated types** - Simplified TenantConfig to match database schema
3. **Added mock configs** - Fallback for development/testing

## 🚀 How to Test

### 1. Start the Development Server

```bash
npm run dev
```

The server will run on **port 5173** (not 3000)

### 2. Access the Correct URLs

Use these URLs with the correct port:

- **Default (No Tenant):** http://localhost:5173
- **Party A:** http://party-a.localhost:5173
- **Party B:** http://party-b.localhost:5173

### 3. Update Hosts File (if not done)

Windows: `C:\Windows\System32\drivers\etc\hosts`
Add these lines:
```
127.0.0.1 party-a.localhost
127.0.0.1 party-b.localhost
```

### 4. Test Login Process

#### Party A Login:
1. Go to: http://party-a.localhost:5173
2. Click Login button
3. Enter:
   - Email: `admin@party-a.com`
   - Password: `SecurePassword123!`
4. You should be logged in as Party A admin

#### Party B Login:
1. Go to: http://party-b.localhost:5173
2. Click Login button
3. Enter:
   - Email: `admin@party-b.com`
   - Password: `SecurePassword123!`
4. You should be logged in as Party B admin

## 🔍 Troubleshooting

### If you still see "Tenant Error":

1. **Check Supabase Connection:**
   - Verify `.env` file has correct Supabase credentials
   - Make sure `VITE_MULTI_TENANT=true` is set

2. **Verify Database Setup:**
   Run this SQL to check:
   ```sql
   SELECT subdomain, name, status FROM tenants;
   ```
   You should see:
   - party-a | Party A Kerala Campaign | active
   - party-b | Party B Kerala Campaign | active

3. **Check Browser Console:**
   - Open DevTools (F12)
   - Look for any errors
   - Should NOT see "Failed to fetch" from registry.pulseofpeople.com

4. **Clear Browser Cache:**
   - Press Ctrl+Shift+Delete
   - Clear cached data
   - Restart browser

### If login fails:

1. **Verify Auth Users Exist:**
   ```sql
   SELECT email, id FROM auth.users
   WHERE email IN ('admin@party-a.com', 'admin@party-b.com');
   ```

2. **Check User Profiles:**
   ```sql
   SELECT u.email, u.role, t.subdomain, t.name as tenant_name
   FROM users u
   JOIN tenants t ON u.tenant_id = t.id
   WHERE u.email IN ('admin@party-a.com', 'admin@party-b.com');
   ```

3. **Run Link Script Again:**
   If user profiles don't exist or have wrong IDs:
   ```sql
   -- Run: supabase/FIX_LINK_AUTH_USERS.sql
   ```

## ✅ Expected Behavior

When everything works correctly:

1. **Party A (http://party-a.localhost:5173):**
   - Blue theme (#1e40af primary color)
   - Shows "Party A Kerala" branding
   - Admin can only see Party A data

2. **Party B (http://party-b.localhost:5173):**
   - Red theme (#dc2626 primary color)
   - Shows "Party B Kerala" branding
   - Admin can only see Party B data

## 🎯 Data Isolation Test

After logging in to each tenant:

1. **Create test data in Party A:**
   - Create a survey or report
   - Note the data

2. **Switch to Party B:**
   - Login as Party B admin
   - Verify you CANNOT see Party A's data
   - Create different test data

3. **Switch back to Party A:**
   - Verify you can see Party A data
   - Verify you CANNOT see Party B data

This confirms tenant isolation is working!

## 📝 Important Notes

- Port is **5173** not 3000
- Use `localhost` not `127.0.0.1` for subdomains
- Each tenant has isolated data via RLS policies
- Theme colors should change per tenant
- Clear cache if you see old data

## 🆘 If Nothing Works

Try the fallback mock mode:
1. Set `VITE_SUPABASE_URL=` (empty) in `.env`
2. Restart dev server
3. Access party-a.localhost:5173
4. Should load with mock data (no database needed)