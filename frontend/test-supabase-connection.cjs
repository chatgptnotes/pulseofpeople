const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://iwtgbseaoztjbnvworyq.supabase.co';
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml3dGdic2Vhb3p0amJudndvcnlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjExNjAzOTksImV4cCI6MjA3NjczNjM5OX0.xA4B0XZJE_4MdjFCkw2yVsf4vlHmHfpeV6Bk5tG2T94';

console.log('🔍 Testing Supabase Connection...\n');
console.log('Supabase URL:', supabaseUrl);
console.log('Anon Key:', supabaseAnonKey.substring(0, 50) + '...\n');

const supabase = createClient(supabaseUrl, supabaseAnonKey);

async function testConnection() {
  try {
    // Test 1: Basic connection health check
    console.log('Test 1: Basic Connection Health Check');
    console.log('─'.repeat(70));

    const startTime = Date.now();
    const healthCheck = await fetch(supabaseUrl + '/rest/v1/', {
      headers: {
        'apikey': supabaseAnonKey
      }
    });
    const responseTime = Date.now() - startTime;

    console.log('Status:', healthCheck.status, healthCheck.statusText);
    console.log('Response Time:', responseTime + 'ms');

    if (healthCheck.ok) {
      console.log('✅ Supabase REST API is reachable\n');
    } else {
      console.log('❌ Supabase REST API returned error\n');
    }

    // Test 2: Auth API check
    console.log('Test 2: Auth API Check');
    console.log('─'.repeat(70));

    const authCheck = await fetch(supabaseUrl + '/auth/v1/health', {
      headers: {
        'apikey': supabaseAnonKey
      }
    });

    console.log('Auth API Status:', authCheck.status);

    if (authCheck.ok) {
      const authData = await authCheck.json();
      console.log('✅ Auth API is healthy');
      console.log('Auth Response:', JSON.stringify(authData, null, 2));
      console.log('');
    } else {
      console.log('❌ Auth API returned error\n');
    }

    // Test 3: Try to sign in
    console.log('Test 3: Testing Login with admin@tvk.com');
    console.log('─'.repeat(70));

    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email: 'admin@tvk.com',
        password: 'Admin@123456',
      });

      if (error) {
        console.log('❌ Login failed:', error.message);
        console.log('Error details:', JSON.stringify(error, null, 2));

        if (error.message.includes('Invalid login credentials')) {
          console.log('\n📋 REASON: Email not confirmed OR wrong password');
          console.log('   Action: Go to Supabase Auth and confirm the email');
        } else if (error.message.includes('User not found')) {
          console.log('\n📋 REASON: User does not exist in Auth');
          console.log('   Action: Create user in Supabase Auth Dashboard');
        }
      } else if (data.user) {
        console.log('✅ Login successful!');
        console.log('User ID:', data.user.id);
        console.log('Email:', data.user.email);
        console.log('Email Confirmed:', data.user.email_confirmed_at ? 'YES ✅' : 'NO ❌');
        console.log('Created At:', data.user.created_at);
      }
    } catch (loginError) {
      console.log('❌ Login threw error:', loginError.message);
    }

    console.log('\n' + '='.repeat(70));

    // Test 4: List auth users (if we can)
    console.log('\nTest 4: Checking Auth Users');
    console.log('─'.repeat(70));

    try {
      const { data: { users }, error } = await supabase.auth.admin.listUsers();

      if (error) {
        console.log('⚠️  Cannot list users (requires service_role key)');
        console.log('   This is normal - only testing anon key');
      } else if (users) {
        console.log('Found', users.length, 'users');
        users.forEach(u => {
          console.log(`  - ${u.email} (Confirmed: ${u.email_confirmed_at ? 'Yes' : 'No'})`);
        });
      }
    } catch (err) {
      console.log('⚠️  User listing requires service_role key');
    }

  } catch (error) {
    console.error('❌ Connection test failed:', error.message);
    console.error('Error stack:', error.stack);

    console.log('\n' + '='.repeat(70));
    console.log('🚨 DIAGNOSIS:');
    console.log('='.repeat(70));

    if (error.message.includes('fetch')) {
      console.log('Network error - Cannot reach Supabase');
      console.log('Possible causes:');
      console.log('  1. No internet connection');
      console.log('  2. Firewall blocking Supabase');
      console.log('  3. DNS resolution issue');
      console.log('  4. Supabase is down (unlikely)');
    } else if (error.message.includes('Invalid API key')) {
      console.log('Invalid Supabase API key');
      console.log('  → Check your .env file');
      console.log('  → Get keys from: https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq/settings/api');
    }
  }

  console.log('\n' + '='.repeat(70));
  console.log('📋 NEXT STEPS:');
  console.log('='.repeat(70));
  console.log('If connection works but login fails:');
  console.log('  1. Go to: https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq/auth/users');
  console.log('  2. Find or create user: admin@tvk.com');
  console.log('  3. Click "..." → "Confirm Email"');
  console.log('  4. Try login again');
  console.log('='.repeat(70));
}

testConnection().catch(console.error);
