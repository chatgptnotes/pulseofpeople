# Pulse of People - Multi-Tenant Deployment Guide

## Overview

This guide walks you through deploying the Pulse of People platform in multi-tenant mode, where a single application serves multiple independent customers (tenants) with complete data isolation.

## Prerequisites

Before starting, ensure you have:

- [ ] Node.js 18+ installed
- [ ] Supabase CLI installed (`npm install -g supabase`)
- [ ] Cloudflare account with Workers enabled
- [ ] Vercel account
- [ ] Domain configured in Cloudflare
- [ ] Git repository set up

## Architecture Summary

```
Frontend (Vercel)
     ↓
Cloudflare Workers (API Gateway)
     ↓
   ┌─────┴─────┐
Tenant DB   Tenant DB   Tenant DB
(Supabase)  (Supabase)  (Supabase)
```

## Step 1: Set Up Tenant Registry

The tenant registry is a central Supabase database that stores all tenant configurations.

### 1.1 Create Registry Project

```bash
# Create a new Supabase project for the registry
supabase projects create "pulse-registry" --region ap-south-1

# Get project credentials
supabase projects list
supabase projects api-keys --project-id YOUR_PROJECT_ID
```

### 1.2 Run Registry Migration

```bash
# Navigate to project directory
cd /path/to/pulseofpeoplevoter23oct

# Set database URL
export DATABASE_URL="postgresql://postgres:[password]@db.xxx.supabase.co:5432/postgres"

# Run migration
psql "$DATABASE_URL" -f supabase/migrations/20251027_create_tenant_registry.sql
```

### 1.3 Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and set:
VITE_TENANT_REGISTRY_URL=https://xxx.supabase.co
VITE_TENANT_REGISTRY_ANON_KEY=your-anon-key
TENANT_REGISTRY_SERVICE_KEY=your-service-role-key
CREDENTIALS_ENCRYPTION_KEY=$(openssl rand -base64 32)
```

## Step 2: Deploy Cloudflare Workers (API Gateway)

### 2.1 Install Wrangler

```bash
npm install -g wrangler

# Login to Cloudflare
wrangler login
```

### 2.2 Create KV Namespace

```bash
# Production KV
wrangler kv:namespace create "TENANT_CACHE"

# Development KV
wrangler kv:namespace create "TENANT_CACHE" --preview

# Note the IDs returned and update wrangler.toml
```

### 2.3 Update Wrangler Config

Edit `cloudflare-workers/wrangler.toml`:

```toml
kv_namespaces = [
  { binding = "TENANT_CACHE", id = "YOUR_PROD_KV_ID", preview_id = "YOUR_PREVIEW_KV_ID" }
]
```

### 2.4 Set Secrets

```bash
cd cloudflare-workers

# Set registry URL
wrangler secret put TENANT_REGISTRY_URL
# Enter: https://xxx.supabase.co

# Set registry key
wrangler secret put TENANT_REGISTRY_KEY
# Enter: your-service-role-key
```

### 2.5 Deploy Worker

```bash
# Deploy to production
wrangler publish

# Note the worker URL returned (e.g., https://pulse-of-people-router.yourname.workers.dev)
```

### 2.6 Configure Custom Domain

In Cloudflare dashboard:

1. Go to Workers & Pages → pulse-of-people-router → Settings → Triggers
2. Add custom domain: `api.pulseofpeople.com`
3. Configure DNS:
   - Add CNAME: `*.pulseofpeople.com` → `pulse-of-people-router.yourname.workers.dev`
   - Add CNAME: `api.pulseofpeople.com` → `pulse-of-people-router.yourname.workers.dev`

## Step 3: Deploy Frontend (Vercel)

### 3.1 Install Vercel CLI

```bash
npm install -g vercel

# Login
vercel login
```

### 3.2 Configure Project

```bash
# In project root
vercel

# Follow prompts:
# - Link to existing project or create new
# - Set build command: npm run build
# - Set output directory: dist
# - Framework preset: Vite
```

### 3.3 Set Environment Variables

```bash
# Set multi-tenant mode
vercel env add VITE_MULTI_TENANT production
# Enter: true

# Set registry URL
vercel env add VITE_TENANT_REGISTRY_URL production
# Enter: https://xxx.supabase.co

# Set registry key (anon key, not service key!)
vercel env add VITE_TENANT_REGISTRY_ANON_KEY production
# Enter: your-anon-key

# Set API gateway URL
vercel env add VITE_API_GATEWAY_URL production
# Enter: https://api.pulseofpeople.com
```

### 3.4 Deploy

```bash
# Deploy to production
vercel --prod

