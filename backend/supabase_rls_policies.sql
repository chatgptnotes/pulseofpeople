-- =====================================================
-- ROW-LEVEL SECURITY (RLS) POLICIES FOR MULTI-TENANCY
-- Pulse of People Platform
-- =====================================================
--
-- This file sets up RLS policies to ensure:
-- 1. Organization data isolation (users only see their org's data)
-- 2. Role-based access control
-- 3. User can access their own data
--
-- Apply this file: psql $DATABASE_URL -f supabase_rls_policies.sql
-- =====================================================

-- Helper function to get current user's organization_id from Supabase JWT
CREATE OR REPLACE FUNCTION auth.get_user_organization_id()
RETURNS uuid
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  org_id uuid;
BEGIN
  -- Get organization_id from user_metadata in JWT token
  SELECT (auth.jwt() -> 'user_metadata' ->> 'organization_id')::uuid INTO org_id;

  -- Fallback: Query from api_userprofile if not in token
  IF org_id IS NULL THEN
    SELECT organization_id INTO org_id
    FROM api_userprofile
    WHERE user_id::text = auth.uid()::text
    LIMIT 1;
  END IF;

  RETURN org_id;
END;
$$;

-- Helper function to get current user's role
CREATE OR REPLACE FUNCTION auth.get_user_role()
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  user_role text;
BEGIN
  -- Get role from user_metadata in JWT token
  SELECT (auth.jwt() -> 'user_metadata' ->> 'role') INTO user_role;

  -- Fallback: Query from api_userprofile if not in token
  IF user_role IS NULL THEN
    SELECT role INTO user_role
    FROM api_userprofile
    WHERE user_id::text = auth.uid()::text
    LIMIT 1;
  END IF;

  RETURN user_role;
END;
$$;

-- =====================================================
-- 1. USER PROFILE TABLE (api_userprofile)
-- =====================================================

-- Enable RLS
ALTER TABLE api_userprofile ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view profiles in their organization
CREATE POLICY "Users can view profiles in their organization"
  ON api_userprofile
  FOR SELECT
  TO authenticated
  USING (
    organization_id = auth.get_user_organization_id()
    OR
    auth.get_user_role() IN ('superadmin', 'admin')
  );

-- Policy: Users can view their own profile
CREATE POLICY "Users can view own profile"
  ON api_userprofile
  FOR SELECT
  TO authenticated
  USING (user_id::text = auth.uid()::text);

-- Policy: Users can update their own profile
CREATE POLICY "Users can update own profile"
  ON api_userprofile
  FOR UPDATE
  TO authenticated
  USING (user_id::text = auth.uid()::text)
  WITH CHECK (user_id::text = auth.uid()::text);

-- Policy: Admins can manage profiles in their organization
CREATE POLICY "Admins can manage organization profiles"
  ON api_userprofile
  FOR ALL
  TO authenticated
  USING (
    organization_id = auth.get_user_organization_id()
    AND auth.get_user_role() IN ('admin', 'superadmin')
  )
  WITH CHECK (
    organization_id = auth.get_user_organization_id()
    AND auth.get_user_role() IN ('admin', 'superadmin')
  );

-- =====================================================
-- 2. NOTIFICATIONS (api_notification)
-- =====================================================

ALTER TABLE api_notification ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view their own notifications
CREATE POLICY "Users can view own notifications"
  ON api_notification
  FOR SELECT
  TO authenticated
  USING (user_id::text = auth.uid()::text);

-- Policy: Users can update their own notifications (mark as read)
CREATE POLICY "Users can update own notifications"
  ON api_notification
  FOR UPDATE
  TO authenticated
  USING (user_id::text = auth.uid()::text)
  WITH CHECK (user_id::text = auth.uid()::text);

-- =====================================================
-- 3. CAMPAIGNS (api_campaign)
-- =====================================================

ALTER TABLE api_campaign ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view campaigns in their organization
CREATE POLICY "Users can view organization campaigns"
  ON api_campaign
  FOR SELECT
  TO authenticated
  USING (
    -- Check if campaign belongs to user's organization
    EXISTS (
      SELECT 1 FROM api_userprofile up
      WHERE up.user_id::text = auth.uid()::text
      AND up.organization_id = (
        SELECT up2.organization_id
        FROM api_userprofile up2
        WHERE up2.user_id = created_by_id
      )
    )
  );

-- Policy: Managers+ can create campaigns
CREATE POLICY "Managers can create campaigns"
  ON api_campaign
  FOR INSERT
  TO authenticated
  WITH CHECK (
    auth.get_user_role() IN ('manager', 'admin', 'superadmin')
  );

-- Policy: Creators can update their campaigns
CREATE POLICY "Users can update own campaigns"
  ON api_campaign
  FOR UPDATE
  TO authenticated
  USING (created_by_id::text = auth.uid()::text)
  WITH CHECK (created_by_id::text = auth.uid()::text);

-- =====================================================
-- 4. VOTERS (api_voter)
-- =====================================================

ALTER TABLE api_voter ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view voters in their organization
CREATE POLICY "Users can view organization voters"
  ON api_voter
  FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM api_userprofile up
      WHERE up.user_id::text = auth.uid()::text
      AND up.organization_id = (
        SELECT up2.organization_id
        FROM api_userprofile up2
        WHERE up2.user_id = created_by_id
      )
    )
  );

