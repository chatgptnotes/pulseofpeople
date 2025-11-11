# Pulse of People - Multi-Tenant Cloud Architecture

## Executive Summary

This document outlines the architecture for deploying Pulse of People as a **multi-tenant SaaS platform** where:
- Single codebase serves multiple customers (tenants)
- Automatic upgrades for all tenants
- Complete data isolation between tenants
- Scalable for 100+ concurrent campaigns
- DPDP Act compliant

## Multi-Tenancy Approaches

### Option 1: Database Per Tenant (Recommended) ⭐

**Architecture:**
```
                        ┌─────────────────┐
                        │  Load Balancer  │
                        └────────┬────────┘
                                 │
                        ┌────────▼────────┐
                        │   API Gateway   │
                        │  (Tenant Router)│
                        └────────┬────────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
        ┌───────▼──────┐  ┌─────▼──────┐  ┌─────▼──────┐
        │ Supabase DB  │  │ Supabase DB│  │ Supabase DB│
        │  Tenant A    │  │  Tenant B  │  │  Tenant C  │
        │  (Kerala)    │  │ (Tamil Nadu)│  │ (Karnataka)│
        └──────────────┘  └────────────┘  └────────────┘

        ┌────────────────────────────────────────────────┐
        │     Shared Frontend (React App on Vercel)     │
        │           Single Codebase for All             │
        └────────────────────────────────────────────────┘
```

**Pros:**
- ✅ Complete data isolation (best security)
- ✅ Easy tenant-specific backups
- ✅ Independent scaling per tenant
- ✅ Regulatory compliance (data residency)
- ✅ Easy to migrate or export tenant data
- ✅ No cross-tenant query risks
- ✅ Tenant-specific customizations possible

**Cons:**
- ❌ Higher infrastructure cost
- ❌ More databases to manage
- ❌ Schema migrations need to run on all DBs

**Best For:**
- High-value customers (₹6,000/month justifies it)
- Political campaigns (data sensitivity)
- Compliance requirements (DPDP Act)
- Need for tenant-specific customizations

**Cost Estimate:**
- Supabase Free tier: 2 projects
- Supabase Pro: $25/project/month
- For 10 tenants: $250/month + shared infrastructure

---

### Option 2: Schema Per Tenant

**Architecture:**
```
        ┌─────────────────────────────────────┐
        │     Single Supabase Database        │
        ├─────────────────────────────────────┤
        │  Schema: tenant_kerala_2026         │
        │    ├─ users                         │
        │    ├─ sentiment_data                │
        │    └─ social_posts...               │
        ├─────────────────────────────────────┤
        │  Schema: tenant_tamilnadu_2026      │
        │    ├─ users                         │
        │    ├─ sentiment_data                │
        │    └─ social_posts...               │
        ├─────────────────────────────────────┤
        │  Schema: public (shared metadata)   │
        │    ├─ tenants                       │
        │    └─ subscriptions                 │
        └─────────────────────────────────────┘
```

**Pros:**
- ✅ Good data isolation
- ✅ Single database to manage
- ✅ Lower cost than database per tenant
- ✅ Shared connection pool
- ✅ Cross-tenant analytics possible (if needed)

**Cons:**
- ❌ All tenants share same database resources
- ❌ One database failure affects all tenants
- ❌ Complex backup/restore per tenant
- ❌ Schema migrations more complex
- ❌ Supabase doesn't natively support this well

**Best For:**
- Medium-scale deployments (10-50 tenants)
- Cost-conscious deployments
- Tenants with similar usage patterns

---

### Option 3: Row-Level Multi-Tenancy (Not Recommended)

**Architecture:**
```
        ┌─────────────────────────────────────┐
        │     Single Supabase Database        │
        │           Single Schema             │
        ├─────────────────────────────────────┤
        │  users (tenant_id, ...)             │
        │  sentiment_data (tenant_id, ...)    │
        │  social_posts (tenant_id, ...)      │
        │  ...                                │
        └─────────────────────────────────────┘
```

