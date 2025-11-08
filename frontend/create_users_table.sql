-- =====================================================
-- Create Users Table in Supabase
-- =====================================================
-- Run this SQL in your Supabase SQL Editor
-- Go to: https://app.supabase.com/project/YOUR_PROJECT/sql/new

-- Create users table if it doesn't exist
CREATE TABLE IF NOT EXISTS public.users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  role TEXT DEFAULT 'user',
  avatar TEXT,
  permissions TEXT[] DEFAULT ARRAY['view_dashboard', 'view_analytics', 'view_reports'],
  ward TEXT,
  constituency TEXT,
  is_super_admin BOOLEAN DEFAULT FALSE,
  organization_id UUID,
  tenant_id UUID,
  status TEXT DEFAULT 'active',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- Create policy to allow users to read their own data
CREATE POLICY "Users can view own data" ON public.users
  FOR SELECT
  USING (auth.uid()::TEXT = id::TEXT OR auth.email() = email);

-- Create policy for insert (for new user registration)
CREATE POLICY "Enable insert for authenticated users" ON public.users
  FOR INSERT
  WITH CHECK (auth.uid() IS NOT NULL);

-- Create policy for update
CREATE POLICY "Users can update own data" ON public.users
  FOR UPDATE
  USING (auth.uid()::TEXT = id::TEXT OR auth.email() = email);

-- Create function to automatically create user profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.users (id, email, name, role, permissions)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'name', split_part(NEW.email, '@', 1)),
    COALESCE(NEW.raw_user_meta_data->>'role', 'user'),
    CASE
      WHEN NEW.raw_user_meta_data->>'role' = 'admin' THEN
        ARRAY['view_all', 'edit_all', 'manage_users', 'export_data', 'verify_submissions', 'edit_settings', 'manage_billing']
      WHEN NEW.raw_user_meta_data->>'role' = 'super_admin' THEN
        ARRAY['view_all', 'edit_all', 'manage_users', 'export_data', 'verify_submissions', 'manage_organizations', 'view_all_data', 'manage_system_settings', 'view_audit_logs', 'manage_billing']
      ELSE
        ARRAY['view_dashboard', 'view_analytics', 'view_reports', 'view_surveys']
    END
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger to automatically create user profile on signup
CREATE OR REPLACE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();

-- Insert test users (you can modify these as needed)
-- First, create auth users in Supabase Dashboard > Authentication > Users
-- Then run this to create corresponding profiles:

-- Example: Insert admin user (after creating in Auth)
-- INSERT INTO public.users (email, name, role, permissions, is_super_admin)
-- VALUES (
--   'admin@bettroi.com',
--   'Admin User',
--   'admin',
--   ARRAY['view_all', 'edit_all', 'manage_users', 'export_data', 'verify_submissions', 'edit_settings', 'manage_billing'],
--   false
-- ) ON CONFLICT (email) DO NOTHING;

-- Grant access to authenticated users
GRANT ALL ON public.users TO authenticated;
GRANT ALL ON public.users TO service_role;