-- Policy: Users can create voters
CREATE POLICY "Users can create voters"
  ON api_voter
  FOR INSERT
  TO authenticated
  WITH CHECK (true);

-- =====================================================
-- 5. ALERTS (api_alert)
-- =====================================================

ALTER TABLE api_alert ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view alerts in their organization
CREATE POLICY "Users can view organization alerts"
  ON api_alert
  FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM api_userprofile up
      WHERE up.user_id::text = auth.uid()::text
      AND up.organization_id = (
        SELECT up2.organization_id
        FROM api_userprofile up2
        WHERE up2.user_id = created_by_id
      )
    )
  );

-- Policy: Admins can create alerts
CREATE POLICY "Admins can create alerts"
  ON api_alert
  FOR INSERT
  TO authenticated
  WITH CHECK (
    auth.get_user_role() IN ('admin', 'superadmin', 'manager')
  );

-- =====================================================
-- 6. EXPENSES (api_expense)
-- =====================================================

ALTER TABLE api_expense ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view expenses in their organization
CREATE POLICY "Users can view organization expenses"
  ON api_expense
  FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM api_userprofile up
      WHERE up.user_id::text = auth.uid()::text
      AND up.organization_id = (
        SELECT up2.organization_id
        FROM api_userprofile up2
        WHERE up2.user_id = created_by_id
      )
    )
  );

-- =====================================================
-- 7. AUDIT LOGS (api_auditlog)
-- =====================================================

ALTER TABLE api_auditlog ENABLE ROW LEVEL SECURITY;

-- Policy: Admins can view all audit logs in their organization
CREATE POLICY "Admins can view organization audit logs"
  ON api_auditlog
  FOR SELECT
  TO authenticated
  USING (
    auth.get_user_role() IN ('admin', 'superadmin')
  );

-- Policy: Users can view their own audit logs
CREATE POLICY "Users can view own audit logs"
  ON api_auditlog
  FOR SELECT
  TO authenticated
  USING (user_id::text = auth.uid()::text);

-- =====================================================
-- 8. BOOTH AGENTS (api_boothagent)
-- =====================================================

ALTER TABLE api_boothagent ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view booth agents in their organization
CREATE POLICY "Users can view organization booth agents"
  ON api_boothagent
  FOR SELECT
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM api_userprofile up
      WHERE up.user_id::text = auth.uid()::text
      AND up.organization_id = (
        SELECT up2.organization_id
        FROM api_userprofile up2
        WHERE up2.user_id = user_id
      )
    )
  );

-- =====================================================
-- 9. UPLOADED FILES (api_uploadedfile)
-- =====================================================

ALTER TABLE api_uploadedfile ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view their own uploaded files
CREATE POLICY "Users can view own files"
  ON api_uploadedfile
  FOR SELECT
  TO authenticated
  USING (user_id::text = auth.uid()::text);

-- Policy: Users can delete their own files
CREATE POLICY "Users can delete own files"
  ON api_uploadedfile
  FOR DELETE
  TO authenticated
  USING (user_id::text = auth.uid()::text);

-- =====================================================
-- 10. TWO-FACTOR BACKUP CODES (api_twofactorbackupcode)
-- =====================================================

ALTER TABLE api_twofactorbackupcode ENABLE ROW LEVEL SECURITY;

-- Policy: Users can manage their own 2FA codes
CREATE POLICY "Users can manage own 2FA codes"
  ON api_twofactorbackupcode
  FOR ALL
  TO authenticated
  USING (user_id::text = auth.uid()::text)
  WITH CHECK (user_id::text = auth.uid()::text);

-- =====================================================
-- GRANT PERMISSIONS
-- =====================================================

-- Grant authenticated users access to these tables
GRANT SELECT, INSERT, UPDATE, DELETE ON api_userprofile TO authenticated;
GRANT SELECT, INSERT, UPDATE ON api_notification TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON api_campaign TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON api_voter TO authenticated;
GRANT SELECT, INSERT, UPDATE ON api_alert TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON api_expense TO authenticated;
GRANT SELECT ON api_auditlog TO authenticated;
GRANT SELECT ON api_boothagent TO authenticated;
GRANT SELECT, INSERT, DELETE ON api_uploadedfile TO authenticated;
GRANT ALL ON api_twofactorbackupcode TO authenticated;

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Check which tables have RLS enabled
-- SELECT schemaname, tablename, rowsecurity
-- FROM pg_tables
-- WHERE schemaname = 'public' AND tablename LIKE 'api_%';

-- Check all policies
-- SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
-- FROM pg_policies
-- WHERE schemaname = 'public'
-- ORDER BY tablename, policyname;
