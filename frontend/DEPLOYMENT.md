# Production Deployment Guide
## Pulse of People - Multi-Tenant SaaS Platform

This guide covers the complete deployment process from development to production.

---

## Table of Contents
1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Database Setup](#database-setup)
3. [Environment Configuration](#environment-configuration)
4. [Vercel Deployment](#vercel-deployment)
5. [Domain & DNS Configuration](#domain--dns-configuration)
6. [Post-Deployment Verification](#post-deployment-verification)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Rollback Procedures](#rollback-procedures)

---

## Pre-Deployment Checklist

### Code Quality
- [ ] All TypeScript errors resolved (`npm run build`)
- [ ] ESLint warnings addressed (`npm run lint`)
- [ ] No console.errors in production code
- [ ] All Material Icons properly imported (no emoji usage)
- [ ] Version footer displays correctly on all pages

### Security
- [ ] No secrets or API keys committed to git
- [ ] Environment variables properly configured
- [ ] RLS policies tested for all tables
- [ ] CORS configuration set for production domains
- [ ] Rate limiting enabled for all API endpoints
- [ ] Error logging configured (Sentry/custom endpoint)

### Features
- [ ] Super Admin Dashboard functional
- [ ] Admin Management operational
- [ ] Tenant Provisioning wizard working
- [ ] User invitation flow tested
- [ ] Payment gateway integration tested (sandbox mode)
- [ ] Notification system configured
- [ ] Data export functionality verified
- [ ] Analytics dashboard loading data
- [ ] Onboarding tours functional
- [ ] Feature flags system operational

### Performance
- [ ] Lazy loading implemented for routes
- [ ] Images optimized
- [ ] Bundle size < 500KB (check with `npm run build`)
- [ ] Database indexes created
- [ ] Lighthouse score > 90

---

## Database Setup

### 1. Supabase Project Setup

```bash
# Login to Supabase CLI
supabase login

# Link to your project
supabase link --project-ref YOUR_PROJECT_REF

# Check connection
supabase status
```

### 2. Run Migrations

```bash
# Run all migrations in order
psql $DATABASE_URL -f supabase/migrations/20251029_single_db_multi_tenant.sql
psql $DATABASE_URL -f supabase/migrations/20251029_optimize_indexes.sql

# Verify migrations
psql $DATABASE_URL -c "SELECT * FROM pg_tables WHERE schemaname = 'public';"
```

### 3. Set Up RLS Policies

```sql
-- Enable RLS on all tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.voters ENABLE ROW LEVEL SECURITY;
-- ... (repeat for all tables)

-- Verify RLS is enabled
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public';
```

### 4. Create Initial Super Admin

```sql
-- Create super admin user
INSERT INTO public.users (id, email, name, role, status)
VALUES (
  'your-auth-user-id',
  'admin@yourcompany.com',
  'Super Admin',
  'super_admin',
  'active'
);
```

### 5. Optimize Database

```sql
-- Run ANALYZE to update statistics
ANALYZE;

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC
LIMIT 20;
```

---

## Environment Configuration

### 1. Required Environment Variables

Create `.env.production` file:

```bash
# Supabase
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key

# Application
VITE_APP_URL=https://yourapp.com
VITE_APP_NAME=Pulse of People

# Multi-tenancy
VITE_TENANT_MODE=subdomain
VITE_DEFAULT_TENANT=demo

# Payment Gateways
VITE_RAZORPAY_KEY=your-razorpay-key
VITE_STRIPE_PUBLISHABLE_KEY=your-stripe-key

# Email (Optional)
VITE_EMAIL_PROVIDER=supabase
VITE_SMTP_HOST=smtp.gmail.com
VITE_SMTP_PORT=587
VITE_SMTP_USER=your-email@gmail.com
VITE_SMTP_PASSWORD=your-app-password

# SMS (Optional)
VITE_SMS_PROVIDER=twilio
VITE_SMS_ACCOUNT_SID=your-twilio-sid
VITE_SMS_AUTH_TOKEN=your-twilio-token
VITE_SMS_FROM=+911234567890

# Error Logging (Optional)
VITE_SENTRY_DSN=your-sentry-dsn
VITE_ERROR_LOGGING_ENDPOINT=https://api.yourapp.com/errors

# Feature Flags
VITE_ENVIRONMENT=production
```

### 2. Supabase Dashboard Configuration

#### Auth Settings
- Navigate to Authentication > Settings
- Configure redirect URLs:
  - `https://yourapp.com/auth/callback`
  - `https://*.yourapp.com/auth/callback` (wildcard for subdomains)
- Set JWT expiry: 3600 seconds (1 hour)
- Enable email confirmations

#### Database
- Go to Database > Extensions
- Enable required extensions:
  - `uuid-ossp`
  - `pg_trgm` (for fuzzy search)
  - `pg_stat_statements` (for monitoring)

#### Storage (if using file uploads)
- Create buckets:
  - `avatars` (public)
  - `documents` (private)
  - `exports` (private)
- Set RLS policies for each bucket

---

## Vercel Deployment

### 1. Install Vercel CLI

```bash
npm install -g vercel
vercel login
```

### 2. Link Project

```bash
cd /Users/murali/1backup/Pulseofpeoplevoter23oct
vercel link
```

### 3. Set Environment Variables

```bash
# Set all environment variables
vercel env add VITE_SUPABASE_URL production
vercel env add VITE_SUPABASE_ANON_KEY production
# ... (repeat for all variables)

# Or import from .env file
vercel env pull .env.production
```

### 4. Deploy

```bash
# Preview deployment
vercel

# Production deployment
vercel --prod

# With specific configuration
vercel --prod --build-env NODE_OPTIONS="--max_old_space_size=4096"
```

### 5. Vercel Configuration

Create `vercel.json`:

```json
{
  "version": 2,
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        },
        {
          "key": "Referrer-Policy",
          "value": "strict-origin-when-cross-origin"
        }
      ]
    }
  ]
}
```

---

## Domain & DNS Configuration

### 1. Main Domain Setup

In your DNS provider (Cloudflare, Namecheap, etc.):

```dns
# A Record
yourapp.com → Vercel IP (76.76.19.0)

# CNAME (alternative)
yourapp.com → cname.vercel-dns.com
```

### 2. Wildcard Subdomain for Tenants

```dns
# Wildcard CNAME
*.yourapp.com → cname.vercel-dns.com
```

### 3. Vercel Domain Configuration

```bash
# Add domain to Vercel project
vercel domains add yourapp.com
vercel domains add "*.yourapp.com"

# Verify DNS propagation
dig yourapp.com
dig kerala.yourapp.com
```

### 4. SSL Certificate

Vercel automatically provisions SSL certificates. Verify:
- Visit https://yourapp.com
- Check certificate validity
- Test subdomain: https://test.yourapp.com

---

## Post-Deployment Verification

### 1. Smoke Tests

```bash
# Main domain
curl -I https://yourapp.com
# Expected: 200 OK

# Subdomain routing
curl -I https://test.yourapp.com
# Expected: 200 OK

# API health check
curl https://yourapp.com/api/health
```

### 2. Feature Verification Checklist

- [ ] Landing page loads correctly
- [ ] Login/signup flows working
- [ ] Super Admin dashboard accessible
- [ ] Tenant creation wizard functional
- [ ] Subdomain routing works (test.yourapp.com)
- [ ] User invitation emails sent
- [ ] Payment gateway test transaction successful
- [ ] Data export downloads properly
- [ ] Analytics dashboard shows data
- [ ] Onboarding tour starts for new users
- [ ] Error boundaries catch and display errors
- [ ] Loading states display during async operations
- [ ] Form validation works on all forms

### 3. Security Verification

```bash
# Check security headers
curl -I https://yourapp.com | grep -E "X-Frame-Options|X-Content-Type-Options|X-XSS-Protection"

# Test RLS policies
# Log in as different users and verify data isolation

# Test rate limiting
# Make 100 rapid requests and verify throttling
```

### 4. Performance Testing

```bash
# Run Lighthouse audit
npx lighthouse https://yourapp.com --view

# Check bundle size
npm run build
ls -lh dist/assets/

# Test page load times
curl -o /dev/null -s -w '%{time_total}\n' https://yourapp.com
```

---

## Monitoring & Maintenance

### 1. Set Up Monitoring

#### Vercel Analytics
- Enable in Vercel Dashboard > Analytics
- Monitor:
  - Page views
  - User sessions
  - Performance metrics
  - Error rates

#### Supabase Dashboard
- Monitor in Database > Query Performance
- Check:
  - Active connections
  - Slow queries
  - RLS policy performance
  - Storage usage

#### Error Tracking (Sentry - Optional)
```bash
npm install @sentry/react @sentry/tracing

# Initialize in src/main.tsx
```

### 2. Database Maintenance

```sql
-- Weekly maintenance script
-- Run every Sunday at 2 AM

-- Update statistics
ANALYZE;

-- Reindex heavily used tables
REINDEX TABLE public.voters;
REINDEX TABLE public.activities;
REINDEX TABLE public.audit_logs;

-- Vacuum to reclaim space
VACUUM ANALYZE;

-- Check for bloat
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;
```

### 3. Backup Strategy

#### Supabase Automated Backups
- Daily backups (included in paid plans)
- Access via Supabase Dashboard > Database > Backups

#### Manual Backup
```bash
# Full database backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Specific tables only
pg_dump $DATABASE_URL -t public.tenants -t public.users > critical_backup.sql

# Restore from backup
psql $DATABASE_URL < backup_20251029.sql
```

### 4. Monitoring Alerts

Set up alerts for:
- [ ] Error rate > 1%
- [ ] Response time > 3 seconds
- [ ] Database connections > 80%
- [ ] Disk usage > 80%
- [ ] Failed payment transactions
- [ ] RLS policy violations

---

## Rollback Procedures

### 1. Vercel Rollback

```bash
# List recent deployments
vercel ls

# Rollback to specific deployment
vercel rollback DEPLOYMENT_URL

# Promote deployment to production
vercel promote DEPLOYMENT_URL --prod
```

### 2. Database Rollback

```bash
# Restore from backup
psql $DATABASE_URL < backup_20251029.sql

# Rollback specific migration
psql $DATABASE_URL -c "DROP TABLE IF EXISTS new_table_name;"
```

### 3. Emergency Procedures

#### Complete Outage
1. Check Vercel status page
2. Check Supabase status page
3. Review recent deployments
4. Rollback to last known good state
5. Notify users via status page

#### Data Corruption
1. Stop all writes (enable maintenance mode)
2. Assess damage with read-only queries
3. Restore from backup
4. Verify data integrity
5. Resume operations

---

## Post-Launch Checklist

### Day 1
- [ ] Monitor error logs constantly
- [ ] Check all critical user flows
- [ ] Verify payment processing
- [ ] Monitor database performance
- [ ] Check email/SMS delivery

### Week 1
- [ ] Review user feedback
- [ ] Analyze usage patterns
- [ ] Optimize slow queries
- [ ] Fine-tune rate limits
- [ ] Update documentation

### Month 1
- [ ] Performance optimization
- [ ] Security audit
- [ ] Cost optimization
- [ ] Feature prioritization based on usage
- [ ] Scale planning

---

## Support & Resources

- **Documentation**: https://docs.yourapp.com
- **Status Page**: https://status.yourapp.com
- **Support Email**: support@yourapp.com
- **Emergency Hotline**: +91-XXXX-XXXX-XX

---

## Version History

- **v1.0** (2025-10-28): Initial release
- **v1.1** (2025-10-29): Multi-tenant architecture
- **v1.2** (Current): Production-ready with all features

---

**Last Updated**: 2025-10-29
**Maintained By**: Development Team
**Review Frequency**: Monthly