**Pros:**
- ✅ Simplest to implement
- ✅ Lowest infrastructure cost
- ✅ Easy cross-tenant analytics
- ✅ Single migration path

**Cons:**
- ❌ ⚠️ Highest risk of data leaks
- ❌ Complex RLS policies
- ❌ Performance issues with large datasets
- ❌ Difficult to ensure complete data isolation
- ❌ Regulatory compliance challenges
- ❌ Cannot scale individual tenants

**Best For:**
- Low-security applications
- Early MVP testing
- Non-political/non-sensitive data

---

## Recommended Architecture: Database Per Tenant

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                          │
│  Pulse of People Frontend (React + TypeScript + Vite)      │
│  Deployed on: Vercel (Global CDN)                          │
│  URL: app.pulseofpeople.com                                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTPS
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   API GATEWAY LAYER                         │
│  Technology: Cloudflare Workers / AWS Lambda                │
│  Functions:                                                 │
│    - Tenant identification (subdomain/header/token)         │
│    - Routing to correct database                           │
│    - Authentication & authorization                         │
│    - Rate limiting per tenant                              │
│    - API versioning                                        │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
┌────────▼────────┐ ┌───▼──────────┐ ┌──▼──────────────┐
│  Supabase       │ │  Supabase    │ │  Supabase       │
│  Project 1      │ │  Project 2   │ │  Project N      │
│  (Kerala 2026)  │ │  (TN 2026)   │ │  (KA 2026)      │
│                 │ │              │ │                 │
│  - PostgreSQL   │ │  - PostgreSQL│ │  - PostgreSQL   │
│  - Auth         │ │  - Auth      │ │  - Auth         │
│  - Storage      │ │  - Storage   │ │  - Storage      │
│  - Realtime     │ │  - Realtime  │ │  - Realtime     │
└─────────────────┘ └──────────────┘ └─────────────────┘
```

### Component Details

#### 1. Frontend (Single Codebase)

**Technology Stack:**
- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS
- Deployed on Vercel

**Tenant Identification:**
```typescript
// Option A: Subdomain-based
// kerala.pulseofpeople.com → Tenant: kerala-2026
// tamilnadu.pulseofpeople.com → Tenant: tamilnadu-2026

// Option B: Path-based
// app.pulseofpeople.com/kerala → Tenant: kerala-2026

// Option C: Header-based (mobile apps)
// X-Tenant-ID: kerala-2026
```

**Configuration:**
```typescript
// src/config/tenant.ts
interface TenantConfig {
  id: string;
  name: string;
  supabaseUrl: string;
  supabaseAnonKey: string;
  region: string;
  features: string[];
  branding: {
    logo: string;
    primaryColor: string;
    name: string;
  };
}

// Loaded dynamically based on tenant identification
const tenantConfig = await loadTenantConfig(tenantId);
```

#### 2. API Gateway / Tenant Router

**Technology Options:**

**Option A: Cloudflare Workers** (Recommended)
```javascript
// cloudflare-worker.js
export default {
  async fetch(request) {
    const url = new URL(request.url);
    const tenantId = extractTenantId(url.hostname);

    // Get tenant configuration
    const tenant = await getTenantConfig(tenantId);

    if (!tenant) {
      return new Response('Tenant not found', { status: 404 });
    }

    // Route to correct Supabase instance
    const supabaseUrl = tenant.supabaseUrl;
    const proxyUrl = url.pathname.replace('/api', supabaseUrl);

    // Forward request with tenant context
    const response = await fetch(proxyUrl, {
      method: request.method,
      headers: {
        ...request.headers,
        'X-Tenant-ID': tenantId
      },
      body: request.body
    });

    return response;
  }
};
```

**Option B: AWS API Gateway + Lambda**
```javascript
// lambda-router.js
exports.handler = async (event) => {
  const tenantId = event.headers['x-tenant-id'] ||
                   extractFromSubdomain(event.headers.host);

  const tenant = await dynamodb.get({
    TableName: 'tenants',
    Key: { id: tenantId }
  });

  // Route to appropriate Supabase instance
  return routeToSupabase(tenant.supabaseUrl, event);
};
```

**Option C: Next.js Middleware** (if using Next.js)
```typescript
// middleware.ts
import { NextResponse } from 'next/server';

