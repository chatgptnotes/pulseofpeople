// Check Supabase data for organizations and wards
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://iwtgbseaoztjbnvworyq.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml3dGdic2Vhb3p0amJudndvcnlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjExNjAzOTksImV4cCI6MjA3NjczNjM5OX0.xA4B0XZJE_4MdjFCkw2yVsf4vlHmHfpeV6Bk5tG2T94';

const supabase = createClient(supabaseUrl, supabaseKey);

async function checkData() {
  console.log('\n=== ORGANIZATIONS ===\n');

  const { data: organizations, error: orgError } = await supabase
    .from('organizations')
    .select('id, name, slug, type, subscription_status')
    .order('name');

  if (orgError) {
    console.error('Error fetching organizations:', orgError);
  } else {
    console.table(organizations);
    console.log(`\nTotal organizations: ${organizations?.length || 0}\n`);
  }

  console.log('\n=== WARDS ===\n');

  const { data: wards, error: wardsError } = await supabase
    .from('wards')
    .select(`
      id,
      name,
      code,
      ward_number,
      population,
      voter_count,
      constituency:constituencies(name)
    `)
    .order('name');

  if (wardsError) {
    console.error('Error fetching wards:', wardsError);
  } else {
    console.table(wards);
    console.log(`\nTotal wards: ${wards?.length || 0}\n`);
  }

  console.log('\n=== CONSTITUENCIES ===\n');

  const { data: constituencies, error: constError } = await supabase
    .from('constituencies')
    .select('id, name, code, type, state, district, voter_count')
    .order('name');

  if (constError) {
    console.error('Error fetching constituencies:', constError);
  } else {
    console.table(constituencies);
    console.log(`\nTotal constituencies: ${constituencies?.length || 0}\n`);
  }

  process.exit(0);
}

checkData();
