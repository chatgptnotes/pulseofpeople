-- =====================================================
-- CONSTITUENCY MASTER DATA - SEED TEMPLATE
-- Tamil Nadu Assembly Constituencies (234)
-- Date: 2025-11-06
-- =====================================================
-- NOTE: This is a template showing the structure.
-- Complete data should be imported from official Election Commission sources.
-- =====================================================

-- =====================================================
-- TAMIL NADU CONSTITUENCIES SEED DATA
-- =====================================================

-- Example constituencies for each district
-- Structure: (code, constituency_number, name, name_tamil, state_code, district_code, reservation_type, parliamentary_constituency, remarks)

INSERT INTO assembly_constituencies (
    code,
    constituency_number,
    name,
    name_tamil,
    state_code,
    district_code,
    reservation_type,
    parliamentary_constituency,
    center_lat,
    center_lng,
    total_voters,
    polling_booths,
    formation_year,
    remarks
) VALUES
-- Chennai District
('TN001', 1, 'Gummidipoondi', 'கும்மிடிப்பூண்டி', 'TN', 'TN03', 'Scheduled Castes', 'Thiruvallur', 13.4074, 80.1119, 285000, 285, 1952, 'Reserved for SC'),
('TN002', 2, 'Ponneri', 'பொன்னேரி', 'TN', 'TN03', 'Scheduled Castes', 'Thiruvallur', 13.3365, 80.1936, 290000, 290, 1952, 'Reserved for SC'),
('TN003', 3, 'Tiruvottiyur', 'திருவொற்றியூர்', 'TN', 'TN03', 'Unreserved', 'North Chennai', 13.1641, 80.3006, 295000, 295, 1952, NULL),
('TN004', 4, 'Radhakrishnan Nagar', 'ராதாகிருஷ்ணன் நகர்', 'TN', 'TN03', 'Unreserved', 'North Chennai', 13.1350, 80.2550, 300000, 300, 2011, NULL),
('TN005', 5, 'Perambur', 'பெரம்பூர்', 'TN', 'TN03', 'Unreserved', 'North Chennai', 13.1143, 80.2381, 285000, 285, 1952, NULL),

-- Coimbatore District
('TN115', 115, 'Sulur', 'சூலூர்', 'TN', 'TN04', 'Scheduled Castes', 'Coimbatore', 11.0287, 77.1283, 295000, 295, 1952, 'Reserved for SC'),
('TN116', 116, 'Kavundampalayam', 'கவுண்டம்பாளையம்', 'TN', 'TN04', 'Unreserved', 'Coimbatore', 11.0510, 76.9698, 300000, 300, 2011, NULL),
('TN117', 117, 'Coimbatore North', 'கோயம்புத்தூர் வடக்கு', 'TN', 'TN04', 'Unreserved', 'Coimbatore', 11.0291, 76.9629, 310000, 310, 1952, NULL),
('TN118', 118, 'Thondamuthur', 'தொண்டாமுத்தூர்', 'TN', 'TN04', 'Unreserved', 'Pollachi', 10.9896, 76.8447, 285000, 285, 1952, NULL),

-- Madurai District
('TN175', 175, 'Madurai East', 'மதுரை கிழக்கு', 'TN', 'TN14', 'Unreserved', 'Madurai', 9.9252, 78.1198, 305000, 305, 1952, NULL),
('TN176', 176, 'Sholavandan', 'சோலவந்தான்', 'TN', 'TN14', 'Unreserved', 'Madurai', 10.1063, 77.8700, 280000, 280, 1952, NULL),
('TN177', 177, 'Madurai North', 'மதுரை வடக்கு', 'TN', 'TN14', 'Unreserved', 'Madurai', 9.9568, 78.1349, 310000, 310, 1952, NULL),
('TN178', 178, 'Madurai South', 'மதுரை தெற்கு', 'TN', 'TN14', 'Unreserved', 'Madurai', 9.9093, 78.1041, 298000, 298, 1952, NULL),
('TN179', 179, 'Madurai Central', 'மதுரை மத்தியம்', 'TN', 'TN14', 'Unreserved', 'Madurai', 9.9195, 78.1193, 295000, 295, 1952, NULL),
('TN180', 180, 'Madurai West', 'மதுரை மேற்கு', 'TN', 'TN14', 'Unreserved', 'Madurai', 9.9147, 78.0985, 300000, 300, 1952, NULL),

-- Add more constituencies following the same pattern...
-- Total should be 234 for Tamil Nadu

-- =====================================================
-- PONDICHERRY CONSTITUENCIES SEED DATA
-- =====================================================

-- Puducherry (30 constituencies)
('PY01', 1, 'Yanam', 'ஆனம்', 'PY', 'PY04', 'Unreserved', 'Puducherry', 16.7333, 82.2167, 45000, 45, 1963, 'Union Territory'),
('PY02', 2, 'Mahe', 'மாஹே', 'PY', 'PY03', 'Unreserved', 'Puducherry', 11.7008, 75.5368, 42000, 42, 1963, 'Union Territory'),
('PY03', 3, 'Thattanchavady', 'தட்டாஞ்சாவடி', 'PY', 'PY01', 'Scheduled Castes', 'Puducherry', 11.9416, 79.8083, 48000, 48, 1963, 'Reserved for SC'),
('PY04', 4, 'Puducherry', 'புதுச்சேரி', 'PY', 'PY01', 'Unreserved', 'Puducherry', 11.9341, 79.8306, 52000, 52, 1963, NULL),
('PY05', 5, 'Ozhukarai', 'ஒழுகாறை', 'PY', 'PY01', 'Scheduled Castes', 'Puducherry', 11.9589, 79.7737, 50000, 50, 1963, 'Reserved for SC')

