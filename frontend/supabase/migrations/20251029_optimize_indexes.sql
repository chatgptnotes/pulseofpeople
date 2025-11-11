-- Optimize Database Indexes for RLS Query Performance
-- This migration creates strategic indexes to improve query performance
-- especially for Row Level Security (RLS) queries in a multi-tenant environment

-- ============================================================================
-- TENANT-BASED INDEXES
-- These indexes optimize the most common query pattern: filtering by tenant_id
-- ============================================================================

-- Users table - tenant_id is heavily used in RLS policies
CREATE INDEX IF NOT EXISTS idx_users_tenant_id ON public.users(tenant_id);
CREATE INDEX IF NOT EXISTS idx_users_tenant_email ON public.users(tenant_id, email);
CREATE INDEX IF NOT EXISTS idx_users_tenant_status ON public.users(tenant_id, status) WHERE status IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_users_created_at ON public.users(created_at DESC);

-- Voters table - primary data table, needs extensive indexing
CREATE INDEX IF NOT EXISTS idx_voters_tenant_id ON public.voters(tenant_id);
CREATE INDEX IF NOT EXISTS idx_voters_tenant_phone ON public.voters(tenant_id, phone);
CREATE INDEX IF NOT EXISTS idx_voters_tenant_email ON public.voters(tenant_id, email);
CREATE INDEX IF NOT EXISTS idx_voters_tenant_booth ON public.voters(tenant_id, booth_no);
CREATE INDEX IF NOT EXISTS idx_voters_tenant_created ON public.voters(tenant_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_voters_search_name ON public.voters USING gin(to_tsvector('english', name));

-- Campaigns table
CREATE INDEX IF NOT EXISTS idx_campaigns_tenant_id ON public.campaigns(tenant_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_tenant_status ON public.campaigns(tenant_id, status);
CREATE INDEX IF NOT EXISTS idx_campaigns_start_date ON public.campaigns(start_date DESC);

-- Activities/Audit logs - frequently queried with time ranges
CREATE INDEX IF NOT EXISTS idx_activities_tenant_id ON public.activities(tenant_id);
CREATE INDEX IF NOT EXISTS idx_activities_tenant_user ON public.activities(tenant_id, user_id);
CREATE INDEX IF NOT EXISTS idx_activities_tenant_created ON public.activities(tenant_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_activities_created_at ON public.activities(created_at DESC);

-- Audit logs
CREATE INDEX IF NOT EXISTS idx_audit_logs_tenant_id ON public.audit_logs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON public.audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON public.audit_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_tenant_created ON public.audit_logs(tenant_id, created_at DESC);

-- ============================================================================
-- ANALYTICS TABLES
-- ============================================================================

-- Analytics events - high volume, need efficient querying
CREATE INDEX IF NOT EXISTS idx_analytics_events_tenant ON public.analytics_events(tenant_id);
CREATE INDEX IF NOT EXISTS idx_analytics_events_tenant_created ON public.analytics_events(tenant_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analytics_events_name ON public.analytics_events(event_name);

-- Page views - for analytics dashboard
CREATE INDEX IF NOT EXISTS idx_page_views_tenant ON public.page_views(tenant_id);
CREATE INDEX IF NOT EXISTS idx_page_views_tenant_created ON public.page_views(tenant_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_page_views_user ON public.page_views(user_id);

-- ============================================================================
-- ADMIN & TENANT MANAGEMENT
-- ============================================================================

-- Tenants table - core multi-tenancy table
CREATE INDEX IF NOT EXISTS idx_tenants_status ON public.tenants(status);
CREATE INDEX IF NOT EXISTS idx_tenants_subdomain ON public.tenants(subdomain);
CREATE INDEX IF NOT EXISTS idx_tenants_subscription_status ON public.tenants(subscription_status);
CREATE INDEX IF NOT EXISTS idx_tenants_created_at ON public.tenants(created_at DESC);

-- Organizations
CREATE INDEX IF NOT EXISTS idx_organizations_status ON public.organizations(status);
CREATE INDEX IF NOT EXISTS idx_organizations_admin_id ON public.organizations(admin_id);

-- Admin-tenant relationships
CREATE INDEX IF NOT EXISTS idx_admin_tenants_admin ON public.admin_tenants(admin_id);
CREATE INDEX IF NOT EXISTS idx_admin_tenants_tenant ON public.admin_tenants(tenant_id);
CREATE INDEX IF NOT EXISTS idx_admin_tenants_both ON public.admin_tenants(admin_id, tenant_id);

-- User-tenant relationships
CREATE INDEX IF NOT EXISTS idx_user_tenants_user ON public.user_tenants(user_id);
CREATE INDEX IF NOT EXISTS idx_user_tenants_tenant ON public.user_tenants(tenant_id);
CREATE INDEX IF NOT EXISTS idx_user_tenants_both ON public.user_tenants(user_id, tenant_id);

-- ============================================================================
-- BILLING & SUBSCRIPTIONS
-- ============================================================================

-- Invoices
CREATE INDEX IF NOT EXISTS idx_invoices_tenant_id ON public.invoices(tenant_id);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON public.invoices(status);
CREATE INDEX IF NOT EXISTS idx_invoices_due_date ON public.invoices(due_date);
CREATE INDEX IF NOT EXISTS idx_invoices_tenant_status ON public.invoices(tenant_id, status);

-- Payments
CREATE INDEX IF NOT EXISTS idx_payments_tenant_id ON public.payments(tenant_id);
CREATE INDEX IF NOT EXISTS idx_payments_invoice_id ON public.payments(invoice_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON public.payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_created_at ON public.payments(created_at DESC);

-- Subscriptions
CREATE INDEX IF NOT EXISTS idx_subscriptions_tenant_id ON public.subscriptions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON public.subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_renewal_date ON public.subscriptions(next_renewal_date);

-- ============================================================================
-- NOTIFICATIONS
-- ============================================================================

-- Notifications table
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON public.notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_tenant_id ON public.notifications(tenant_id) WHERE tenant_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_notifications_status ON public.notifications(status);
CREATE INDEX IF NOT EXISTS idx_notifications_user_status ON public.notifications(user_id, status);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON public.notifications(created_at DESC);

-- Export jobs
CREATE INDEX IF NOT EXISTS idx_export_jobs_tenant ON public.export_jobs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_export_jobs_user ON public.export_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_export_jobs_status ON public.export_jobs(status);
CREATE INDEX IF NOT EXISTS idx_export_jobs_tenant_created ON public.export_jobs(tenant_id, created_at DESC);

-- ============================================================================
-- COMPOSITE INDEXES FOR COMMON QUERY PATTERNS
-- ============================================================================

-- User authentication queries
CREATE INDEX IF NOT EXISTS idx_users_email_active ON public.users(email) WHERE status = 'active';

-- Active campaigns with date range
CREATE INDEX IF NOT EXISTS idx_campaigns_active_dates ON public.campaigns(tenant_id, status, start_date, end_date)
  WHERE status = 'active';

-- Recent activities for dashboard
CREATE INDEX IF NOT EXISTS idx_activities_recent ON public.activities(tenant_id, created_at DESC, type);

-- Unread notifications
CREATE INDEX IF NOT EXISTS idx_notifications_unread ON public.notifications(user_id, created_at DESC)
  WHERE status = 'unread';

-- Overdue invoices
CREATE INDEX IF NOT EXISTS idx_invoices_overdue ON public.invoices(tenant_id, due_date)
  WHERE status IN ('pending', 'overdue');

-- ============================================================================
-- PARTIAL INDEXES FOR BETTER PERFORMANCE
-- Partial indexes are smaller and faster for specific query patterns
-- ============================================================================

-- Active users only
CREATE INDEX IF NOT EXISTS idx_users_active ON public.users(tenant_id, email)
  WHERE status = 'active';

-- Failed login attempts (for security monitoring)
CREATE INDEX IF NOT EXISTS idx_auth_failures ON public.audit_logs(user_id, created_at DESC)
  WHERE action LIKE '%login_failed%';

-- Pending export jobs (actively monitored)
CREATE INDEX IF NOT EXISTS idx_export_jobs_pending ON public.export_jobs(tenant_id, created_at DESC)
  WHERE status IN ('pending', 'processing');

-- ============================================================================
-- FOREIGN KEY INDEXES
-- Ensure all foreign keys have indexes for join performance
-- ============================================================================

-- These are created automatically by PostgreSQL for primary keys,
-- but we ensure they exist for foreign key columns

CREATE INDEX IF NOT EXISTS idx_fk_voters_tenant ON public.voters(tenant_id);
CREATE INDEX IF NOT EXISTS idx_fk_campaigns_tenant ON public.campaigns(tenant_id);
CREATE INDEX IF NOT EXISTS idx_fk_activities_tenant ON public.activities(tenant_id);
CREATE INDEX IF NOT EXISTS idx_fk_activities_user ON public.activities(user_id);

-- ============================================================================
-- TEXT SEARCH INDEXES
-- For full-text search capabilities
-- ============================================================================

-- Voter name search
CREATE INDEX IF NOT EXISTS idx_voters_name_search ON public.voters
  USING gin(to_tsvector('english', name));

-- Voter address search
CREATE INDEX IF NOT EXISTS idx_voters_address_search ON public.voters
  USING gin(to_tsvector('english', address)) WHERE address IS NOT NULL;

-- Campaign name search
CREATE INDEX IF NOT EXISTS idx_campaigns_name_search ON public.campaigns
  USING gin(to_tsvector('english', name));

-- ============================================================================
-- ANALYZE TABLES
-- Update table statistics for query planner
-- ============================================================================

ANALYZE public.users;
ANALYZE public.tenants;
ANALYZE public.voters;
ANALYZE public.campaigns;
ANALYZE public.activities;
ANALYZE public.audit_logs;
ANALYZE public.notifications;
ANALYZE public.invoices;
ANALYZE public.payments;
ANALYZE public.subscriptions;

-- ============================================================================
-- INDEX MAINTENANCE RECOMMENDATIONS
-- ============================================================================

-- Run these commands periodically (weekly or monthly) to maintain index health:
-- REINDEX TABLE public.voters;
-- REINDEX TABLE public.activities;
-- REINDEX TABLE public.audit_logs;
-- VACUUM ANALYZE;

-- Monitor index usage with:
-- SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
-- FROM pg_stat_user_indexes
-- WHERE schemaname = 'public'
-- ORDER BY idx_scan ASC;

-- Check for unused indexes:
-- SELECT schemaname, tablename, indexname
-- FROM pg_stat_user_indexes
-- WHERE idx_scan = 0 AND schemaname = 'public';

COMMENT ON INDEX idx_users_tenant_id IS 'Primary tenant filtering index for RLS policies';
COMMENT ON INDEX idx_voters_tenant_id IS 'Primary tenant filtering index for voter queries';
COMMENT ON INDEX idx_activities_tenant_created IS 'Composite index for recent activity queries';
COMMENT ON INDEX idx_notifications_unread IS 'Partial index for unread notifications dashboard';
