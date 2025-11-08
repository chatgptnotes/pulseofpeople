# Multi-Tenant Setup Guide - Quick Integration

## Overview
This guide will help you set up multi-tenant functionality for two political parties (Party A and Party B) in 3-5 days.

## Prerequisites
- [x] Supabase project with credentials
- [x] Access to Supabase SQL Editor
- [x] Admin access to DNS settings
- [x] Vercel account for deployment

## Day 1: Core Integration (Completed ✅)

### 1. Environment Configuration ✅
- Updated `.env` file with multi-tenant settings
- Set `VITE_MULTI_TENANT=true`
- Configured production URL: `https://pulseofpeople.com`

### 2. Application Integration ✅
- Integrated TenantProvider into `App.tsx`
- Tenant context now wraps entire application
- Ready for tenant-specific data isolation

### 3. Local Testing Setup ✅
- Created testing documentation in `LOCAL_MULTI_TENANT_TESTING.md`
- Test page available at `src/test-multi-tenant.html`
- Hosts file configuration for local subdomains

## Day 2: Database Setup (Current Task)

### Step 1: Run Multi-Tenant Migration

1. Go to Supabase SQL Editor: https://app.supabase.com/project/iwtgbseaoztjbnvworyq/sql/new

2. Copy and run the migration from:
   ```
   supabase/migrations/20251029_single_db_multi_tenant.sql
   ```

3. Verify migration success by checking for new tables:
   - organizations
   - tenants
   - tenant_provisioning_audit
   - tenant_operations_audit

### Step 2: Create Auth Users

1. Go to Supabase Authentication > Users
2. Create Party A Admin:
   - Email: `admin@party-a.com`
   - Password: `SecurePassword123!`
   - ✅ Auto Confirm Email

3. Create Party B Admin:
   - Email: `admin@party-b.com`
   - Password: `SecurePassword123!`
   - ✅ Auto Confirm Email

### Step 3: Create Tenant Data

1. Run the tenant creation script:
   ```
   supabase/create_tenants_party_a_b.sql
   ```

2. This will create:
   - Organizations for both parties
   - Tenants with subdomains (party-a, party-b)
   - Admin user profiles
   - Sample constituency data

### Step 4: Verify Setup

Run these queries to verify:
```sql
-- Check organizations
SELECT * FROM organizations;

-- Check tenants
SELECT slug, subdomain, status FROM tenants;

-- Check users
SELECT email, role, tenant_id FROM users
WHERE email IN ('admin@party-a.com', 'admin@party-b.com');
```

## Day 3: DNS & Deployment

### Step 1: Configure DNS

1. Add wildcard DNS record in your domain provider:
   ```
   Type: A
   Name: *
   Value: [Vercel IP - 76.76.21.21]
   TTL: 3600
   ```

2. Wait for DNS propagation (5-30 minutes)

### Step 2: Deploy to Vercel

1. Push code to GitHub:
   ```bash
   git add .
   git commit -m "Enable multi-tenant support for Party A and Party B"
   git push origin main
   ```

2. Import project to Vercel:
   - Go to https://vercel.com/new
   - Import GitHub repository
   - Configure environment variables from `.env`

3. Add domain configuration in Vercel:
   - Add `pulseofpeople.com`
   - Add `*.pulseofpeople.com` (wildcard)

### Step 3: Test Production Subdomains

1. Access Party A: https://party-a.pulseofpeople.com
2. Access Party B: https://party-b.pulseofpeople.com
3. Verify SSL certificates are working

## Day 4: Testing & Validation

### Cross-Tenant Isolation Testing

1. **Test Party A:**
   - Login: admin@party-a.com
   - Create test data (survey, report, etc.)
   - Note the data created

2. **Test Party B:**
   - Login: admin@party-b.com
   - Verify Party A's data is NOT visible
   - Create different test data
   - Verify isolation

3. **Super Admin Test:**
   - Login: superadmin@pulseofpeople.com
   - Verify can see both tenants
   - Verify can switch between tenants

### Performance Testing

1. Load test both subdomains simultaneously
2. Verify response times < 2 seconds
3. Check database query performance

## Day 5: Production Launch

### Final Checklist

- [ ] Both subdomains accessible
- [ ] SSL working on all domains
- [ ] Admin users can login
- [ ] Data isolation verified
- [ ] Performance acceptable
- [ ] Backup configured

### Handoff Documentation

Create and share:
1. Admin credentials for each party
2. Subdomain URLs
3. Quick start guide
4. Support contact info

## Quick Commands Reference

### Local Development
```bash
# Start dev server
npm run dev

# Access local tenants
# http://party-a.localhost:5173
# http://party-b.localhost:5173
```

### Database Verification
```sql
-- Check tenant isolation
SELECT current_setting('app.current_tenant_id', true);

-- List all tenants
SELECT slug, subdomain, status FROM tenants;

-- Check user's tenant
SELECT email, tenant_id FROM users WHERE email = current_user;
```

### Troubleshooting

#### Tenant Not Detected
1. Check VITE_MULTI_TENANT=true in .env
2. Verify TenantProvider in App.tsx
3. Check browser console for errors

#### Login Issues
1. Verify user exists in auth.users
2. Check user has profile in public.users
3. Ensure tenant_id is set correctly

#### Data Not Isolated
1. Check RLS policies are enabled
2. Verify tenant_id on all records
3. Test get_user_tenant_id() function

## Support

For issues or questions:
1. Check browser console for errors
2. Review Supabase logs
3. Verify environment variables
4. Test with incognito mode

## Next Steps After Launch

1. **Week 1:**
   - Monitor usage and performance
   - Gather user feedback
   - Fix any critical issues

2. **Week 2:**
   - Add custom branding for each party
   - Implement email notifications
   - Enable advanced features

3. **Month 1:**
   - Add more tenants as needed
   - Optimize performance
   - Implement billing integration