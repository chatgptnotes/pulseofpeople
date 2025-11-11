const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://iwtgbseaoztjbnvworyq.supabase.co';
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml3dGdic2Vhb3p0amJudndvcnlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjExNjAzOTksImV4cCI6MjA3NjczNjM5OX0.xA4B0XZJE_4MdjFCkw2yVsf4vlHmHfpeV6Bk5tG2T94';

const supabase = createClient(supabaseUrl, supabaseAnonKey);

async function createConfirmedUser() {
  console.log('🔧 Creating Auto-Confirmed Test User...\n');

  const testEmail = 'testadmin@tvk.com';
  const testPassword = 'TestAdmin123!';

  try {
    // Try to sign up with auto-confirm
    console.log('Attempting to create user:', testEmail);

    const { data, error } = await supabase.auth.signUp({
      email: testEmail,
      password: testPassword,
      options: {
        data: {
          full_name: 'Test Admin',
          role: 'superadmin'
        },
        emailRedirectTo: undefined // Don't send confirmation email
      }
    });

    if (error) {
      if (error.message.includes('already registered')) {
        console.log('✅ User already exists, trying to login...\n');

        // Try to login
        const { data: loginData, error: loginError } = await supabase.auth.signInWithPassword({
          email: testEmail,
          password: testPassword,
        });

        if (loginError) {
          console.log('❌ Login failed:', loginError.message);
          console.log('\n🔍 Let me try the original credentials...\n');

          // Try original admin@tvk.com
          const { data: origLogin, error: origError } = await supabase.auth.signInWithPassword({
            email: 'admin@tvk.com',
            password: 'Admin@123456',
          });

          if (origError) {
            console.log('❌ Original admin@tvk.com login also failed:', origError.message);

            // Try with shorter password
            console.log('\n🔍 Trying with Admin@123...\n');
            const { data: shortLogin, error: shortError } = await supabase.auth.signInWithPassword({
              email: 'admin@tvk.com',
              password: 'Admin@123',
            });

            if (shortError) {
              console.log('❌ Admin@123 also failed:', shortError.message);
            } else {
              console.log('✅ SUCCESS with Admin@123!');
              console.log('User ID:', shortLogin.user.id);
              console.log('Email:', shortLogin.user.email);
            }
          } else {
            console.log('✅ SUCCESS with Admin@123456!');
            console.log('User ID:', origLogin.user.id);
            console.log('Email:', origLogin.user.email);
          }
        } else {
          console.log('✅ Login successful with testadmin@tvk.com!');
          console.log('User ID:', loginData.user.id);
          console.log('Email:', loginData.user.email);
        }
      } else {
        console.log('❌ Signup failed:', error.message);
      }
    } else if (data.user) {
      console.log('✅ User created successfully!');
      console.log('User ID:', data.user.id);
      console.log('Email:', data.user.email);
      console.log('Email Confirmed:', data.user.email_confirmed_at ? 'YES' : 'NO');

      if (!data.user.email_confirmed_at) {
        console.log('\n⚠️  Email NOT confirmed automatically');
        console.log('   Supabase settings require email confirmation');
      }
    }

  } catch (err) {
    console.error('❌ Error:', err.message);
  }

  console.log('\n' + '='.repeat(70));
  console.log('📋 WORKING CREDENTIALS TO TRY:');
  console.log('='.repeat(70));
  console.log('\nOption 1 (New Test User):');
  console.log('  Email:', testEmail);
  console.log('  Password:', testPassword);
  console.log('\nOption 2 (Original):');
  console.log('  Email: admin@tvk.com');
  console.log('  Password: Admin@123456');
  console.log('\nOption 3 (Short password):');
  console.log('  Email: admin@tvk.com');
  console.log('  Password: Admin@123');
  console.log('='.repeat(70));

  console.log('\n💡 IMPORTANT:');
  console.log('If NONE of these work, you MUST go to Supabase Dashboard:');
  console.log('1. https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq/auth/users');
  console.log('2. Click "Add User" → Create new user');
  console.log('3. Email: admin@tvk.com, Password: Admin@123456');
  console.log('4. ✅ CHECK "Auto Confirm User"');
  console.log('5. Click "Create User"');
  console.log('='.repeat(70));
}

createConfirmedUser().catch(console.error);
