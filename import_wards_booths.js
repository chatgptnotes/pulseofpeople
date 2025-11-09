const fs = require('fs');
const path = require('path');

// ============================================================================
// CSV to SQL Import Script for Wards and Polling Booths
// ============================================================================
// Usage:
//   node import_wards_booths.js --wards csv_data/wards.csv
//   node import_wards_booths.js --booths csv_data/booths.csv
//   node import_wards_booths.js --all (imports both)
// ============================================================================

const ORGANIZATION_ID = '11111111-1111-1111-1111-111111111111';

// ============================================================================
// CSV Parser (simple, no dependencies)
// ============================================================================

function parseCSV(csvText) {
  const lines = csvText.split('\n').filter(line => line.trim());
  if (lines.length === 0) return [];

  const headers = lines[0].split(',').map(h => h.trim());
  const rows = [];

  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(',').map(v => v.trim());
    const row = {};
    headers.forEach((header, index) => {
      row[header] = values[index] || null;
    });
    rows.push(row);
  }

  return rows;
}

// ============================================================================
// Generate Wards SQL
// ============================================================================

function generateWardsSQL(csvFilePath) {
  console.log(`\n📊 Processing Wards CSV: ${csvFilePath}\n`);

  const csvText = fs.readFileSync(csvFilePath, 'utf8');
  const wards = parseCSV(csvText);

  console.log(`Found ${wards.length} wards to import\n`);

  let sql = `-- ============================================================================
-- WARDS IMPORT - Generated from CSV
-- ============================================================================
-- Generated: ${new Date().toISOString()}
-- Total Wards: ${wards.length}
-- ============================================================================

-- Ensure TVK organization exists
INSERT INTO organizations (id, name, slug, type, subscription_status, is_active)
VALUES ('${ORGANIZATION_ID}', 'Tamilaga Vettri Kazhagam', 'tvk', 'political_party', 'active', true)
ON CONFLICT (id) DO NOTHING;

-- Import wards (with constituency lookup)
INSERT INTO wards (
  organization_id,
  constituency_id,
  name,
  code,
  ward_number,
  population,
  voter_count,
  total_booths,
  urbanization,
  income_level,
  literacy_rate
) VALUES
`;

  const values = wards.map((ward, index) => {
    const constituencyCode = ward.constituency_code;
    const wardName = ward.ward_name.replace(/'/g, "''");
    const wardCode = ward.ward_code;
    const wardNumber = ward.ward_number || 'NULL';
    const population = ward.population || 'NULL';
    const voterCount = ward.voter_count || '0';
    const totalBooths = ward.total_booths || '0';
    const urbanization = ward.urbanization ? `'${ward.urbanization}'` : 'NULL';
    const incomeLevel = ward.income_level ? `'${ward.income_level}'` : 'NULL';
    const literacyRate = ward.literacy_rate || 'NULL';

    return `  (
    '${ORGANIZATION_ID}'::uuid,
    (SELECT id FROM constituencies WHERE code = '${constituencyCode}' AND organization_id = '${ORGANIZATION_ID}' LIMIT 1),
    '${wardName}',
    '${wardCode}',
    ${wardNumber},
    ${population},
    ${voterCount},
    ${totalBooths},
    ${urbanization},
    ${incomeLevel},
    ${literacyRate}
  )`;
  }).join(',\n');

  sql += values;
  sql += `\nON CONFLICT (organization_id, code) DO UPDATE SET
  name = EXCLUDED.name,
  ward_number = EXCLUDED.ward_number,
  population = EXCLUDED.population,
  voter_count = EXCLUDED.voter_count,
  total_booths = EXCLUDED.total_booths,
  urbanization = EXCLUDED.urbanization,
  income_level = EXCLUDED.income_level,
  literacy_rate = EXCLUDED.literacy_rate,
  updated_at = NOW();

-- Verify import
SELECT
  'Wards Import' as type,
  COUNT(*) as total_imported,
  COUNT(DISTINCT constituency_id) as constituencies_covered
FROM wards
WHERE organization_id = '${ORGANIZATION_ID}';

-- Show breakdown by constituency
SELECT
  c.code as constituency_code,
  c.name as constituency_name,
  COUNT(w.id) as ward_count,
  SUM(w.total_booths) as total_booths
FROM constituencies c
LEFT JOIN wards w ON w.constituency_id = c.id
WHERE c.organization_id = '${ORGANIZATION_ID}'
GROUP BY c.id, c.code, c.name
HAVING COUNT(w.id) > 0
ORDER BY c.code;
`;

  return sql;
}

// ============================================================================
// Generate Polling Booths SQL
// ============================================================================

function generateBoothsSQL(csvFilePath) {
  console.log(`\n🗳️  Processing Booths CSV: ${csvFilePath}\n`);

  const csvText = fs.readFileSync(csvFilePath, 'utf8');
  const booths = parseCSV(csvText);

  console.log(`Found ${booths.length} booths to import\n`);

  let sql = `-- ============================================================================
-- POLLING BOOTHS IMPORT - Generated from CSV
-- ============================================================================
-- Generated: ${new Date().toISOString()}
-- Total Booths: ${booths.length}
-- ============================================================================

-- Ensure TVK organization exists
INSERT INTO organizations (id, name, slug, type, subscription_status, is_active)
VALUES ('${ORGANIZATION_ID}', 'Tamilaga Vettri Kazhagam', 'tvk', 'political_party', 'active', true)
ON CONFLICT (id) DO NOTHING;

-- Import polling booths (with constituency and ward lookup)
INSERT INTO polling_booths (
  organization_id,
  constituency_id,
  ward_id,
  booth_number,
  name,
  address,
  latitude,
  longitude,
  total_voters,
  male_voters,
  female_voters,
  transgender_voters,
  accessible,
  parking_available,
  landmark
) VALUES
`;

  const values = booths.map((booth, index) => {
    const constituencyCode = booth.constituency_code;
    const wardCode = booth.ward_code || null;
    const boothNumber = booth.booth_number;
    const boothName = booth.booth_name.replace(/'/g, "''");
    const address = booth.address ? booth.address.replace(/'/g, "''") : '';
    const latitude = booth.latitude || 'NULL';
    const longitude = booth.longitude || 'NULL';
    const totalVoters = booth.total_voters || '0';
    const maleVoters = booth.male_voters || '0';
    const femaleVoters = booth.female_voters || '0';
    const transgenderVoters = booth.transgender_voters || '0';
    const accessible = booth.accessible === 'true' || booth.accessible === '1' || booth.accessible === 'TRUE';
    const parkingAvailable = booth.parking_available === 'true' || booth.parking_available === '1' || booth.parking_available === 'TRUE';
    const landmark = booth.landmark ? booth.landmark.replace(/'/g, "''") : '';

    const wardLookup = wardCode
      ? `(SELECT id FROM wards WHERE code = '${wardCode}' AND organization_id = '${ORGANIZATION_ID}' LIMIT 1)`
      : 'NULL';

    return `  (
    '${ORGANIZATION_ID}'::uuid,
    (SELECT id FROM constituencies WHERE code = '${constituencyCode}' AND organization_id = '${ORGANIZATION_ID}' LIMIT 1),
    ${wardLookup},
    '${boothNumber}',
    '${boothName}',
    '${address}',
    ${latitude},
    ${longitude},
    ${totalVoters},
    ${maleVoters},
    ${femaleVoters},
    ${transgenderVoters},
    ${accessible},
    ${parkingAvailable},
    '${landmark}'
  )`;
  }).join(',\n');

  sql += values;
  sql += `\nON CONFLICT (organization_id, constituency_id, booth_number) DO UPDATE SET
  name = EXCLUDED.name,
  address = EXCLUDED.address,
  latitude = EXCLUDED.latitude,
  longitude = EXCLUDED.longitude,
  total_voters = EXCLUDED.total_voters,
  male_voters = EXCLUDED.male_voters,
  female_voters = EXCLUDED.female_voters,
  transgender_voters = EXCLUDED.transgender_voters,
  accessible = EXCLUDED.accessible,
  parking_available = EXCLUDED.parking_available,
  landmark = EXCLUDED.landmark,
  updated_at = NOW();

-- Verify import
SELECT
  'Booths Import' as type,
  COUNT(*) as total_imported,
  COUNT(DISTINCT constituency_id) as constituencies_covered,
  COUNT(DISTINCT ward_id) as wards_covered,
  SUM(total_voters) as total_voters
FROM polling_booths
WHERE organization_id = '${ORGANIZATION_ID}';

-- Show breakdown by constituency
SELECT
  c.code as constituency_code,
  c.name as constituency_name,
  COUNT(pb.id) as booth_count,
  SUM(pb.total_voters) as total_voters,
  SUM(pb.male_voters) as male_voters,
  SUM(pb.female_voters) as female_voters
FROM constituencies c
LEFT JOIN polling_booths pb ON pb.constituency_id = c.id
WHERE c.organization_id = '${ORGANIZATION_ID}'
GROUP BY c.id, c.code, c.name
HAVING COUNT(pb.id) > 0
ORDER BY c.code;
`;

  return sql;
}

// ============================================================================
// Main Execution
// ============================================================================

function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log(`
📚 CSV to SQL Import Tool for Wards and Polling Booths

Usage:
  node import_wards_booths.js --wards <csv_file>
  node import_wards_booths.js --booths <csv_file>
  node import_wards_booths.js --all

Options:
  --wards <file>   Convert wards CSV to SQL
  --booths <file>  Convert booths CSV to SQL
  --all            Convert both (looks for csv_data/wards.csv and csv_data/booths.csv)

Examples:
  node import_wards_booths.js --wards csv_data/wards.csv
  node import_wards_booths.js --booths csv_data/booths.csv
  node import_wards_booths.js --all

Output:
  SQL files will be created in the current directory:
  - import_wards.sql
  - import_booths.sql
`);
    process.exit(0);
  }

  const mode = args[0];

  if (mode === '--wards') {
    const csvFile = args[1] || 'csv_data/wards.csv';
    if (!fs.existsSync(csvFile)) {
      console.error(`❌ Error: File not found: ${csvFile}`);
      process.exit(1);
    }

    const sql = generateWardsSQL(csvFile);
    const outputFile = 'import_wards.sql';
    fs.writeFileSync(outputFile, sql, 'utf8');

    console.log(`✅ Generated: ${outputFile}`);
    console.log(`📄 File size: ${(fs.statSync(outputFile).size / 1024).toFixed(2)} KB`);
    console.log(`\n🚀 Next: Run this SQL in Supabase SQL Editor\n`);

  } else if (mode === '--booths') {
    const csvFile = args[1] || 'csv_data/booths.csv';
    if (!fs.existsSync(csvFile)) {
      console.error(`❌ Error: File not found: ${csvFile}`);
      process.exit(1);
    }

    const sql = generateBoothsSQL(csvFile);
    const outputFile = 'import_booths.sql';
    fs.writeFileSync(outputFile, sql, 'utf8');

    console.log(`✅ Generated: ${outputFile}`);
    console.log(`📄 File size: ${(fs.statSync(outputFile).size / 1024).toFixed(2)} KB`);
    console.log(`\n🚀 Next: Run this SQL in Supabase SQL Editor\n`);

  } else if (mode === '--all') {
    const wardsFile = 'csv_data/wards.csv';
    const boothsFile = 'csv_data/booths.csv';

    if (fs.existsSync(wardsFile)) {
      const wardsSql = generateWardsSQL(wardsFile);
      fs.writeFileSync('import_wards.sql', wardsSql, 'utf8');
      console.log(`✅ Generated: import_wards.sql`);
    }

    if (fs.existsSync(boothsFile)) {
      const boothsSql = generateBoothsSQL(boothsFile);
      fs.writeFileSync('import_booths.sql', boothsSql, 'utf8');
      console.log(`✅ Generated: import_booths.sql`);
    }

    console.log(`\n🚀 Next: Run both SQL files in Supabase SQL Editor\n`);

  } else {
    console.error(`❌ Unknown mode: ${mode}`);
    console.error(`Use --wards, --booths, or --all`);
    process.exit(1);
  }
}

main();
