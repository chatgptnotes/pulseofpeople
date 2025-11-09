-- ============================================================
-- TRENDING TOPICS SEED DATA
-- ============================================================
-- Purpose: Generate 100 realistic trending political topics for Tamil Nadu
-- Based on: Real TN issues (Water crisis, TVK, NEET, Cauvery, Jobs, Fishermen)
-- Time Range: Last 7 days
-- Usage: Run via Supabase SQL Editor or psql
-- ============================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create trending_topics table
CREATE TABLE IF NOT EXISTS trending_topics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  keyword TEXT NOT NULL,
  volume INTEGER NOT NULL,
  growth_rate DECIMAL(5,2),
  sentiment_score DECIMAL(3,2),
  platforms TEXT[],
  time_period TEXT,
  timestamp TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_trending_topics_keyword ON trending_topics(keyword);
CREATE INDEX IF NOT EXISTS idx_trending_topics_timestamp ON trending_topics(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_trending_topics_volume ON trending_topics(volume DESC);
CREATE INDEX IF NOT EXISTS idx_trending_topics_growth_rate ON trending_topics(growth_rate DESC);

-- Clear existing data
TRUNCATE TABLE trending_topics;

-- ============================================================
-- INSERT TRENDING TOPICS (100 entries)
-- ============================================================

-- WATER CRISIS KEYWORDS (25 entries - 25%)
INSERT INTO trending_topics (id, keyword, volume, growth_rate, sentiment_score, platforms, time_period, timestamp) VALUES
('a1b2c3d4-e5f6-4a7b-8c9d-000000000001', 'Chennai Water Crisis', 8432, 0.65, -0.45, ARRAY['twitter','facebook','news'], '24h', NOW() - INTERVAL '2 hours'),
('a1b2c3d4-e5f6-4a7b-8c9d-000000000002', 'Groundwater Depletion TN', 5678, 0.42, -0.52, ARRAY['twitter','news'], '24h', NOW() - INTERVAL '4 hours'),
('a1b2c3d4-e5f6-4a7b-8c9d-000000000003', 'Water Scarcity Tamil Nadu', 6234, 0.58, -0.38, ARRAY['facebook','instagram','news'], '24h', NOW() - INTERVAL '6 hours'),
('a1b2c3d4-e5f6-4a7b-8c9d-000000000004', 'Coimbatore Water Shortage', 4321, 0.71, -0.61, ARRAY['twitter','facebook'], '24h', NOW() - INTERVAL '8 hours'),
('a1b2c3d4-e5f6-4a7b-8c9d-000000000005', 'Tanker Water Prices', 3456, 0.85, -0.48, ARRAY['twitter','instagram'], '24h', NOW() - INTERVAL '10 hours'),
('a1b2c3d4-e5f6-4a7b-8c9d-000000000006', 'Metro Water Supply Crisis', 5012, 0.54, -0.42, ARRAY['twitter','news'], '7d', NOW() - INTERVAL '1 day'),
('a1b2c3d4-e5f6-4a7b-8c9d-000000000007', 'Chennai Desalination Plant', 2345, 0.28, -0.25, ARRAY['news'], '7d', NOW() - INTERVAL '1 day 3 hours'),
('a1b2c3d4-e5f6-4a7b-8c9d-000000000008', 'Madurai Water Scarcity', 3890, 0.63, -0.55, ARRAY['twitter','facebook'], '24h', NOW() - INTERVAL '1 day 6 hours'),
('a1b2c3d4-e5f6-4a7b-8c9d-000000000009', 'Salem Water Crisis', 2876, 0.47, -0.44, ARRAY['facebook','news'], '7d', NOW() - INTERVAL '1 day 12 hours'),
('a1b2c3d4-e5f6-4a7b-8c9d-000000000010', 'Trichy Water Shortage', 2543, 0.39, -0.37, ARRAY['twitter','instagram'], '7d', NOW() - INTERVAL '2 days'),
('a1b2c3d4-e5f6-4a7b-8c9d-000000000011', 'Vellore Groundwater Crisis', 1987, 0.52, -0.49, ARRAY['twitter','news'], '7d', NOW() - INTERVAL '2 days 6 hours'),
('a1b2c3d4-e5f6-4a7b-8c9d-000000000012', 'Erode Water Scarcity', 1765, 0.45, -0.41, ARRAY['facebook'], '30d', NOW() - INTERVAL '2 days 12 hours'),
('a1b2c3d4-e5f6-4a7b-8c9d-000000000013', 'Water Rationing Chennai', 4567, 0.68, -0.53, ARRAY['twitter','facebook','news'], '24h', NOW() - INTERVAL '3 days'),
('a1b2c3d4-e5f6-4a7b-8c9d-000000000014', 'Drought Tamil Nadu 2024', 3210, 0.35, -0.46, ARRAY['news'], '30d', NOW() - INTERVAL '3 days 8 hours'),
('a1b2c3d4-e5f6-4a7b-8c9d-000000000015', 'Borewells Dry Chennai', 2890, 0.72, -0.58, ARRAY['twitter','instagram'], '24h', NOW() - INTERVAL '3 days 16 hours'),
('a1b2c3d4-e5f6-4a7b-8c9d-000000000016', 'Water Table Depletion', 1543, 0.31, -0.35, ARRAY['news'], '30d', NOW() - INTERVAL '4 days'),
('a1b2c3d4-e5f6-4a7b-8c9d-000000000017', 'Tirunelveli Water Crisis', 2123, 0.56, -0.47, ARRAY['twitter','facebook'], '7d', NOW() - INTERVAL '4 days 8 hours'),
('a1b2c3d4-e5f6-4a7b-8c9d-000000000018', 'Water Mafia TN', 3456, 0.79, -0.62, ARRAY['twitter','news'], '24h', NOW() - INTERVAL '4 days 16 hours'),
('a1b2c3d4-e5f6-4a7b-8c9d-000000000019', 'Rainwater Harvesting TN', 987, 0.22, 0.15, ARRAY['instagram','news'], '30d', NOW() - INTERVAL '5 days'),
('a1b2c3d4-e5f6-4a7b-8c9d-000000000020', 'Lake Restoration Chennai', 1234, 0.18, 0.28, ARRAY['facebook','news'], '30d', NOW() - INTERVAL '5 days 12 hours'),
('a1b2c3d4-e5f6-4a7b-8c9d-000000000021', 'Water Conservation TN', 876, 0.15, 0.32, ARRAY['instagram'], '30d', NOW() - INTERVAL '6 days'),
('a1b2c3d4-e5f6-4a7b-8c9d-000000000022', 'Chennai Rivers Pollution', 2345, 0.48, -0.51, ARRAY['twitter','news'], '7d', NOW() - INTERVAL '6 days 8 hours'),
('a1b2c3d4-e5f6-4a7b-8c9d-000000000023', 'Cooum River Cleanup', 1456, 0.26, -0.22, ARRAY['facebook','news'], '30d', NOW() - INTERVAL '6 days 16 hours'),
('a1b2c3d4-e5f6-4a7b-8c9d-000000000024', 'Adyar River Encroachment', 1789, 0.41, -0.39, ARRAY['twitter','facebook'], '7d', NOW() - INTERVAL '7 days'),
('a1b2c3d4-e5f6-4a7b-8c9d-000000000025', 'Water Quality Testing TN', 654, 0.19, -0.28, ARRAY['news'], '30d', NOW() - INTERVAL '7 days'),

-- TVK/POLITICAL KEYWORDS (30 entries - 30%)
('b1c2d3e4-f5a6-4b7c-8d9e-000000000001', 'Vijay TVK', 15234, 1.22, 0.72, ARRAY['twitter','facebook','instagram','news'], '24h', NOW() - INTERVAL '1 hour'),
('b1c2d3e4-f5a6-4b7c-8d9e-000000000002', 'TVK Vision 2026', 12876, 0.98, 0.68, ARRAY['twitter','instagram','news'], '24h', NOW() - INTERVAL '3 hours'),
('b1c2d3e4-f5a6-4b7c-8d9e-000000000003', 'Vijay Political Entry', 14567, 1.15, 0.64, ARRAY['facebook','twitter','news'], '24h', NOW() - INTERVAL '5 hours'),
('b1c2d3e4-f5a6-4b7c-8d9e-000000000004', 'TVK Rally Chennai', 11234, 0.87, 0.76, ARRAY['twitter','instagram'], '24h', NOW() - INTERVAL '7 hours'),
('b1c2d3e4-f5a6-4b7c-8d9e-000000000005', 'Tamil Nadu Politics 2026', 9876, 0.76, 0.58, ARRAY['twitter','news'], '7d', NOW() - INTERVAL '9 hours'),
('b1c2d3e4-f5a6-4b7c-8d9e-000000000006', 'Vijay Political Strategy', 8543, 0.91, 0.61, ARRAY['facebook','news'], '7d', NOW() - INTERVAL '12 hours'),
('b1c2d3e4-f5a6-4b7c-8d9e-000000000007', 'TVK Manifesto', 7890, 0.68, 0.54, ARRAY['twitter','facebook'], '7d', NOW() - INTERVAL '15 hours'),
('b1c2d3e4-f5a6-4b7c-8d9e-000000000008', 'TVK Youth Movement', 6543, 0.82, 0.71, ARRAY['instagram','twitter'], '24h', NOW() - INTERVAL '18 hours'),
('b1c2d3e4-f5a6-4b7c-8d9e-000000000009', 'Vijay Speech Chennai', 10234, 1.05, 0.77, ARRAY['twitter','facebook','news'], '24h', NOW() - INTERVAL '1 day'),
('b1c2d3e4-f5a6-4b7c-8d9e-000000000010', 'TVK Cadre Training', 4567, 0.59, 0.66, ARRAY['facebook','instagram'], '7d', NOW() - INTERVAL '1 day 4 hours'),
('b1c2d3e4-f5a6-4b7c-8d9e-000000000011', 'Vijay Meets Farmers', 5678, 0.74, 0.69, ARRAY['twitter','news'], '24h', NOW() - INTERVAL '1 day 8 hours'),
('b1c2d3e4-f5a6-4b7c-8d9e-000000000012', 'TVK Social Justice', 6789, 0.65, 0.63, ARRAY['facebook','twitter'], '7d', NOW() - INTERVAL '1 day 12 hours'),
('b1c2d3e4-f5a6-4b7c-8d9e-000000000013', 'Vijay Anti-Corruption', 7234, 0.88, 0.74, ARRAY['twitter','instagram','news'], '24h', NOW() - INTERVAL '2 days'),
('b1c2d3e4-f5a6-4b7c-8d9e-000000000014', 'TVK Coimbatore Rally', 8901, 0.93, 0.78, ARRAY['twitter','facebook'], '24h', NOW() - INTERVAL '2 days 6 hours'),
('b1c2d3e4-f5a6-4b7c-8d9e-000000000015', 'Vijay vs DMK', 9345, 0.79, 0.42, ARRAY['twitter','news'], '7d', NOW() - INTERVAL '2 days 12 hours'),
('b1c2d3e4-f5a6-4b7c-8d9e-000000000016', 'Vijay vs ADMK', 8012, 0.71, 0.38, ARRAY['facebook','news'], '7d', NOW() - INTERVAL '3 days'),
('b1c2d3e4-f5a6-4b7c-8d9e-000000000017', 'TVK Alliance Talks', 5432, 0.56, 0.31, ARRAY['news'], '7d', NOW() - INTERVAL '3 days 8 hours'),
('b1c2d3e4-f5a6-4b7c-8d9e-000000000018', 'Vijay Tamil Identity', 6890, 0.84, 0.73, ARRAY['twitter','instagram'], '24h', NOW() - INTERVAL '3 days 16 hours'),
('b1c2d3e4-f5a6-4b7c-8d9e-000000000019', 'TVK Madurai Meeting', 4321, 0.67, 0.71, ARRAY['facebook','twitter'], '24h', NOW() - INTERVAL '4 days'),
('b1c2d3e4-f5a6-4b7c-8d9e-000000000020', 'Vijay Temple Visit', 3456, 0.44, 0.55, ARRAY['instagram','news'], '7d', NOW() - INTERVAL '4 days 8 hours'),
('b1c2d3e4-f5a6-4b7c-8d9e-000000000021', 'TVK Salem Campaign', 5678, 0.72, 0.69, ARRAY['twitter','facebook'], '24h', NOW() - INTERVAL '4 days 16 hours'),
('b1c2d3e4-f5a6-4b7c-8d9e-000000000022', 'Vijay Education Policy', 4789, 0.61, 0.64, ARRAY['news','twitter'], '7d', NOW() - INTERVAL '5 days'),
('b1c2d3e4-f5a6-4b7c-8d9e-000000000023', 'TVK Employment Promise', 6234, 0.78, 0.68, ARRAY['facebook','instagram'], '7d', NOW() - INTERVAL '5 days 12 hours'),
('b1c2d3e4-f5a6-4b7c-8d9e-000000000024', 'Vijay Healthcare Plan', 3890, 0.53, 0.59, ARRAY['news'], '30d', NOW() - INTERVAL '6 days'),
('b1c2d3e4-f5a6-4b7c-8d9e-000000000025', 'TVK Trichy Convention', 7123, 0.89, 0.75, ARRAY['twitter','facebook','news'], '24h', NOW() - INTERVAL '6 days 8 hours'),
('b1c2d3e4-f5a6-4b7c-8d9e-000000000026', 'Vijay vs BJP', 8456, 0.94, 0.48, ARRAY['twitter','instagram'], '7d', NOW() - INTERVAL '6 days 16 hours'),
('b1c2d3e4-f5a6-4b7c-8d9e-000000000027', 'TVK Flag Launch', 5901, 0.81, 0.79, ARRAY['instagram','twitter'], '24h', NOW() - INTERVAL '7 days'),
('b1c2d3e4-f5a6-4b7c-8d9e-000000000028', 'Vijay Economic Vision', 4567, 0.63, 0.62, ARRAY['news','facebook'], '30d', NOW() - INTERVAL '7 days'),
('b1c2d3e4-f5a6-4b7c-8d9e-000000000029', 'TVK Woman Empowerment', 3678, 0.57, 0.71, ARRAY['instagram','facebook'], '7d', NOW() - INTERVAL '7 days'),
('b1c2d3e4-f5a6-4b7c-8d9e-000000000030', 'Vijay Farmers Rights', 6012, 0.75, 0.73, ARRAY['twitter','news'], '7d', NOW() - INTERVAL '7 days'),

-- NEET KEYWORDS (15 entries - 15%)
('c1d2e3f4-a5b6-4c7d-8e9f-000000000001', 'NEET Opposition TN', 5892, 0.48, -0.42, ARRAY['twitter','facebook','news'], '7d', NOW() - INTERVAL '2 hours'),
('c1d2e3f4-a5b6-4c7d-8e9f-000000000002', 'Stop NEET', 6234, 0.52, -0.48, ARRAY['twitter','instagram'], '24h', NOW() - INTERVAL '6 hours'),
('c1d2e3f4-a5b6-4c7d-8e9f-000000000003', 'NEET Injustice', 4567, 0.45, -0.51, ARRAY['facebook','twitter'], '7d', NOW() - INTERVAL '12 hours'),
('c1d2e3f4-a5b6-4c7d-8e9f-000000000004', 'Tamil Nadu NEET Exemption', 5123, 0.38, -0.35, ARRAY['news','twitter'], '7d', NOW() - INTERVAL '1 day'),
('c1d2e3f4-a5b6-4c7d-8e9f-000000000005', 'Medical Admissions NEET', 3890, 0.29, -0.28, ARRAY['news'], '30d', NOW() - INTERVAL '1 day 12 hours'),
('c1d2e3f4-a5b6-4c7d-8e9f-000000000006', 'NEET Student Suicide', 4321, 0.67, -0.73, ARRAY['twitter','facebook','news'], '24h', NOW() - INTERVAL '2 days'),
('c1d2e3f4-a5b6-4c7d-8e9f-000000000007', 'NEET Coaching Mafia', 2876, 0.54, -0.58, ARRAY['twitter','news'], '7d', NOW() - INTERVAL '2 days 12 hours'),
('c1d2e3f4-a5b6-4c7d-8e9f-000000000008', 'Rural Students NEET', 3456, 0.41, -0.46, ARRAY['facebook','news'], '7d', NOW() - INTERVAL '3 days'),
('c1d2e3f4-a5b6-4c7d-8e9f-000000000009', 'NEET Protest Chennai', 4789, 0.59, -0.44, ARRAY['twitter','instagram','news'], '24h', NOW() - INTERVAL '4 days'),
('c1d2e3f4-a5b6-4c7d-8e9f-000000000010', 'Anti NEET Movement', 3678, 0.46, -0.39, ARRAY['facebook','twitter'], '7d', NOW() - INTERVAL '4 days 12 hours'),
('c1d2e3f4-a5b6-4c7d-8e9f-000000000011', 'NEET Alternative TN', 2345, 0.33, -0.12, ARRAY['news'], '30d', NOW() - INTERVAL '5 days'),
('c1d2e3f4-a5b6-4c7d-8e9f-000000000012', 'NEET Supreme Court', 5012, 0.44, -0.31, ARRAY['twitter','news'], '7d', NOW() - INTERVAL '5 days 12 hours'),
('c1d2e3f4-a5b6-4c7d-8e9f-000000000013', 'NEET vs State Rights', 4123, 0.37, -0.27, ARRAY['news','facebook'], '30d', NOW() - INTERVAL '6 days'),
('c1d2e3f4-a5b6-4c7d-8e9f-000000000014', 'NEET Coaching Fees', 2987, 0.49, -0.53, ARRAY['twitter','instagram'], '7d', NOW() - INTERVAL '6 days 12 hours'),
('c1d2e3f4-a5b6-4c7d-8e9f-000000000015', 'NEET Language Barrier', 3567, 0.42, -0.49, ARRAY['facebook','news'], '7d', NOW() - INTERVAL '7 days'),

-- CAUVERY DISPUTE (10 entries - 10%)
('d1e2f3a4-b5c6-4d7e-8f9a-000000000001', 'Cauvery Water Dispute', 4012, 0.38, -0.34, ARRAY['twitter','news'], '7d', NOW() - INTERVAL '4 hours'),
('d1e2f3a4-b5c6-4d7e-8f9a-000000000002', 'Karnataka Water Release', 3678, 0.42, -0.41, ARRAY['facebook','news'], '7d', NOW() - INTERVAL '10 hours'),
('d1e2f3a4-b5c6-4d7e-8f9a-000000000003', 'Delta Farmers Protest', 3234, 0.51, -0.48, ARRAY['twitter','facebook','news'], '24h', NOW() - INTERVAL '1 day'),
('d1e2f3a4-b5c6-4d7e-8f9a-000000000004', 'Cauvery Rights TN', 2890, 0.35, -0.29, ARRAY['twitter','news'], '7d', NOW() - INTERVAL '2 days'),
('d1e2f3a4-b5c6-4d7e-8f9a-000000000005', 'Cauvery Tribunal', 2456, 0.28, -0.22, ARRAY['news'], '30d', NOW() - INTERVAL '3 days'),
('d1e2f3a4-b5c6-4d7e-8f9a-000000000006', 'Thanjavur Farmers Cauvery', 3012, 0.45, -0.37, ARRAY['facebook','twitter'], '7d', NOW() - INTERVAL '4 days'),
('d1e2f3a4-b5c6-4d7e-8f9a-000000000007', 'Cauvery River Pollution', 1987, 0.31, -0.43, ARRAY['news','twitter'], '30d', NOW() - INTERVAL '5 days'),
('d1e2f3a4-b5c6-4d7e-8f9a-000000000008', 'Mettur Dam Water Level', 2543, 0.24, -0.18, ARRAY['news'], '30d', NOW() - INTERVAL '6 days'),
('d1e2f3a4-b5c6-4d7e-8f9a-000000000009', 'Cauvery Management Board', 2123, 0.19, -0.15, ARRAY['news','facebook'], '30d', NOW() - INTERVAL '6 days 12 hours'),
('d1e2f3a4-b5c6-4d7e-8f9a-000000000010', 'Cauvery Delta Agriculture', 1765, 0.16, -0.09, ARRAY['news'], '30d', NOW() - INTERVAL '7 days'),

-- JOBS/EMPLOYMENT (10 entries - 10%)
('e1f2a3b4-c5d6-4e7f-8a9b-000000000001', 'TN Unemployment', 4567, 0.33, -0.28, ARRAY['twitter','facebook'], '7d', NOW() - INTERVAL '5 hours'),
('e1f2a3b4-c5d6-4e7f-8a9b-000000000002', 'Jobs for Youth TN', 3890, 0.29, -0.21, ARRAY['instagram','twitter'], '7d', NOW() - INTERVAL '11 hours'),
('e1f2a3b4-c5d6-4e7f-8a9b-000000000003', 'IT Jobs Chennai', 5012, 0.25, 0.08, ARRAY['news','facebook'], '30d', NOW() - INTERVAL '1 day 2 hours'),
('e1f2a3b4-c5d6-4e7f-8a9b-000000000004', 'Manufacturing Jobs TN', 2876, 0.18, 0.05, ARRAY['news'], '30d', NOW() - INTERVAL '2 days'),
('e1f2a3b4-c5d6-4e7f-8a9b-000000000005', 'Government Jobs TN', 4321, 0.22, 0.12, ARRAY['facebook','twitter'], '30d', NOW() - INTERVAL '3 days'),
('e1f2a3b4-c5d6-4e7f-8a9b-000000000006', 'Startup Jobs Chennai', 2543, 0.31, 0.18, ARRAY['instagram','news'], '30d', NOW() - INTERVAL '4 days'),
('e1f2a3b4-c5d6-4e7f-8a9b-000000000007', 'TN Youth Unemployment Rate', 3678, 0.35, -0.32, ARRAY['twitter','news'], '7d', NOW() - INTERVAL '5 days'),
('e1f2a3b4-c5d6-4e7f-8a9b-000000000008', 'Skill Development TN', 1987, 0.15, 0.22, ARRAY['news','facebook'], '30d', NOW() - INTERVAL '6 days'),
('e1f2a3b4-c5d6-4e7f-8a9b-000000000009', 'Campus Placements TN', 2234, 0.19, 0.14, ARRAY['instagram','twitter'], '30d', NOW() - INTERVAL '6 days 12 hours'),
('e1f2a3b4-c5d6-4e7f-8a9b-000000000010', 'TN Employment Exchange', 1654, 0.12, -0.08, ARRAY['facebook'], '30d', NOW() - INTERVAL '7 days'),

-- FISHERMEN ISSUES (5 entries - 5%)
('f1a2b3c4-d5e6-4f7a-8b9c-000000000001', 'Fishermen Arrests SL Navy', 2876, 0.61, -0.58, ARRAY['twitter','facebook','news'], '24h', NOW() - INTERVAL '3 hours'),
('f1a2b3c4-d5e6-4f7a-8b9c-000000000002', 'TN Fishermen Rights', 2345, 0.47, -0.44, ARRAY['twitter','news'], '7d', NOW() - INTERVAL '1 day 3 hours'),
('f1a2b3c4-d5e6-4f7a-8b9c-000000000003', 'Rameswaram Fishermen', 1987, 0.52, -0.51, ARRAY['facebook','news'], '7d', NOW() - INTERVAL '3 days'),
('f1a2b3c4-d5e6-4f7a-8b9c-000000000004', 'Fishing Ban Tamil Nadu', 1654, 0.28, -0.35, ARRAY['news'], '30d', NOW() - INTERVAL '5 days'),
('f1a2b3c4-d5e6-4f7a-8b9c-000000000005', 'Coastal Fishermen Issues', 2123, 0.39, -0.42, ARRAY['twitter','facebook'], '7d', NOW() - INTERVAL '6 days'),

-- OTHERS (5 entries - 5%)
('g1b2c3d4-e5f6-4a7b-8c9d-000000000001', 'Chennai Air Pollution', 3456, 0.44, -0.39, ARRAY['twitter','news'], '7d', NOW() - INTERVAL '8 hours'),
('g1b2c3d4-e5f6-4a7b-8c9d-000000000002', 'TN Education Budget', 2890, 0.26, 0.18, ARRAY['news','facebook'], '30d', NOW() - INTERVAL '2 days'),
('g1b2c3d4-e5f6-4a7b-8c9d-000000000003', 'Chennai Metro Expansion', 4123, 0.32, 0.24, ARRAY['twitter','instagram','news'], '7d', NOW() - INTERVAL '3 days 6 hours'),
('g1b2c3d4-e5f6-4a7b-8c9d-000000000004', 'TN Road Safety', 2543, 0.21, -0.14, ARRAY['facebook','news'], '30d', NOW() - INTERVAL '5 days 12 hours'),
('g1b2c3d4-e5f6-4a7b-8c9d-000000000005', 'Tamil Nadu Smart Cities', 1987, 0.17, 0.21, ARRAY['news'], '30d', NOW() - INTERVAL '7 days');

-- ============================================================
-- VERIFICATION QUERIES
-- ============================================================

-- Count total records
-- SELECT COUNT(*) FROM trending_topics;

-- Top 10 trending topics by volume
-- SELECT keyword, volume, growth_rate, sentiment_score
-- FROM trending_topics
-- ORDER BY volume DESC
-- LIMIT 10;

-- Topics with highest growth rate
-- SELECT keyword, volume, growth_rate, sentiment_score
-- FROM trending_topics
-- ORDER BY growth_rate DESC
-- LIMIT 10;

-- Most negative sentiment topics
-- SELECT keyword, volume, sentiment_score
-- FROM trending_topics
-- ORDER BY sentiment_score ASC
-- LIMIT 10;

-- Most positive sentiment topics
-- SELECT keyword, volume, sentiment_score
-- FROM trending_topics
-- ORDER BY sentiment_score DESC
-- LIMIT 10;

-- Topics by time period
-- SELECT time_period, COUNT(*) as count
-- FROM trending_topics
-- GROUP BY time_period;

-- Topics by platform
-- SELECT UNNEST(platforms) as platform, COUNT(*) as count
-- FROM trending_topics
-- GROUP BY platform
-- ORDER BY count DESC;

-- ============================================================
-- END OF SEED FILE
-- ============================================================
