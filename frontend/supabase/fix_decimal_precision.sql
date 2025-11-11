-- =====================================================
-- FIX DECIMAL PRECISION OVERFLOW
-- =====================================================
-- Run this if you already created the tables with wrong precision
-- This will alter existing tables to support values up to 100.00
-- =====================================================

-- Option 1: Drop and recreate (if tables are empty or you don't care about data)
DROP TABLE IF EXISTS tv_sentiment_trends CASCADE;
DROP TABLE IF EXISTS tv_viewership_data CASCADE;
DROP TABLE IF EXISTS broadcast_segments CASCADE;
DROP TABLE IF EXISTS tv_shows CASCADE;
DROP TABLE IF EXISTS tv_channels CASCADE;

-- Now re-run the schema migration: 20251109_tv_broadcast_schema.sql

-- =====================================================
-- OR Option 2: Alter existing tables (if you want to keep data)
-- Uncomment below if you have data you want to keep
-- =====================================================

/*
-- Fix tv_channels table
ALTER TABLE tv_channels
  ALTER COLUMN credibility_score TYPE DECIMAL(5,2);

-- Fix tv_shows table
ALTER TABLE tv_shows
  ALTER COLUMN credibility_rating TYPE DECIMAL(5,2),
  ALTER COLUMN guest_influence_score TYPE DECIMAL(5,2);

-- No changes needed for other tables
*/
