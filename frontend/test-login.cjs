const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://iwtgbseaoztjbnvworyq.supabase.co';
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml3dGdic2Vhb3p0amJudndvcnlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjExNjAzOTksImV4cCI6MjA3NjczNjM5OX0.xA4B0XZJE_4MdjFCkw2yVsf4vlHmHfpeV6Bk5tG2T94';

const supabase = createClient(supabaseUrl, supabaseAnonKey);

async function testLogin() {
  console.log('🔍 Testing Supabase Connection and Login...\n');

  // Test 1: Check database connection
  console.log('Test 1: Checking database connection...');
  try {
    const { data, error } = await supabase.from('users').select('count').limit(1);
    if (error) {
      console.log('❌ Database connection failed:', error.message);
    } else {
      console.log('✅ Database connection successful\n');
    }
  } catch (err) {
    console.log('❌ Database connection error:', err.message);
  }

  // Test 2: Check if users table exists and has data
  console.log('Test 2: Checking users table...');
  try {
    const { data: users, error } = await supabase
      .from('users')
      .select('id, email, role, is_super_admin')
      .limit(5);

    if (error) {
      console.log('❌ Users table error:', error.message);
      console.log('   This might mean the users table doesn\'t exist yet\n');
    } else if (!users || users.length === 0) {
      console.log('⚠️  Users table exists but is empty\n');
    } else {
      console.log('✅ Found', users.length, 'user(s) in database:');
      users.forEach(u => {
        console.log(`   - ${u.email} (${u.role})${u.is_super_admin ? ' [SUPER ADMIN]' : ''}`);
      });
      console.log('');
    }
  } catch (err) {
    console.log('❌ Users table check error:', err.message);
  }

  // Test 3: Try login with superadmin credentials
  console.log('Test 3: Testing login with admin@tvk.com...');
  try {
    const { data: authData, error: authError } = await supabase.auth.signInWithPassword({
      email: 'admin@tvk.com',
      password: 'Admin@123456',
    });

    if (authError) {
      console.log('❌ Login failed:', authError.message);
    } else if (authData.user) {
      console.log('✅ Login successful!');
      console.log('   User ID:', authData.user.id);
      console.log('   Email:', authData.user.email);
      console.log('   Email Confirmed:', authData.user.email_confirmed_at ? 'Yes' : 'No');

      // Try to fetch user data from database
      const { data: userData, error: userError } = await supabase
        .from('users')
        .select('*')
        .eq('email', 'admin@tvk.com')
        .single();

      if (userError) {
        console.log('   ⚠️  User exists in Auth but NOT in users table');
        console.log('   Error:', userError.message);
      } else if (userData) {
        console.log('   ✅ User data found in database');
        console.log('   Name:', userData.full_name || userData.name);
        console.log('   Role:', userData.role);
      }
    }
  } catch (err) {
    console.log('❌ Login test error:', err.message);
  }

  console.log('\n' + '='.repeat(70));
  console.log('🎯 DIAGNOSIS:');
  console.log('='.repeat(70));
  console.log('If login succeeded but user data NOT found in database:');
  console.log('  → You need to run the SQL migration to create the users table');
  console.log('  → Or insert user records into the users table');
  console.log('\nIf login failed:');
  console.log('  → Check email confirmation status in Supabase Dashboard');
  console.log('  → Verify password is correct: Admin@123456');
  console.log('='.repeat(70));
}

testLogin().catch(console.error);
