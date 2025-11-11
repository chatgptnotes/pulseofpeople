# Claude Code Mission File

## PROJECT GOAL
Build a voter sentiment analysis platform with Super Admin and Admin role hierarchy. **Single-tenant mode** - accessible via localhost or main domain (no subdomain routing). All authentication, user roles, and features remain fully functional.

## TECH STACK & TARGETS
- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS
- **Backend**: Supabase (PostgreSQL + Auth + RLS)
- **Deployment**: Vercel (Frontend) + Supabase Cloud (Database)
- **Tenant Mode**: Single-tenant (VITE_MULTI_TENANT=false) - No subdomain routing
- **Database**: Single database with Row Level Security (RLS) for data isolation
- **Icons**: Google Material Icons only (no emojis)

## REPO/ENV
- **Repo Path**: `/Users/murali/1backup/Pulseofpeoplevoter23oct`
- **Package Manager**: npm
- **OS**: macOS (Darwin 24.6.0)
- **Node Version**: >=18.0.0

## ARCHITECTURE DECISIONS
1. **Single-Tenant Mode**: Multi-tenant subdomain routing disabled (tvk.pulseofpeople.com, bjp.pulseofpeople.com removed)
2. **Three-Tier Role Hierarchy** (Preserved):
   - Super Admin (Platform Owner) → Creates Admins
   - Admin (Client Organization Owner) → Manages organization
   - Users (Project Team) → Manages campaigns
3. **Database**: Single Supabase database with RLS policies for data isolation
4. **Authentication**: Full auth system with role-based access control (RBAC) intact

## DELIVERABLES IN PROGRESS

### Phase 1: Database Schema (COMPLETED)
- ✅ Single-DB multi-tenancy migration created
- ✅ tenant_id added to all domain tables
- ✅ Comprehensive RLS policies for isolation
- ✅ Admin-tenant relationship tables
- ✅ Audit logging infrastructure

### Phase 2: Super Admin Dashboard (IN PROGRESS)
- Platform overview with stats
- Admin management interface
- Tenant registry with health monitoring
- Billing & subscriptions dashboard
- Platform settings

### Phase 3: Tenant Provisioning
- Automated tenant creation wizard
- Subdomain configuration
- Initial data setup
- Welcome email automation

### Phase 4: Admin Dashboard
- Organization overview
- Tenant management for their org
- User management within org
- Organization settings

### Phase 5: User Management
- User list with advanced filtering
- Invitation workflow
- Permission management UI
- Audit log viewer

### Phase 6: Subdomain Routing
- DNS wildcard configuration
- Frontend tenant detection
- Tenant context provider
- API middleware for tenant validation

### Phase 7: Navigation Updates
- Role-based menu items
- Tenant switcher
- Unauthorized page
- Permission-based UI elements

### Phase 8: Testing & Deployment
- End-to-end testing
- Security audit
- Performance optimization
- Production deployment

## ASSUMPTIONS & DECISIONS
1. Using existing RBAC system (already 85% complete)
2. Supabase handles authentication, using custom RLS for multi-tenancy
3. Tenant provisioning automated but manual DNS verification initially
4. Mock payment gateway (integrate Razorpay/Stripe later)
5. Email via Supabase (configure SMTP later)
6. Development testing on localhost:5173
7. Material Icons from @mui/icons-material (already installed)

## VERSION TRACKING
- **Initial Version**: 1.0 (2025-10-28)
- **Current Version**: 1.1 (2025-10-29) - Multi-tenant schema migration
- **Version Increment**: Auto-increment on each git push
- **Display Location**: Footer of all pages (gray text, small print)

## ENVIRONMENT VARIABLES
```env
# Supabase (Main Database)
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key

# Application
VITE_APP_URL=https://yourapp.com
VITE_APP_NAME=Pulse of People

# Multi-tenancy (DISABLED - Single Tenant Mode)
VITE_MULTI_TENANT=false
VITE_TENANT_MODE=subdomain
VITE_DEFAULT_TENANT=demo

# Optional: External Services (use mocks if not configured)
VITE_EMAIL_SERVICE=supabase
VITE_DNS_PROVIDER=cloudflare
VITE_PAYMENT_GATEWAY=mock
```

## RUN COMMANDS
```bash
# Development
npm run dev              # Start dev server (port 5173)

# Build
npm run build            # Production build

# Testing
npm run test             # Run tests
npm run test:coverage    # Coverage report

# Linting
npm run lint             # Check code
npm run lint:fix         # Auto-fix issues

# Database
psql $DATABASE_URL -f supabase/migrations/20251029_single_db_multi_tenant.sql
```

## QUALITY CHECKLIST
- [x] TypeScript strict mode enabled
- [x] ESLint configured
- [x] No secrets in code
- [x] RLS policies for data isolation
- [x] Audit logging for admin actions
- [ ] Tests for core logic (in progress)
- [ ] Error boundaries in React
- [ ] Loading states for async operations
- [ ] Input validation on all forms

## BLOCKED ITEMS (Using Mocks)
1. **DNS Automation**: Manual subdomain configuration initially, will integrate Cloudflare API
2. **Email Service**: Using Supabase auth emails, custom SMTP later
3. **Payment Gateway**: Mock implementation, Razorpay integration planned
4. **SSL Certificates**: Using Vercel's automatic SSL

## NEXT ACTIONS
1. Build Super Admin Dashboard components
2. Implement tenant provisioning wizard
3. Create subdomain routing logic
4. Add version footer to all pages
5. Replace all emojis with Material Icons
6. Test multi-tenant isolation
7. Deploy to Vercel production

## TESTING STRATEGY
- **Unit Tests**: Permission functions, utility helpers
- **Integration Tests**: API calls, RLS policies
- **E2E Tests**: User flows (create admin → create tenant → login)
- **Manual Testing**: Cross-tenant isolation, subdomain routing
- **Security Testing**: SQL injection, XSS, CSRF

## OPERATIONS NOTES
- **Backups**: Supabase handles automated daily backups
- **Monitoring**: Built-in Supabase monitoring + custom metrics
- **Logs**: Console logs + audit tables in database
- **Env Rotation**: Update Supabase keys via dashboard
- **Scaling**: RLS queries optimized with proper indexes

## STATUS
🟢 **ACTIVE DEVELOPMENT** - Single Tenant Mode (Subdomain routing disabled)
**Last Updated**: 2025-11-06
**Progress**: Multi-tenant subdomain routing removed. All auth & features preserved.