export function middleware(request: Request) {
  const url = new URL(request.url);
  const tenantId = extractTenantId(url.hostname);

  // Add tenant context to headers
  const response = NextResponse.next();
  response.headers.set('X-Tenant-ID', tenantId);

  return response;
}
```

#### 3. Tenant Registry (Centralized)

**Metadata Database:**
```sql
-- Central registry (could be Supabase, DynamoDB, or PostgreSQL)
CREATE TABLE tenants (
    id UUID PRIMARY KEY,
    slug TEXT UNIQUE NOT NULL,  -- kerala-2026, tamilnadu-2026
    name TEXT NOT NULL,
    supabase_url TEXT NOT NULL,
    supabase_project_id TEXT NOT NULL,
    supabase_anon_key TEXT NOT NULL,

    -- Subscription details
    subscription_status TEXT,  -- trial, active, suspended, cancelled
    subscription_tier TEXT,    -- basic, premium, enterprise
    subscription_start TIMESTAMPTZ,
    subscription_end TIMESTAMPTZ,

    -- Billing
    monthly_fee DECIMAL(10, 2),
    billing_email TEXT,

    -- Features
    enabled_features JSONB,

    -- Configuration
    region TEXT,  -- ap-south-1, us-east-1
    data_residency TEXT,  -- india, singapore

    -- Branding
    branding JSONB,  -- { logo, colors, name }
    custom_domain TEXT,  -- Optional

    -- Limits
    max_users INTEGER DEFAULT 100,
    max_wards INTEGER DEFAULT 1000,
    max_storage_gb INTEGER DEFAULT 50,

    -- Status
    status TEXT DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tenant database credentials (encrypted)
CREATE TABLE tenant_credentials (
    tenant_id UUID REFERENCES tenants(id),
    supabase_service_key TEXT NOT NULL,  -- Encrypted
    database_url TEXT NOT NULL,           -- Encrypted
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Usage tracking
CREATE TABLE tenant_usage (
    tenant_id UUID REFERENCES tenants(id),
    date DATE,
    api_calls BIGINT DEFAULT 0,
    storage_used_gb DECIMAL(10, 2),
    active_users INTEGER,
    sentiment_records_created BIGINT,
    PRIMARY KEY (tenant_id, date)
);
```

#### 4. Supabase Configuration Per Tenant

**Project Setup Script:**
```bash
#!/bin/bash
# setup-new-tenant.sh

TENANT_NAME=$1
REGION=$2  # ap-south-1, us-east-1

# Create new Supabase project
supabase projects create "$TENANT_NAME" --region "$REGION"

# Get project credentials
PROJECT_ID=$(supabase projects list | grep "$TENANT_NAME" | awk '{print $1}')
SUPABASE_URL="https://$PROJECT_ID.supabase.co"
ANON_KEY=$(supabase projects api-keys --project-id "$PROJECT_ID" | grep anon | awk '{print $2}')

# Run schema migration
psql "$DATABASE_URL" -f supabase/migrations/20251027_create_all_tables.sql

# Configure RLS policies
psql "$DATABASE_URL" -f supabase/setup/rls_policies.sql

# Enable realtime
supabase realtime enable --project-id "$PROJECT_ID"

# Configure storage buckets
supabase storage create field-reports --project-id "$PROJECT_ID"
supabase storage create media-uploads --project-id "$PROJECT_ID"

# Store in tenant registry
psql $REGISTRY_DB_URL <<EOF
INSERT INTO tenants (slug, name, supabase_url, supabase_project_id, supabase_anon_key, region)
VALUES ('$TENANT_NAME', '$TENANT_NAME', '$SUPABASE_URL', '$PROJECT_ID', '$ANON_KEY', '$REGION');
EOF

echo "Tenant $TENANT_NAME created successfully!"
echo "URL: https://$TENANT_NAME.pulseofpeople.com"
```

### Tenant Lifecycle Management

#### Onboarding New Tenant

```typescript
// src/admin/tenant-manager.ts

interface TenantOnboardingRequest {
  name: string;
  contactEmail: string;
  region: string;
  subscriptionTier: 'basic' | 'premium' | 'enterprise';
  coverageArea: string;
  estimatedWards: number;
}

async function onboardTenant(request: TenantOnboardingRequest) {
  // 1. Create Supabase project
  const supabaseProject = await createSupabaseProject({
    name: request.name,
    region: request.region,
    plan: 'pro'  // All tenants on Pro plan
  });

  // 2. Run database migrations
  await runMigrations(supabaseProject.databaseUrl);

  // 3. Create initial admin user
  await createAdminUser(supabaseProject, {
    email: request.contactEmail,
    role: 'admin'
  });

  // 4. Configure storage buckets
  await setupStorageBuckets(supabaseProject);

  // 5. Register tenant in central registry
  const tenant = await registerTenant({
    slug: slugify(request.name),
    name: request.name,
    supabaseUrl: supabaseProject.url,
    supabaseProjectId: supabaseProject.id,
    supabaseAnonKey: supabaseProject.anonKey,
    region: request.region,
    subscriptionTier: request.subscriptionTier
  });

  // 6. Send welcome email
  await sendWelcomeEmail(tenant);

  // 7. Create subdomain
  await createSubdomain(`${tenant.slug}.pulseofpeople.com`);

  return tenant;
}
```

#### Updating All Tenants (Code Deployment)

```typescript
// src/admin/tenant-updater.ts

async function deployToAllTenants() {
  const tenants = await getAllActiveTenants();

  for (const tenant of tenants) {
    try {
      console.log(`Deploying to ${tenant.name}...`);

      // 1. Run database migrations (if any)
      if (hasNewMigrations()) {
        await runMigrations(tenant.databaseUrl);
      }

      // 2. Update RLS policies (if changed)
      if (rlsPoliciesChanged()) {
        await updateRLSPolicies(tenant.databaseUrl);
      }

      // 3. Update storage rules (if changed)
      if (storageRulesChanged()) {
        await updateStorageRules(tenant.supabaseProjectId);
      }

      // 4. Clear caches
      await clearTenantCache(tenant.id);

      console.log(`✓ ${tenant.name} updated successfully`);

    } catch (error) {
      console.error(`✗ Failed to update ${tenant.name}:`, error);
      // Log error but continue with other tenants
      await logDeploymentError(tenant.id, error);
    }
  }

  // Frontend is auto-deployed via Vercel (single deployment for all)
  console.log('Frontend deployed to Vercel - all tenants updated');
}
```

#### Tenant Suspension/Deletion

```typescript
// src/admin/tenant-lifecycle.ts

async function suspendTenant(tenantId: string, reason: string) {
  // 1. Update status in registry
  await updateTenantStatus(tenantId, 'suspended');

  // 2. Disable authentication (users can't log in)
  await disableSupabaseAuth(tenantId);

  // 3. Send notification to tenant
  await notifyTenantSuspension(tenantId, reason);

  // 4. Log action
  await auditLog.record({
    action: 'tenant_suspended',
    tenantId,
    reason,
    timestamp: new Date()
  });
}

async function deleteTenant(tenantId: string) {
  // 1. Export tenant data (compliance)
  const exportPath = await exportTenantData(tenantId);

  // 2. Delete Supabase project
  const tenant = await getTenant(tenantId);
  await deleteSupabaseProject(tenant.supabaseProjectId);

  // 3. Remove from registry
  await deleteTenantFromRegistry(tenantId);

  // 4. Remove subdomain
  await deleteSubdomain(tenant.slug);

  // 5. Archive export
  await archiveExport(exportPath);

  // 6. Send confirmation
  await sendDeletionConfirmation(tenant.contactEmail);
}
```

### Data Isolation & Security

#### 1. Authentication Flow

```typescript
// src/lib/auth.ts

class TenantAwareAuth {
  private supabaseClient: SupabaseClient;

  constructor(tenantId: string) {
    const tenant = getTenantConfig(tenantId);
    this.supabaseClient = createClient(
      tenant.supabaseUrl,
      tenant.supabaseAnonKey
    );
  }

  async signIn(email: string, password: string) {
    // User can only access their tenant's database
    const { data, error } = await this.supabaseClient.auth.signInWithPassword({
      email,
      password
    });

    if (error) throw error;

    // Store tenant context in session
    sessionStorage.setItem('tenantId', this.tenantId);

    return data;
  }

  async signOut() {
    await this.supabaseClient.auth.signOut();
    sessionStorage.removeItem('tenantId');
  }
}
```

#### 2. API Request Flow

```
User Request
    ↓
[Extract Tenant ID from subdomain/header/token]
    ↓
[Validate tenant exists and is active]
    ↓
[Verify user belongs to tenant]
    ↓
[Route to tenant's Supabase instance]
    ↓
[Execute query with tenant's database]
    ↓
[Return response]
```

#### 3. Cross-Tenant Protection

```typescript
// Middleware to prevent cross-tenant access
export function tenantIsolationMiddleware(req, res, next) {
  const userTenantId = req.user.tenantId;  // From JWT
  const requestTenantId = req.headers['x-tenant-id'];

  if (userTenantId !== requestTenantId) {
    return res.status(403).json({
      error: 'Access denied: Cross-tenant access not allowed'
    });
  }

  next();
}
```

### Deployment & CI/CD

#### 1. Frontend Deployment (Vercel)

```yaml
# vercel.json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ],
  "env": {
    "VITE_API_GATEWAY_URL": "https://api.pulseofpeople.com",
    "VITE_TENANT_REGISTRY_URL": "https://registry.pulseofpeople.com"
  }
}
```

#### 2. Database Migration Strategy

```bash
#!/bin/bash
# migrate-all-tenants.sh

# Get all active tenant database URLs
TENANTS=$(psql $REGISTRY_DB_URL -t -c "SELECT database_url FROM tenant_credentials tc JOIN tenants t ON tc.tenant_id = t.id WHERE t.status = 'active'")

# Run migration on each tenant
for DB_URL in $TENANTS; do
  echo "Migrating $DB_URL..."
  psql "$DB_URL" -f "supabase/migrations/$(date +%Y%m%d)_new_migration.sql"

  if [ $? -eq 0 ]; then
    echo "✓ Migration successful"
  else
    echo "✗ Migration failed - manual intervention required"
    # Send alert to ops team
    curl -X POST $SLACK_WEBHOOK_URL -d "{\"text\": \"Migration failed for $DB_URL\"}"
  fi
done
```

#### 3. Automated Deployment Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy to All Tenants

on:
  push:
    branches: [main]

jobs:
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Vercel
        run: vercel --prod
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}

  migrate-databases:
    runs-on: ubuntu-latest
    needs: deploy-frontend
    steps:
      - uses: actions/checkout@v2
      - name: Run migrations on all tenants
        run: ./scripts/migrate-all-tenants.sh
        env:
          REGISTRY_DB_URL: ${{ secrets.REGISTRY_DB_URL }}

  notify:
    runs-on: ubuntu-latest
    needs: [deploy-frontend, migrate-databases]
    steps:
      - name: Send notification
        run: |
          curl -X POST ${{ secrets.SLACK_WEBHOOK }} \
            -d '{"text": "Deployment successful - all tenants updated"}'
```

### Monitoring & Observability

#### 1. Per-Tenant Metrics

```typescript
// Collect metrics per tenant
interface TenantMetrics {
  tenantId: string;
  timestamp: Date;

  // Performance
  apiResponseTime: number;
  databaseQueryTime: number;
  errorRate: number;

  // Usage
  activeUsers: number;
  apiCallsPerHour: number;
  storageUsedGB: number;
  sentimentRecordsCreated: number;

  // Health
  uptime: number;
  healthScore: number;
}

// Send to monitoring service (Datadog, New Relic, etc.)
```

#### 2. Alerting

```typescript
// Alert conditions per tenant
const alertRules = [
  {
    condition: 'errorRate > 5%',
    action: 'notify_tenant_admin',
    severity: 'warning'
  },
  {
    condition: 'storageUsed > 90% of limit',
    action: 'notify_tenant_admin',
    severity: 'critical'
  },
  {
    condition: 'apiResponseTime > 2000ms',
    action: 'investigate',
    severity: 'warning'
  }
];
```

### Cost Optimization

#### 1. Supabase Pricing

**Per Tenant Cost:**
- Supabase Pro: $25/month
- Additional storage: $0.125/GB/month
- Additional bandwidth: $0.09/GB

**Revenue vs Cost:**
- Subscription: ₹6,000/month (~$72)
- Supabase cost: $25/month
- Infrastructure: $10/month
- **Gross margin: ~$37/tenant (51%)**

#### 2. Shared Infrastructure Cost

- Vercel Frontend: $20/month (unlimited traffic)
- Cloudflare Workers: $5/month (10M requests)
- Tenant Registry DB: $25/month
- Monitoring: $50/month
- **Total shared: $100/month**

**Break-even:** ~3 tenants
**Target:** 50+ tenants

### Scaling Strategy

#### Phase 1: 1-10 Tenants (Current)
- Manual tenant provisioning
- Single region (India)
- Basic monitoring

#### Phase 2: 10-50 Tenants (6 months)
- Automated tenant provisioning
- Multi-region support
- Advanced monitoring
- Tier-based features

#### Phase 3: 50-500 Tenants (12-24 months)
- Self-service sign-up
- Global CDN
- Premium tiers with custom features
- White-label options
- Reseller program

### Compliance & Data Residency

#### DPDP Act Compliance

```typescript
// Ensure data stays in India for Indian tenants
const tenantConfig = {
  region: 'ap-south-1',  // Mumbai
  dataResidency: 'india',
  encryptionAtRest: true,
  encryptionInTransit: true,
  retentionPolicy: '365 days',
  rightToDelete: true,
  consentManagement: true
};
```

### Comparison Summary

| Feature | Database Per Tenant | Schema Per Tenant | Row-Level |
|---------|-------------------|------------------|-----------|
| Data Isolation | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| Security | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| Scalability | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Cost | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Complexity | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| Supabase Support | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Recommendation** | **YES** ✓ | Maybe | NO |

## Implementation Roadmap

### Week 1-2: Infrastructure Setup
- [ ] Set up tenant registry database
- [ ] Create tenant provisioning scripts
- [ ] Configure API gateway (Cloudflare Workers)
- [ ] Set up monitoring

### Week 3-4: Multi-Tenant Core
- [ ] Implement tenant identification logic
- [ ] Update frontend for tenant-aware routing
- [ ] Create admin dashboard for tenant management
- [ ] Implement automated migrations

### Week 5-6: Testing & Deployment
- [ ] Create 3 test tenants
- [ ] Test data isolation
- [ ] Performance testing
- [ ] Security audit
- [ ] Deploy to production

### Week 7-8: Operations & Documentation
- [ ] Create runbooks
- [ ] Set up alerts
- [ ] Train support team
- [ ] Onboard first real tenants

## Conclusion

**Recommended Approach:** Database Per Tenant (Option 1)

**Rationale:**
1. Best security and data isolation (critical for political data)
2. Compliance with DPDP Act
3. Each tenant can scale independently
4. Easy to backup/restore individual tenants
5. Cost is justified by ₹6,000/month revenue
6. Natural fit with Supabase's project model

**Next Steps:**
1. Set up tenant registry database
2. Create tenant provisioning automation
3. Deploy API gateway layer
4. Test with 2-3 pilot tenants
5. Scale to production

