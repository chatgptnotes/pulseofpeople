-- Enable Row Level Security (RLS) policies for users table
-- This allows authenticated users to read their own user data

-- Enable RLS on users table (if not already enabled)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist (to avoid conflicts)
DROP POLICY IF EXISTS "Users can view their own data" ON users;
DROP POLICY IF EXISTS "Users can update their own data" ON users;
DROP POLICY IF EXISTS "Enable read access for authenticated users" ON users;

-- Policy 1: Allow users to read their own data based on email
CREATE POLICY "Users can view their own data"
ON users
FOR SELECT
USING (
  auth.email() = email
);

-- Policy 2: Allow users to read their own data based on auth.uid()
-- This is a fallback policy in case auth_user_id is set
CREATE POLICY "Users can view own data by auth_user_id"
ON users
FOR SELECT
USING (
  auth.uid()::text = auth_user_id::text
);

-- Policy 3: Allow users to update their own data
CREATE POLICY "Users can update their own data"
ON users
FOR UPDATE
USING (
  auth.email() = email
)
WITH CHECK (
  auth.email() = email
);

-- Policy 4: Service role can do everything (for admin operations)
-- This policy allows backend services to manage users
CREATE POLICY "Service role has full access"
ON users
FOR ALL
USING (
  current_setting('request.jwt.claims', true)::json->>'role' = 'service_role'
);

-- Grant necessary permissions
GRANT SELECT, UPDATE ON users TO authenticated;
GRANT ALL ON users TO service_role;

-- Add helpful comment
COMMENT ON TABLE users IS 'User profiles with RLS enabled. Authenticated users can read/update their own data.';
