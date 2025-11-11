-- ============================================================================
-- QUICK IMPORT: All 234 Tamil Nadu Constituencies
-- ============================================================================
-- Optimized for Supabase SQL Editor - Smaller payload
-- ============================================================================

-- 1. Ensure organization exists
INSERT INTO organizations (id, name, slug, type, subscription_status, is_active)
VALUES ('11111111-1111-1111-1111-111111111111', 'Tamilaga Vettri Kazhagam', 'tvk', 'political_party', 'active', true)
ON CONFLICT (id) DO NOTHING;

-- 2. Load constituencies from JSON file (client-side approach)
-- Since the SQL is too large, use this JavaScript approach instead
-- Run this in your browser console on the Supabase SQL Editor page:

/*
(async () => {
  const response = await fetch('/Users/murali/1backup/Pulseofpeople8thNov/pulseofpeople/frontend/src/data/geo/tamilnadu-constituencies-full.json');
  const data = await response.json();
  
  console.log(`Loading ${data.features.length} constituencies...`);
  
  // Import via Supabase client
  // You'll need to adapt this for your use case
})();
*/

