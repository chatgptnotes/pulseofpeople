const fs = require('fs');
const path = require('path');

// Read the GeoJSON file
const geoJsonPath = path.join(__dirname, 'frontend', 'src', 'data', 'geo', 'tamilnadu-constituencies-full.json');
const geoJson = JSON.parse(fs.readFileSync(geoJsonPath, 'utf8'));

console.log(`\n📊 Total constituencies: ${geoJson.features.length}\n`);

// Configuration
const ORGANIZATION_ID = '11111111-1111-1111-1111-111111111111';
const BATCH_SIZE = 59; // 234 / 4 = 58.5, so 59, 59, 59, 57
const OUTPUT_DIR = path.join(__dirname, 'supabase', 'migrations', 'batches');

// Create output directory
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

// Split constituencies into 4 batches
const batches = [];
for (let i = 0; i < 4; i++) {
  const start = i * BATCH_SIZE;
  const end = Math.min(start + BATCH_SIZE, geoJson.features.length);
  batches.push(geoJson.features.slice(start, end));
}

console.log('Batch sizes:');
batches.forEach((batch, i) => {
  console.log(`  Batch ${i + 1}: ${batch.length} constituencies`);
});
console.log('');

// Generate SQL for each batch
batches.forEach((batch, batchIndex) => {
  const batchNumber = batchIndex + 1;
  const timestamp = `20251109140000_tn_batch${batchNumber}`;
  const filename = `${timestamp}_insert_tn_constituencies.sql`;
  const filepath = path.join(OUTPUT_DIR, filename);

  let sql = `-- ============================================================================
-- BATCH ${batchNumber}/4: Tamil Nadu Constituencies (${batch.length} constituencies)
-- ============================================================================
-- Total TN: 234 constituencies split into 4 batches for safe import
-- This batch: Constituencies ${batchIndex * BATCH_SIZE + 1} - ${Math.min((batchIndex + 1) * BATCH_SIZE, 234)}
-- ============================================================================

-- Ensure TVK organization exists
INSERT INTO organizations (id, name, slug, type, subscription_status, is_active)
VALUES ('${ORGANIZATION_ID}', 'Tamilaga Vettri Kazhagam', 'tvk', 'political_party', 'active', true)
ON CONFLICT (id) DO NOTHING;

-- Insert batch ${batchNumber} constituencies
INSERT INTO constituencies (
  organization_id,
  name,
  code,
  type,
  state,
  district,
  population,
  voter_count,
  total_booths,
  area_sq_km,
  reserved_category,
  last_election_year,
  current_representative,
  current_party,
  boundaries
) VALUES
`;

  const values = batch.map((feature, index) => {
    const props = feature.properties;
    const geometry = feature.geometry;

    // Extract constituency details
    const acNo = props.AC_NO || props.ac_no || (batchIndex * BATCH_SIZE + index + 1);
    const acName = (props.AC_NAME || props.ac_name || `Constituency ${acNo}`).trim();

    // Extract reserved category from name (e.g., "Ponneri (SC)" -> "sc")
    const cleanName = acName.replace(/\s*\((SC|ST)\)\s*$/i, '').trim();
    const reservedCategory = acName.match(/\((SC|ST)\)/i)
      ? acName.match(/\((SC|ST)\)/i)[1].toLowerCase()
      : 'general';

    // Format code
    const code = `TN-AC-${String(acNo).padStart(3, '0')}`;

    // Extract district name
    const distName = (props.DIST_NAME || props.dist_name || 'Unknown').trim();

    // Convert geometry to JSON string (escape single quotes)
    const boundariesJson = JSON.stringify(geometry).replace(/'/g, "''");

    return `  (
    '${ORGANIZATION_ID}',
    '${cleanName.replace(/'/g, "''")}',
    '${code}',
    'assembly',
    'Tamil Nadu',
    '${distName.replace(/'/g, "''")}',
    NULL, -- population (to be filled later)
    0, -- voter_count
    0, -- total_booths
    NULL, -- area_sq_km
    '${reservedCategory}',
    2021, -- last_election_year
    NULL, -- current_representative
    NULL, -- current_party
    '${boundariesJson}'::jsonb
  )`;
  }).join(',\n');

  sql += values;
  sql += `\nON CONFLICT (organization_id, code) DO UPDATE SET
  name = EXCLUDED.name,
  district = EXCLUDED.district,
  boundaries = EXCLUDED.boundaries,
  reserved_category = EXCLUDED.reserved_category;

-- Verify batch ${batchNumber} import
SELECT
  'Batch ${batchNumber}' as batch,
  COUNT(*) as inserted,
  COUNT(*) FILTER (WHERE reserved_category = 'sc') as sc,
  COUNT(*) FILTER (WHERE reserved_category = 'st') as st,
  COUNT(*) FILTER (WHERE reserved_category = 'general') as general
FROM constituencies
WHERE organization_id = '${ORGANIZATION_ID}'
  AND code LIKE 'TN-AC-%'
  AND code >= 'TN-AC-${String(batchIndex * BATCH_SIZE + 1).padStart(3, '0')}'
  AND code <= 'TN-AC-${String(Math.min((batchIndex + 1) * BATCH_SIZE, 234)).padStart(3, '0')}';
`;

  // Write to file
  fs.writeFileSync(filepath, sql, 'utf8');
  console.log(`✅ Created: ${filename}`);

  // Calculate file size
  const stats = fs.statSync(filepath);
  const sizeKB = (stats.size / 1024).toFixed(2);
  console.log(`   Size: ${sizeKB} KB\n`);
});

console.log('🎉 All 4 batch files created successfully!\n');
console.log('📁 Location: supabase/migrations/batches/\n');
console.log('📝 Import Instructions:');
console.log('   1. Go to Supabase SQL Editor');
console.log('   2. Run each batch file in order (batch1, batch2, batch3, batch4)');
console.log('   3. Wait for each to complete before running the next\n');