-- Add remaining 25 constituencies...

ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    name_tamil = EXCLUDED.name_tamil,
    reservation_type = EXCLUDED.reservation_type,
    center_lat = EXCLUDED.center_lat,
    center_lng = EXCLUDED.center_lng,
    total_voters = EXCLUDED.total_voters,
    polling_booths = EXCLUDED.polling_booths,
    updated_at = NOW();

-- =====================================================
-- SAMPLE ELECTED MEMBERS DATA
-- =====================================================

INSERT INTO elected_members (
    constituency_code,
    member_name,
    political_party,
    alliance,
    election_year,
    term_start,
    term_end,
    votes_received,
    vote_percentage,
    victory_margin,
    total_valid_votes,
    is_current_member
) VALUES
-- 2021 Election results (current members)
('TN001', 'K. Selvam', 'DMK', 'DMK Alliance', 2021, '2021-05-07', '2026-05-06', 108523, 52.3, 15234, 207500, TRUE),
('TN002', 'J. Jayavardhan', 'DMK', 'DMK Alliance', 2021, '2021-05-07', '2026-05-06', 112456, 48.9, 8934, 229800, TRUE),
('TN003', 'S. Eswaran', 'DMK', 'DMK Alliance', 2021, '2021-05-07', '2026-05-06', 98765, 45.2, 5678, 218500, TRUE),

-- Historical data (previous terms)
('TN001', 'R. Rajendran', 'AIADMK', 'AIADMK Alliance', 2016, '2016-05-19', '2021-05-06', 95234, 49.8, 3456, 191200, FALSE),
('TN002', 'M. Muthuvel', 'AIADMK', 'AIADMK Alliance', 2016, '2016-05-19', '2021-05-06', 89567, 46.5, 2345, 192600, FALSE)

ON CONFLICT (constituency_code, election_year) DO UPDATE SET
    member_name = EXCLUDED.member_name,
    political_party = EXCLUDED.political_party,
    votes_received = EXCLUDED.votes_received,
    is_current_member = EXCLUDED.is_current_member,
    updated_at = NOW();

-- =====================================================
-- SAMPLE POLLING BOOTHS DATA
-- =====================================================

INSERT INTO polling_booths (
    booth_number,
    booth_name,
    constituency_code,
    location_lat,
    location_lng,
    address,
    total_voters,
    male_voters,
    female_voters,
    is_accessible,
    facilities
) VALUES
('001', 'Government Primary School, Gummidipoondi North', 'TN001', 13.4080, 80.1125, 'Gummidipoondi North Street, Thiruvallur District', 1200, 600, 600, TRUE, ARRAY['Ramp', 'Wheelchair', 'Separate Queue for Elderly']),
('002', 'Government High School, Gummidipoondi South', 'TN001', 13.4065, 80.1110, 'Gummidipoondi South Main Road, Thiruvallur District', 1150, 575, 575, TRUE, ARRAY['Ramp', 'Wheelchair']),
('003', 'Community Hall, Gummidipoondi East', 'TN001', 13.4090, 80.1135, 'Gummidipoondi East Street, Thiruvallur District', 1080, 540, 540, TRUE, ARRAY['Ramp', 'Separate Queue for Elderly'])

ON CONFLICT (constituency_code, booth_number) DO UPDATE SET
    booth_name = EXCLUDED.booth_name,
    location_lat = EXCLUDED.location_lat,
    location_lng = EXCLUDED.location_lng,
    total_voters = EXCLUDED.total_voters,
    updated_at = NOW();

-- =====================================================
-- DATA VALIDATION QUERIES
-- =====================================================

-- Check total constituencies by state
-- SELECT state_code, COUNT(*) as total_constituencies
-- FROM assembly_constituencies
-- GROUP BY state_code;
-- Expected: TN=234, PY=30

-- Check reservation distribution
-- SELECT reservation_type, COUNT(*) as count
-- FROM assembly_constituencies
-- WHERE state_code = 'TN'
-- GROUP BY reservation_type;
-- Expected: SC=44, ST=3, Unreserved=187 (for current Tamil Nadu)

-- Check for duplicate constituency numbers
-- SELECT state_code, constituency_number, COUNT(*)
-- FROM assembly_constituencies
-- GROUP BY state_code, constituency_number
-- HAVING COUNT(*) > 1;
-- Expected: 0 rows (no duplicates)

-- =====================================================
-- NOTES FOR DATA IMPORT
-- =====================================================

/*
RECOMMENDED DATA SOURCES:
1. Election Commission of India (https://eci.gov.in)
   - Official constituency boundaries
   - Voter statistics
   - Election results

2. Tamil Nadu Chief Electoral Officer (https://www.elections.tn.gov.in)
   - Constituency-wise voter lists
   - Polling booth locations
   - Detailed demographic data

3. OpenStreetMap / Google Maps API
   - Geographic coordinates
   - Boundary polygons (GeoJSON)

IMPORT PROCESS:
1. Export official data to CSV format
2. Clean and validate data
3. Use COPY command for bulk import:
   COPY assembly_constituencies FROM '/path/to/constituencies.csv' DELIMITER ',' CSV HEADER;

4. Verify data integrity using validation queries above
5. Update center_point column using trigger (happens automatically)

ONGOING MAINTENANCE:
- Update after each election (every 5 years)
- Update voter counts annually
- Track boundary changes (delimitation)
- Maintain historical data for trend analysis
*/

-- =====================================================
-- END OF SEED DATA
-- =====================================================