# Configure custom domain in Vercel dashboard:
# - Add domain: pulseofpeople.com
# - Add wildcard: *.pulseofpeople.com
```

## Step 4: Provision First Tenant

### 4.1 Install Dependencies

```bash
npm install
```

### 4.2 Run Provisioning Script

```bash
# Provision Kerala tenant
npm run provision-tenant -- \
  --name "kerala-2026" \
  --displayName "Kerala Elections 2026" \
  --contactName "Admin Name" \
  --contactEmail "admin@kerala.gov.in" \
  --contactPhone "+91-9876543210" \
  --organizationName "Kerala Government" \
  --region "ap-south-1" \
  --state "Kerala" \
  --coverageArea "Kerala State Elections" \
  --estimatedWards 1000 \
  --expectedUsers 50 \
  --subscriptionTier "standard"
```

### 4.3 Note Credentials

The script will output:
```
Tenant URL: https://kerala-2026.pulseofpeople.com
Admin Email: admin@kerala.gov.in
Admin Password: [temporary-password]
```

**Important**: Send these credentials to the customer securely!

## Step 5: Verify Deployment

### 5.1 Test Tenant Access

1. Open browser to `https://kerala-2026.pulseofpeople.com`
2. You should see the login page
3. Log in with admin credentials
4. Verify dashboard loads

### 5.2 Test API Gateway

```bash
# Test tenant identification
curl -H "X-Tenant-ID: kerala-2026" https://api.pulseofpeople.com/rest/v1/

# Should return Supabase API response
```

### 5.3 Check Health

```bash
# Check tenant health in registry
psql "$REGISTRY_DB_URL" -c "SELECT * FROM tenant_overview WHERE slug = 'kerala-2026';"
```

## Step 6: Provision Additional Tenants

### 6.1 Automated Provisioning

```bash
# Tamil Nadu tenant
npm run provision-tenant -- \
  --name "tamilnadu-2026" \
  --displayName "Tamil Nadu Elections 2026" \
  --contactName "TN Admin" \
  --contactEmail "admin@tn.gov.in" \
  --region "ap-south-1" \
  --state "Tamil Nadu" \
  --coverageArea "Tamil Nadu State" \
  --estimatedWards 1200 \
  --expectedUsers 75 \
  --subscriptionTier "premium"

# Karnataka tenant
npm run provision-tenant -- \
  --name "karnataka-2026" \
  --displayName "Karnataka Elections 2026" \
  --contactName "KA Admin" \
  --contactEmail "admin@karnataka.gov.in" \
  --region "ap-south-1" \
  --state "Karnataka" \
  --coverageArea "Karnataka State" \
  --estimatedWards 1500 \
  --expectedUsers 100 \
  --subscriptionTier "enterprise"
```

## Step 7: Set Up Monitoring

### 7.1 Health Check Cron

Create a GitHub Action or cron job:

```yaml
# .github/workflows/health-check.yml
name: Tenant Health Check
on:
  schedule:
    - cron: '*/30 * * * *'  # Every 30 minutes

jobs:
  health-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - run: npm install
      - run: npm run check-tenant-health
        env:
          TENANT_REGISTRY_URL: ${{ secrets.TENANT_REGISTRY_URL }}
          TENANT_REGISTRY_SERVICE_KEY: ${{ secrets.TENANT_REGISTRY_SERVICE_KEY }}
```

### 7.2 Configure Alerts

Set up Slack webhook for alerts:

```bash
# In Vercel or GitHub Secrets
DEPLOYMENT_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK
```

## Step 8: Set Up CI/CD

### 8.1 Automated Deployments

```yaml
# .github/workflows/deploy.yml
name: Deploy All Tenants
on:
  push:
    branches: [main]

jobs:
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - run: npm install
      - run: npm run build
      - uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-args: '--prod'

  deploy-workers:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: cloudflare/wrangler-action@2.0.0
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          workingDirectory: 'cloudflare-workers'

  migrate-tenants:
    needs: [deploy-frontend, deploy-workers]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - run: npm install
      - run: npm run deploy-tenants
        env:
          TENANT_REGISTRY_URL: ${{ secrets.TENANT_REGISTRY_URL }}
          TENANT_REGISTRY_SERVICE_KEY: ${{ secrets.TENANT_REGISTRY_SERVICE_KEY }}
```

## Step 9: Database Migrations

### 9.1 Create New Migration

```bash
# Create migration file
echo "-- Migration description" > supabase/migrations/$(date +%Y%m%d)_description.sql

# Edit the file with your SQL changes
```

### 9.2 Deploy to All Tenants

```bash
# Dry run first
npm run deploy-tenants -- --dry-run

# Deploy for real
npm run deploy-tenants

# Deploy to specific tenant only
npm run deploy-tenants -- --tenant kerala-2026
```

