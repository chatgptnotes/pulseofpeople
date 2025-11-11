const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');

const supabaseUrl = 'https://iwtgbseaoztjbnvworyq.supabase.co';
const supabaseServiceKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml3dGdic2Vhb3p0amJudndvcnlxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MTE2MDM5OSwiZXhwIjoyMDc2NzM2Mzk5fQ.X6j-39tynhesQLZuzPc9IXP8H9UONWcKmkKdonFBnrvIqXMO-T-PACOWxpks6fVaKoPblX0FPyI3vc3X5J1x7g';

// Note: Service key is required to run DDL operations
const supabase = createClient(supabaseUrl, supabaseServiceKey);

async function applyMigration() {
  console.log('🔧 Applying Users Table Migration...\n');

  try {
    // Read the SQL file
    const sqlPath = path.join(__dirname, 'fix-users-table.sql');
    const sql = fs.readFileSync(sqlPath, 'utf8');

    console.log('📄 Executing SQL migration...');

    // Execute the SQL
    const { data, error } = await supabase.rpc('exec_sql', { sql_query: sql });

    if (error) {
      console.log('⚠️  Direct SQL execution not available, trying alternative approach...\n');

      // Alternative: Run individual operations
      console.log('Step 1: Checking if columns exist...');

      // Try to select from users table
      const { data: testData, error: testError } = await supabase
        .from('users')
        .select('id, email')
        .limit(1);

      if (testError) {
        console.log('❌ Users table check failed:', testError.message);
        console.log('\n📋 MANUAL ACTION REQUIRED:');
        console.log('='.repeat(70));
        console.log('Please run the SQL migration manually in Supabase:');
        console.log('1. Go to: https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq/sql');
        console.log('2. Copy and paste the contents of: fix-users-table.sql');
        console.log('3. Click "Run" to execute the migration');
        console.log('='.repeat(70));
        return;
      }

      console.log('✅ Users table exists\n');

      // Insert/update superadmin user
      console.log('Step 2: Creating superadmin user...');
      const { data: userData, error: userError } = await supabase
        .from('users')
        .upsert({
          email: 'admin@tvk.com',
          full_name: 'TVK Super Admin',
          name: 'TVK Super Admin',
          role: 'superadmin',
          is_super_admin: true,
          status: 'active',
          permissions: ['*'],
          constituency: 'All',
          state: 'All States',
          updated_at: new Date().toISOString()
        }, {
          onConflict: 'email'
        });

      if (userError) {
        console.log('❌ Failed to create superadmin:', userError.message);
        console.log('\n   This is likely because the users table is missing columns.');
        console.log('   Please run fix-users-table.sql manually in Supabase SQL Editor.');
      } else {
        console.log('✅ Superadmin user created/updated successfully\n');
      }

      // Verify
      const { data: verifyData, error: verifyError } = await supabase
        .from('users')
        .select('id, email, full_name, role, is_super_admin')
        .eq('email', 'admin@tvk.com')
        .single();

      if (verifyError) {
        console.log('❌ Verification failed:', verifyError.message);
      } else if (verifyData) {
        console.log('✅ USER VERIFIED:');
        console.log('   Email:', verifyData.email);
        console.log('   Name:', verifyData.full_name);
        console.log('   Role:', verifyData.role);
        console.log('   Is Super Admin:', verifyData.is_super_admin);
      }
    } else {
      console.log('✅ Migration executed successfully!');
    }
  } catch (err) {
    console.error('❌ Migration error:', err.message);
    console.log('\n📋 MANUAL ACTION REQUIRED:');
    console.log('='.repeat(70));
    console.log('Please run the SQL migration manually in Supabase:');
    console.log('1. Go to: https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq/sql');
    console.log('2. Copy and paste the contents of: fix-users-table.sql');
    console.log('3. Click "Run" to execute the migration');
    console.log('='.repeat(70));
  }

  console.log('\n' + '='.repeat(70));
  console.log('📋 NEXT STEPS:');
  console.log('='.repeat(70));
  console.log('1. Confirm email in Supabase Auth:');
  console.log('   https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq/auth/users');
  console.log('   Find admin@tvk.com and click "..." → "Confirm Email"');
  console.log('');
  console.log('2. Then try logging in with:');
  console.log('   Email: admin@tvk.com');
  console.log('   Password: Admin@123456');
  console.log('='.repeat(70));
}

applyMigration().catch(console.error);
