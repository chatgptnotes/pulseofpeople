-- Enable RLS on users table
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Drop all existing policies
DROP POLICY IF EXISTS "Users can view their own data" ON users;
DROP POLICY IF EXISTS "Users can update their own data" ON users;
DROP POLICY IF EXISTS "Users can view own data by auth_user_id" ON users;
DROP POLICY IF EXISTS "Service role has full access" ON users;
DROP POLICY IF EXISTS "Enable read access for authenticated users" ON users;
DROP POLICY IF EXISTS "Service role and anon have read access" ON users;

-- Policy 1: Allow anon role to read all users (needed for login)
CREATE POLICY "Anon can read all users"
ON users
FOR SELECT
TO anon
USING (true);

-- Policy 2: Allow authenticated users to read their own data
CREATE POLICY "Authenticated users can read own data"
ON users
FOR SELECT
TO authenticated
USING (email = (SELECT auth.jwt()->>'email'));

-- Policy 3: Allow authenticated users to update their own data
CREATE POLICY "Authenticated users can update own data"
ON users
FOR UPDATE
TO authenticated
USING (email = (SELECT auth.jwt()->>'email'))
WITH CHECK (email = (SELECT auth.jwt()->>'email'));

-- Policy 4: Service role has full access
CREATE POLICY "Service role full access"
ON users
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- Grant permissions
GRANT SELECT ON users TO anon;
GRANT SELECT, UPDATE ON users TO authenticated;
GRANT ALL ON users TO service_role;