## Step 10: Maintenance

### 10.1 Backup Tenants

```bash
# Backup all tenants
npm run backup-tenants

# Backups saved to: ./backups/
```

### 10.2 Monitor Usage

```sql
-- Check tenant usage
SELECT
  t.slug,
  t.name,
  SUM(tu.api_calls) as total_api_calls,
  AVG(tu.active_users) as avg_active_users,
  MAX(tu.storage_used_gb) as current_storage
FROM tenants t
JOIN tenant_usage tu ON t.id = tu.tenant_id
WHERE tu.date >= CURRENT_DATE - 7
GROUP BY t.slug, t.name
ORDER BY total_api_calls DESC;
```

### 10.3 Suspend Tenant

```bash
# Suspend for non-payment
npm run manage-tenant suspend kerala-2026 --reason "Payment overdue"

# Reactivate
npm run manage-tenant activate kerala-2026
```

## Troubleshooting

### Issue: Tenant not found

**Symptom**: Error "Tenant not found" when accessing subdomain

**Solutions**:
1. Check DNS propagation: `dig kerala-2026.pulseofpeople.com`
2. Verify tenant in registry: `psql $REGISTRY_DB -c "SELECT * FROM tenants WHERE slug='kerala-2026';"`
3. Clear Cloudflare Workers KV cache
4. Check Cloudflare Workers logs

### Issue: Database connection failed

**Symptom**: 500 error or connection timeout

**Solutions**:
1. Verify Supabase project is running
2. Check credentials in registry
3. Test connection: `psql "postgresql://..."`
4. Check firewall rules

### Issue: Slow performance

**Symptom**: High response times

**Solutions**:
1. Check Cloudflare Workers metrics
2. Verify tenant database performance in Supabase
3. Check for missing indexes
4. Review rate limiting settings

### Issue: CORS errors

**Symptom**: Browser console shows CORS errors

**Solutions**:
1. Verify Cloudflare Workers CORS headers
2. Check custom domain configuration
3. Ensure subdomain wildcards are configured

## Scaling

### Handling 100+ Tenants

1. **Cloudflare Workers**: Automatically scales, no action needed
2. **Vercel**: Upgrade to Pro plan for better performance
3. **Supabase**: Each tenant scales independently

### Regional Deployment

For global tenants:

```bash
# Deploy to multiple regions
npm run provision-tenant -- \
  --name "us-tenant" \
  --region "us-east-1" \
  --dataResidency "us"

npm run provision-tenant -- \
  --name "eu-tenant" \
  --region "eu-west-1" \
  --dataResidency "eu"
```

## Cost Estimates

### Per Tenant (Monthly)

- Supabase Pro: $25
- Storage (50GB): $6.25
- Bandwidth: ~$5
- **Total**: ~$36/tenant

### Shared Infrastructure

- Vercel Pro: $20
- Cloudflare Workers: $5
- Registry Database: $25
- Monitoring: $50
- **Total**: $100/month

### Break-even Analysis

- Revenue per tenant: $72/month (₹6,000)
- Cost per tenant: $36/month
- Margin per tenant: $36/month (50%)
- Shared infrastructure: $100/month
- **Break-even**: 3 tenants

## Security Checklist

- [ ] Registry service key is secret (never in frontend)
- [ ] Tenant credentials are encrypted in registry
- [ ] RLS policies enabled on all tables
- [ ] HTTPS enforced on all domains
- [ ] Rate limiting configured
- [ ] Backups automated
- [ ] Monitoring alerts configured
- [ ] Admin access logging enabled
- [ ] 2FA enabled for admin accounts
- [ ] Firewall rules configured

## Support

For issues or questions:
- Technical Support: tech@pulseofpeople.com
- Documentation: https://docs.pulseofpeople.com
- GitHub Issues: https://github.com/yourorg/pulse-of-people/issues

## Appendix

### Useful Commands

```bash
# List all tenants
npm run list-tenants

# Check tenant health
npm run health-check kerala-2026

# View tenant logs
npm run tenant-logs kerala-2026 --tail

# Update tenant settings
npm run update-tenant kerala-2026 --max-users 200

# Delete tenant (WARNING: irreversible!)
npm run delete-tenant kerala-2026 --confirm
```

### Environment Variables Reference

See `.env.example` for complete list of environment variables.

### Database Schema

See `supabase/DATABASE_SCHEMA.md` for detailed schema documentation.

### API Documentation

See `API_REFERENCE.md` for tenant management API documentation.

---

**Last Updated**: 2025-10-27
**Version**: 1.0
**Deployment Status**: Production Ready
