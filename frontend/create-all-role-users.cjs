const { createClient } = require('@supabase/supabase-js');

// Supabase configuration
const supabaseUrl = 'https://iwtgbseaoztjbnvworyq.supabase.co';

// IMPORTANT: Get your Service Role Key from Supabase Dashboard
// Go to: https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq/settings/api
// Copy the "service_role" key (NOT the anon key)
// NEVER commit this key to Git!
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY || 'YOUR_SERVICE_ROLE_KEY_HERE';

if (supabaseServiceKey === 'YOUR_SERVICE_ROLE_KEY_HERE') {
  console.error('\n❌ ERROR: Service Role Key not configured!\n');
  console.log('📝 To fix this:\n');
  console.log('1. Go to: https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq/settings/api');
  console.log('2. Copy the "service_role" secret key');
  console.log('3. Run this script with the key:\n');
  console.log('   SUPABASE_SERVICE_ROLE_KEY=your_key_here node create-all-role-users.cjs\n');
  console.log('OR create a .env.local file with:');
  console.log('   SUPABASE_SERVICE_ROLE_KEY=your_key_here\n');
  process.exit(1);
}

// Create admin client with service role key (can bypass RLS)
const supabase = createClient(supabaseUrl, supabaseServiceKey, {
  auth: {
    autoRefreshToken: false,
    persistSession: false
  }
});

/**
 * Role Hierarchy Test Users
 * superadmin > admin > manager > analyst > user
 */
const TEST_USERS = [
  {
    email: 'superadmin@pulseofpeople.com',
    password: 'SuperAdmin@123',
    full_name: 'TVK Super Admin',
    role: 'superadmin',
    is_super_admin: true,
    constituency: 'All Organizations',
    state: 'All States',
    permissions: ['*'],
  },
  {
    email: 'admin@tvk.com',
    password: 'Admin@123',
    full_name: 'TVK Admin',
    role: 'admin',
    is_super_admin: false,
    constituency: 'All',
    permissions: ['view_all', 'edit_all', 'manage_users', 'export_data'],
  },
  {
    email: 'manager@tvk.com',
    password: 'Manager@123',
    full_name: 'TVK Manager',
    role: 'manager',
    is_super_admin: false,
    constituency: 'Chennai District',
    permissions: ['view_users', 'create_users', 'view_analytics', 'export_data'],
  },
  {
    email: 'analyst@tvk.com',
    password: 'Analyst@123',
    full_name: 'TVK Analyst',
    role: 'analyst',
    is_super_admin: false,
    constituency: 'Perambur Constituency',
    permissions: ['view_analytics', 'verify_submissions', 'export_data'],
  },
  {
    email: 'user@tvk.com',
    password: 'User@123',
    full_name: 'TVK User',
    role: 'user',
    is_super_admin: false,
    constituency: 'Booth B-456',
    ward: 'Ward 15',
    permissions: ['view_dashboard', 'submit_data'],
  },
];

async function createAllRoleUsers() {
  console.log('\n' + '='.repeat(80));
  console.log('🚀 CREATING ROLE HIERARCHY TEST USERS');
  console.log('='.repeat(80));
  console.log('\nRole Hierarchy: superadmin → admin → manager → analyst → user\n');

  const results = [];

  for (const user of TEST_USERS) {
    console.log(`\n📝 Processing: ${user.email} (${user.role})`);
    console.log('-'.repeat(60));

    try {
      // Step 1: Create user in Supabase Auth
      console.log('Step 1/3: Creating auth user...');
      const { data: authData, error: authError } = await supabase.auth.admin.createUser({
        email: user.email,
        password: user.password,
        email_confirm: true, // Auto-confirm email
        user_metadata: {
          full_name: user.full_name,
          role: user.role
        }
      });

      if (authError && !authError.message.includes('already registered')) {
        throw authError;
      }

      let userId;
      if (authData && authData.user) {
        userId = authData.user.id;
        console.log(`✅ Auth user created: ${userId}`);
      } else {
        // User already exists, get their ID
        const { data: existingUsers } = await supabase.auth.admin.listUsers();
        const existingUser = existingUsers.users.find(u => u.email === user.email);
        if (existingUser) {
          userId = existingUser.id;
          console.log(`✅ Auth user already exists: ${userId}`);
        } else {
          throw new Error('Could not find user ID');
        }
      }

      // Step 2: Create/Update user in database
      console.log('Step 2/3: Creating database record...');
      const { data: dbData, error: dbError } = await supabase
        .from('users')
        .upsert({
          id: userId,
          email: user.email,
          full_name: user.full_name,
          role: user.role,
          is_super_admin: user.is_super_admin || false,
          constituency: user.constituency,
          state: user.state || null,
          ward: user.ward || null,
          permissions: user.permissions,
          status: 'active',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        }, {
          onConflict: 'id'
        })
        .select()
        .single();

      if (dbError) {
        console.log(`⚠️  Database warning: ${dbError.message}`);
      } else {
        console.log(`✅ Database record created/updated`);
      }

      // Step 3: Verify the user
      console.log('Step 3/3: Verifying user...');
      const { data: verifyData, error: verifyError } = await supabase
        .from('users')
        .select('*')
        .eq('email', user.email)
        .single();

      if (verifyError) {
        throw verifyError;
      }

      console.log(`✅ Verified: ${verifyData.full_name} | Role: ${verifyData.role}`);

      results.push({
        success: true,
        email: user.email,
        role: user.role,
        userId: userId,
      });

    } catch (error) {
      console.error(`❌ Failed: ${error.message}`);
      results.push({
        success: false,
        email: user.email,
        role: user.role,
        error: error.message,
      });
    }
  }

  // Print summary
  console.log('\n' + '='.repeat(80));
  console.log('📊 SUMMARY');
  console.log('='.repeat(80));

  const successful = results.filter(r => r.success);
  const failed = results.filter(r => !r.success);

  console.log(`\n✅ Successful: ${successful.length}/${TEST_USERS.length}`);
  if (successful.length > 0) {
    successful.forEach(r => {
      console.log(`   • ${r.email} (${r.role})`);
    });
  }

  if (failed.length > 0) {
    console.log(`\n❌ Failed: ${failed.length}/${TEST_USERS.length}`);
    failed.forEach(r => {
      console.log(`   • ${r.email} (${r.role}): ${r.error}`);
    });
  }

  // Print credentials
  console.log('\n' + '='.repeat(80));
  console.log('🔑 TEST CREDENTIALS (Copy these!)');
  console.log('='.repeat(80));
  console.log('\nRole Hierarchy: superadmin → admin → manager → analyst → user\n');

  TEST_USERS.forEach((user, index) => {
    console.log(`${index + 1}. ${user.role.toUpperCase()} (${user.full_name})`);
    console.log(`   Email:    ${user.email}`);
    console.log(`   Password: ${user.password}`);
    console.log(`   Scope:    ${user.constituency}`);
    console.log('');
  });

  console.log('='.repeat(80));
  console.log('✅ SETUP COMPLETE!');
  console.log('='.repeat(80));
  console.log('\n💡 Now you can:');
  console.log('   1. Go to http://localhost:5173/login');
  console.log('   2. Login with any of the credentials above');
  console.log('   3. Click on your profile icon (bottom left)');
  console.log('   4. Verify the role badge matches your login role');
  console.log('\n📝 Expected behavior:');
  console.log('   • Login as manager@tvk.com → Badge shows "Manager"');
  console.log('   • Login as analyst@tvk.com → Badge shows "Analyst"');
  console.log('   • Login as user@tvk.com → Badge shows "User"');
  console.log('');
}

createAllRoleUsers().catch(console.error);
