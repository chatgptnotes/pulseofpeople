-- Enable RLS on users table
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Drop existing policies
DROP POLICY IF EXISTS "Users can view their own data" ON users;
DROP POLICY IF EXISTS "Users can update their own data" ON users;
DROP POLICY IF EXISTS "Users can view own data by auth_user_id" ON users;
DROP POLICY IF EXISTS "Service role has full access" ON users;
DROP POLICY IF EXISTS "Enable read access for authenticated users" ON users;
DROP POLICY IF EXISTS "Service role and anon have read access" ON users;

-- Allow anon and service_role to read all users
CREATE POLICY "Service role and anon have read access"
ON users
FOR SELECT
TO anon, service_role
USING (true);

-- Allow authenticated users to read their own data by email
CREATE POLICY "Users can view their own data"
ON users
FOR SELECT
TO authenticated
USING (email = (SELECT auth.jwt()->>'email'));

-- Allow authenticated users to read their own data by auth_user_id
CREATE POLICY "Users can view own data by auth_user_id"
ON users
FOR SELECT
TO authenticated
USING (auth_user_id::text = (SELECT auth.jwt()->>'sub'));

-- Allow authenticated users to update their own data
CREATE POLICY "Users can update their own data"
ON users
FOR UPDATE
TO authenticated
USING (email = (SELECT auth.jwt()->>'email'))
WITH CHECK (email = (SELECT auth.jwt()->>'email'));

-- Allow service role full access
CREATE POLICY "Service role has full access"
ON users
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- Grant permissions
GRANT SELECT, UPDATE ON users TO authenticated;
GRANT SELECT ON users TO anon;
GRANT ALL ON users TO service_role;
