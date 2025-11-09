-- Enable Row Level Security (RLS) policies for users table
-- This allows authenticated users to read their own user data

-- Enable RLS on users table (if not already enabled)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist (to avoid conflicts)
DROP POLICY IF EXISTS "Users can view their own data" ON users;
DROP POLICY IF EXISTS "Users can update their own data" ON users;
DROP POLICY IF EXISTS "Users can view own data by auth_user_id" ON users;
DROP POLICY IF EXISTS "Service role has full access" ON users;
DROP POLICY IF EXISTS "Enable read access for authenticated users" ON users;

-- Policy 1: Allow authenticated users to read their own data based on email
-- Using JWT claims to get the authenticated user's email
CREATE POLICY "Users can view their own data"
ON users
FOR SELECT
TO authenticated
USING (
  email = (SELECT auth.jwt()->>'email')
);

-- Policy 2: Allow users to read their own data based on auth_user_id
-- This is a fallback policy in case auth_user_id is set
CREATE POLICY "Users can view own data by auth_user_id"
ON users
FOR SELECT
TO authenticated
USING (
  auth_user_id::text = (SELECT auth.jwt()->>'sub')
);

-- Policy 3: Allow authenticated users to update their own data
CREATE POLICY "Users can update their own data"
ON users
FOR UPDATE
TO authenticated
USING (
  email = (SELECT auth.jwt()->>'email')
)
WITH CHECK (
  email = (SELECT auth.jwt()->>'email')
);

-- Policy 4: Service role and anon can read all users (for admin operations)
-- This is needed because the frontend uses the anon key
CREATE POLICY "Service role and anon have read access"
ON users
FOR SELECT
TO anon, service_role
USING (true);

-- Policy 5: Service role can do everything (for admin operations)
CREATE POLICY "Service role has full access"
ON users
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- Grant necessary permissions
GRANT SELECT, UPDATE ON users TO authenticated;
GRANT SELECT ON users TO anon;
GRANT ALL ON users TO service_role;

-- Add helpful comment
COMMENT ON TABLE users IS 'User profiles with RLS enabled. Authenticated users can read/update their own data.';
