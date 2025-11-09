-- ============================================================
-- ALERTS SEED DATA
-- ============================================================
-- Purpose: Generate 50 realistic political alerts for Tamil Nadu
-- Alert Types: Sentiment spike (40%), Crisis (30%), Competitor (15%), Viral (10%), System (5%)
-- Severity: Critical (10%), High (20%), Medium (40%), Low (30%)
-- Time Range: Last 48 hours
-- Usage: Run via Supabase SQL Editor or psql
-- ============================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create alerts table
CREATE TABLE IF NOT EXISTS alerts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title TEXT NOT NULL,
  description TEXT,
  severity TEXT CHECK (severity IN ('low','medium','high','critical')),
  type TEXT CHECK (type IN ('sentiment_spike','crisis','competitor_activity','viral','system')),
  status TEXT DEFAULT 'active' CHECK (status IN ('active','acknowledged','resolved')),
  timestamp TIMESTAMPTZ DEFAULT NOW(),
  ward TEXT,
  district TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_type ON alerts(type);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_district ON alerts(district);

-- Clear existing data
TRUNCATE TABLE alerts;

-- ============================================================
-- INSERT ALERTS (50 entries)
-- ============================================================

-- CRITICAL ALERTS (5 entries - 10%)
INSERT INTO alerts (id, title, description, severity, type, status, timestamp, ward, district) VALUES
('c1r2i3t4-i5c6-4a7l-8a9l-000000000001',
 'CRITICAL: Negative sentiment crash Coimbatore water crisis',
 'Sentiment dropped 65% in 6 hours due to water crisis escalation. Groundwater depletion protests intensifying across 12 wards. Immediate response required - recommend water tanker deployment and public address by local officials.',
 'critical', 'sentiment_spike', 'active', NOW() - INTERVAL '2 hours', 'Ward-23', 'Coimbatore'),

('c1r2i3t4-i5c6-4a7l-8a9l-000000000002',
 'CRITICAL: Viral post NEET student suicide - 15K shares',
 'Social media viral post about NEET-related student suicide in Ariyalur gaining massive traction - 15,000 shares in 2 hours. Negative sentiment at -0.82. Anti-NEET protests likely to intensify. Recommend crisis communication strategy and counseling helpline announcement.',
 'critical', 'viral', 'active', NOW() - INTERVAL '4 hours', 'Ward-7', 'Ariyalur'),

('c1r2i3t4-i5c6-4a7l-8a9l-000000000003',
 'CRITICAL: Water mafia violence Chennai - media coverage spike',
 'Reports of violence involving water tanker mafia in Chennai North spreading rapidly. 8 mainstream news outlets covering. Public anger trending on Twitter. Law enforcement intervention needed immediately.',
 'critical', 'crisis', 'acknowledged', NOW() - INTERVAL '6 hours', 'Ward-45', 'Chennai'),

('c1r2i3t4-i5c6-4a7l-8a9l-000000000004',
 'CRITICAL: TVK rally crowd estimate 50K+ exceeds permit',
 'TVK rally in Chennai Marina Beach showing 50,000+ attendance, exceeding permitted 25,000. Traffic gridlock reported on major arterial roads. Recommend immediate crowd management and public transport rerouting.',
 'critical', 'competitor_activity', 'active', NOW() - INTERVAL '8 hours', NULL, 'Chennai'),

('c1r2i3t4-i5c6-4a7l-8a9l-000000000005',
 'CRITICAL: Fishermen arrests by Sri Lanka Navy - 23 boats seized',
 'Mass arrests of Tamil Nadu fishermen by Sri Lankan Navy - 23 boats seized, 87 fishermen detained. Protests erupting in Rameswaram. Sentiment at -0.78. Federal intervention and diplomatic response urgently needed.',
 'critical', 'crisis', 'active', NOW() - INTERVAL '10 hours', NULL, 'Ramanathapuram'),

-- HIGH SEVERITY ALERTS (10 entries - 20%)
('h1i2g3h4-a5l6-4e7r-8t9s-000000000001',
 'HIGH: Fishermen protest escalating Ramanathapuram - 500+ participants',
 'Protest against Sri Lankan Navy arrests growing rapidly. 500+ fishermen and families blocking coastal highway. Media coverage increasing. Recommend immediate dialogue with fishermen associations and government statement.',
 'high', 'crisis', 'active', NOW() - INTERVAL '3 hours', 'Ward-12', 'Ramanathapuram'),

('h1i2g3h4-a5l6-4e7r-8t9s-000000000002',
 'HIGH: TVK negative trend Thanjavur constituency - down 15%',
 'Sentiment for TVK declining in Thanjavur constituency - down 15% over 24 hours. Competitor DMK gaining ground with agrarian welfare announcements. Delta farmer outreach campaign needed urgently.',
 'high', 'sentiment_spike', 'active', NOW() - INTERVAL '5 hours', NULL, 'Thanjavur'),

('h1i2g3h4-a5l6-4e7r-8t9s-000000000003',
 'HIGH: Cauvery water dispute mentions up 300% - Karnataka row',
 'Cauvery water sharing dispute mentions surged 300% following Karnataka CM statements on reducing releases. Delta farmers planning state-wide protests. Immediate coordination with Central government needed.',
 'high', 'sentiment_spike', 'active', NOW() - INTERVAL '7 hours', NULL, 'Nagapattinam'),

('h1i2g3h4-a5l6-4e7r-8t9s-000000000004',
 'HIGH: Water tanker prices surge 200% in Madurai',
 'Private water tanker prices increased 200% overnight in Madurai due to acute shortage. Public outrage building. Price control measures and government tanker deployment urgently required.',
 'high', 'crisis', 'acknowledged', NOW() - INTERVAL '12 hours', 'Ward-34', 'Madurai'),

('h1i2g3h4-a5l6-4e7r-8t9s-000000000005',
 'HIGH: DMK rally scheduled Chennai - 5,000 expected attendance',
 'Opposition DMK planning major rally in Chennai tomorrow with 5,000 expected attendees. Focus on water crisis failures and NEET opposition. Counter-messaging strategy needed.',
 'high', 'competitor_activity', 'active', NOW() - INTERVAL '1 day', NULL, 'Chennai'),

('h1i2g3h4-a5l6-4e7r-8t9s-000000000006',
 'HIGH: NEET opposition hashtag trending - student mobilization',
 'Anti-NEET hashtag #StopNEETNow trending nationally with 45K tweets. Student organizations planning coordinated protests across TN colleges. Monitor student sentiment and prepare policy statement.',
 'high', 'viral', 'active', NOW() - INTERVAL '1 day 2 hours', NULL, 'Chennai'),

('h1i2g3h4-a5l6-4e7r-8t9s-000000000007',
 'HIGH: Unemployment sentiment negative spike Salem youth',
 'Negative sentiment spike among youth regarding employment opportunities in Salem. IT park delay and manufacturing layoffs driving frustration. Youth engagement programs and jobs announcement recommended.',
 'high', 'sentiment_spike', 'active', NOW() - INTERVAL '1 day 6 hours', 'Ward-18', 'Salem'),

('h1i2g3h4-a5l6-4e7r-8t9s-000000000008',
 'HIGH: Groundwater depletion crisis Vellore - borewells dry',
 'Groundwater crisis intensifying in Vellore - 60% of borewells reported dry. Agricultural operations halted in 8 villages. Emergency water supply and alternate irrigation support needed.',
 'high', 'crisis', 'active', NOW() - INTERVAL '1 day 8 hours', 'Ward-29', 'Vellore'),

('h1i2g3h4-a5l6-4e7r-8t9s-000000000009',
 'HIGH: TVK manifesto leak on social media - authenticity disputed',
 'Alleged TVK manifesto document leaked on social media platforms. Authenticity disputed but generating significant discussion. Official clarification statement needed to control narrative.',
 'high', 'viral', 'acknowledged', NOW() - INTERVAL '1 day 12 hours', NULL, NULL),

('h1i2g3h4-a5l6-4e7r-8t9s-000000000010',
 'HIGH: ADMK alliance speculation viral - BJP coordination rumors',
 'Social media speculation about ADMK-BJP alliance coordination going viral. Sentiment mixed among traditional ADMK voters. Clarification on alliance strategy may be needed.',
 'high', 'competitor_activity', 'active', NOW() - INTERVAL '1 day 16 hours', NULL, NULL),

-- MEDIUM SEVERITY ALERTS (20 entries - 40%)
('m1e2d3i4-u5m6-4a7l-8e9r-000000000001',
 'MEDIUM: Healthcare sentiment declining Salem district',
 'Public healthcare sentiment declining in Salem district due to staff shortages at government hospitals. 18% drop in satisfaction scores over 2 weeks. Service quality improvements needed.',
 'medium', 'sentiment_spike', 'active', NOW() - INTERVAL '4 hours', NULL, 'Salem'),

('m1e2d3i4-u5m6-4a7l-8e9r-000000000002',
 'MEDIUM: DMK Coimbatore event scheduled - infrastructure focus',
 'DMK organizing infrastructure development seminar in Coimbatore with local corporators. Expected 200-300 attendees. Monitor messaging around Metro expansion promises.',
 'medium', 'competitor_activity', 'active', NOW() - INTERVAL '6 hours', NULL, 'Coimbatore'),

('m1e2d3i4-u5m6-4a7l-8e9r-000000000003',
 'MEDIUM: NEET coaching fees criticism trending Trichy',
 'Parents in Trichy expressing frustration over skyrocketing NEET coaching fees. Local media coverage increasing. Education affordability messaging opportunity.',
 'medium', 'sentiment_spike', 'active', NOW() - INTERVAL '9 hours', 'Ward-51', 'Tiruchirappalli'),

('m1e2d3i4-u5m6-4a7l-8e9r-000000000004',
 'MEDIUM: Cooum River pollution complaints surge Chennai',
 'Cooum River pollution complaints increased 45% following monsoon. Residents demanding cleanup acceleration. Environmental action update recommended.',
 'medium', 'crisis', 'acknowledged', NOW() - INTERVAL '14 hours', 'Ward-38', 'Chennai'),

('m1e2d3i4-u5m6-4a7l-8e9r-000000000005',
 'MEDIUM: TVK youth wing recruitment drive viral videos',
 'TVK youth wing recruitment drive videos gaining traction on Instagram - 50K views. Positive sentiment among 18-25 demographic. Continue youth engagement strategy.',
 'medium', 'viral', 'active', NOW() - INTERVAL '18 hours', NULL, NULL),

('m1e2d3i4-u5m6-4a7l-8e9r-000000000006',
 'MEDIUM: Metro Water supply schedule change confusion',
 'Confusion and complaints about Metro Water supply schedule changes in North Chennai. Clearer communication needed to residents about timing adjustments.',
 'medium', 'crisis', 'active', NOW() - INTERVAL '1 day', 'Ward-42', 'Chennai'),

('m1e2d3i4-u5m6-4a7l-8e9r-000000000007',
 'MEDIUM: TVK farmer outreach event Thanjavur announced',
 'TVK announced farmer outreach event in Thanjavur delta region for next week. Expected 1,000 farmers. Delta-specific agricultural policies should be highlighted.',
 'medium', 'competitor_activity', 'active', NOW() - INTERVAL '1 day 4 hours', NULL, 'Thanjavur'),

('m1e2d3i4-u5m6-4a7l-8e9r-000000000008',
 'MEDIUM: Education budget allocation criticism increasing',
 'Criticism of state education budget allocation increasing among teacher associations. Moderate negative sentiment. Engagement with education stakeholders recommended.',
 'medium', 'sentiment_spike', 'active', NOW() - INTERVAL '1 day 8 hours', NULL, NULL),

('m1e2d3i4-u5m6-4a7l-8e9r-000000000009',
 'MEDIUM: Chennai Metro Phase 2 delay complaints',
 'Public complaints about Chennai Metro Phase 2 construction delays increasing. Infrastructure progress updates needed to manage expectations.',
 'medium', 'sentiment_spike', 'active', NOW() - INTERVAL '1 day 10 hours', NULL, 'Chennai'),

('m1e2d3i4-u5m6-4a7l-8e9r-000000000010',
 'MEDIUM: BJP TN unit social media campaign launch',
 'BJP Tamil Nadu unit launched coordinated social media campaign on Central government schemes. Moderate engagement. Monitor messaging effectiveness.',
 'medium', 'competitor_activity', 'active', NOW() - INTERVAL '1 day 12 hours', NULL, NULL),

('m1e2d3i4-u5m6-4a7l-8e9r-000000000011',
 'MEDIUM: Skill development program sentiment positive Madurai',
 'Positive sentiment emerging around new skill development programs in Madurai. 32% approval among youth. Amplify success stories for broader reach.',
 'medium', 'sentiment_spike', 'active', NOW() - INTERVAL '1 day 14 hours', 'Ward-27', 'Madurai'),

('m1e2d3i4-u5m6-4a7l-8e9r-000000000012',
 'MEDIUM: Cauvery delta irrigation complaints Nagapattinam',
 'Farmers in Nagapattinam expressing concerns about irrigation water availability. Moderate negative sentiment. Coordination with water resources department needed.',
 'medium', 'crisis', 'active', NOW() - INTERVAL '1 day 16 hours', NULL, 'Nagapattinam'),

('m1e2d3i4-u5m6-4a7l-8e9r-000000000013',
 'MEDIUM: NEET language barrier discussion forum viral',
 'Online forum discussion about NEET Tamil language option gaining engagement. 8K participants. Education equity messaging opportunity.',
 'medium', 'viral', 'active', NOW() - INTERVAL '1 day 18 hours', NULL, NULL),

('m1e2d3i4-u5m6-4a7l-8e9r-000000000014',
 'MEDIUM: Road safety concerns increasing Erode',
 'Road safety concerns increasing in Erode following recent accidents on NH-544. Infrastructure improvement announcements could address sentiment.',
 'medium', 'sentiment_spike', 'active', NOW() - INTERVAL '1 day 20 hours', NULL, 'Erode'),

('m1e2d3i4-u5m6-4a7l-8e9r-000000000015',
 'MEDIUM: TVK Tamil identity messaging resonating youth',
 'TVK Tamil cultural identity messaging showing strong resonance among urban youth. Positive sentiment at +0.58. Cultural events could amplify this trend.',
 'medium', 'viral', 'active', NOW() - INTERVAL '1 day 22 hours', NULL, NULL),

('m1e2d3i4-u5m6-4a7l-8e9r-000000000016',
 'MEDIUM: Manufacturing jobs decline Hosur industrial area',
 'Reports of manufacturing jobs decline in Hosur industrial area causing concern. Youth employment messaging should address this sector.',
 'medium', 'sentiment_spike', 'acknowledged', NOW() - INTERVAL '2 days', NULL, 'Krishnagiri'),

('m1e2d3i4-u5m6-4a7l-8e9r-000000000017',
 'MEDIUM: DMK social welfare scheme announcement Salem',
 'DMK announced new social welfare scheme focusing on Salem district women. Moderate positive reception. Monitor competitive positioning.',
 'medium', 'competitor_activity', 'active', NOW() - INTERVAL '2 days 2 hours', NULL, 'Salem'),

('m1e2d3i4-u5m6-4a7l-8e9r-000000000018',
 'MEDIUM: Lake restoration progress positive sentiment',
 'Positive sentiment emerging around Chennai lake restoration projects. 41% approval rating. Environmental achievements should be highlighted.',
 'medium', 'sentiment_spike', 'active', NOW() - INTERVAL '2 days 4 hours', NULL, 'Chennai'),

('m1e2d3i4-u5m6-4a7l-8e9r-000000000019',
 'MEDIUM: Fishing ban period complaints Tuticorin',
 'Fishermen in Tuticorin expressing concerns about extended fishing ban period. Livelihood support messaging needed during ban season.',
 'medium', 'crisis', 'active', NOW() - INTERVAL '2 days 6 hours', NULL, 'Thoothukudi'),

('m1e2d3i4-u5m6-4a7l-8e9r-000000000020',
 'MEDIUM: Government job recruitment positive response',
 'Positive response to recent government job recruitment announcement. 52% approval among job seekers. Continue employment opportunity messaging.',
 'medium', 'sentiment_spike', 'active', NOW() - INTERVAL '2 days 8 hours', NULL, NULL),

-- LOW SEVERITY ALERTS (15 entries - 30%)
('l1o2w3s4-e5v6-4e7r-8i9t-000000000001',
 'LOW: Infrastructure complaints Tiruchirappalli ward-level',
 'Minor increase in ward-level infrastructure maintenance complaints in Tiruchirappalli. Standard service request volumes. Monitor for escalation.',
 'low', 'sentiment_spike', 'active', NOW() - INTERVAL '5 hours', 'Ward-44', 'Tiruchirappalli'),

('l1o2w3s4-e5v6-4e7r-8i9t-000000000002',
 'LOW: Positive TVK sentiment Coimbatore youth segment',
 'Slight uptick in positive TVK sentiment among Coimbatore college students. Small but consistent trend. Continue youth engagement activities.',
 'low', 'sentiment_spike', 'active', NOW() - INTERVAL '11 hours', NULL, 'Coimbatore'),

('l1o2w3s4-e5v6-4e7r-8i9t-000000000003',
 'LOW: Local temple festival positive coverage',
 'Positive local media coverage of TVK cadre participation in temple festival community service. Good grassroots visibility.',
 'low', 'viral', 'active', NOW() - INTERVAL '16 hours', 'Ward-15', 'Madurai'),

('l1o2w3s4-e5v6-4e7r-8i9t-000000000004',
 'LOW: Bus service improvement requests Vellore',
 'Routine requests for bus service frequency improvement in Vellore suburban areas. Standard public transport feedback.',
 'low', 'sentiment_spike', 'active', NOW() - INTERVAL '1 day 2 hours', NULL, 'Vellore'),

('l1o2w3s4-e5v6-4e7r-8i9t-000000000005',
 'LOW: Street lighting complaints minor ward',
 'Minor street lighting maintenance complaints in single ward. Routine municipal service issue.',
 'low', 'crisis', 'resolved', NOW() - INTERVAL '1 day 8 hours', 'Ward-31', 'Chennai'),

('l1o2w3s4-e5v6-4e7r-8i9t-000000000006',
 'LOW: ADMK local event low attendance reported',
 'ADMK local organizational event showed lower than expected attendance in Tirunelveli. Limited strategic impact.',
 'low', 'competitor_activity', 'active', NOW() - INTERVAL '1 day 14 hours', NULL, 'Tirunelveli'),

('l1o2w3s4-e5v6-4e7r-8i9t-000000000007',
 'LOW: Rainwater harvesting awareness positive',
 'Positive sentiment toward rainwater harvesting awareness campaigns. Small but engaged audience. Environmental messaging effective.',
 'low', 'sentiment_spike', 'active', NOW() - INTERVAL '1 day 18 hours', NULL, 'Chennai'),

('l1o2w3s4-e5v6-4e7r-8i9t-000000000008',
 'LOW: Smart city initiative discussions Coimbatore',
 'Online discussions about Smart City initiatives in Coimbatore showing mild interest. Moderate engagement levels.',
 'low', 'viral', 'active', NOW() - INTERVAL '2 days', NULL, 'Coimbatore'),

('l1o2w3s4-e5v6-4e7r-8i9t-000000000009',
 'LOW: Women empowerment program feedback positive',
 'Positive feedback from women empowerment program participants. Small sample size but encouraging sentiment.',
 'low', 'sentiment_spike', 'active', NOW() - INTERVAL '2 days 4 hours', 'Ward-22', 'Salem'),

('l1o2w3s4-e5v6-4e7r-8i9t-000000000010',
 'LOW: BJP minor social media engagement increase',
 'Slight increase in BJP social media engagement in TN. Minimal impact on overall political landscape.',
 'low', 'competitor_activity', 'active', NOW() - INTERVAL '2 days 8 hours', NULL, NULL),

('l1o2w3s4-e5v6-4e7r-8i9t-000000000011',
 'LOW: Park maintenance appreciation posts',
 'Social media posts appreciating recent park maintenance work. Positive community sentiment.',
 'low', 'viral', 'active', NOW() - INTERVAL '2 days 12 hours', 'Ward-17', 'Chennai'),

('l1o2w3s4-e5v6-4e7r-8i9t-000000000012',
 'LOW: Garbage collection schedule feedback',
 'Minor feedback about garbage collection schedule adjustments. Routine municipal communication issue.',
 'low', 'crisis', 'acknowledged', NOW() - INTERVAL '2 days 16 hours', 'Ward-28', 'Madurai'),

('l1o2w3s4-e5v6-4e7r-8i9t-000000000013',
 'LOW: Sports facility improvement discussions',
 'Community discussions about local sports facility improvements. Standard infrastructure development interest.',
 'low', 'sentiment_spike', 'active', NOW() - INTERVAL '2 days 18 hours', NULL, 'Tiruchirappalli'),

('l1o2w3s4-e5v6-4e7r-8i9t-000000000014',
 'LOW: System maintenance scheduled notification',
 'Scheduled system maintenance for sentiment monitoring platform tonight 11 PM - 2 AM. Standard maintenance window.',
 'low', 'system', 'active', NOW() - INTERVAL '2 days 20 hours', NULL, NULL),

('l1o2w3s4-e5v6-4e7r-8i9t-000000000015',
 'LOW: Data backup completion successful',
 'Automated daily data backup completed successfully. All sentiment analytics data secured. System health normal.',
 'low', 'system', 'resolved', NOW() - INTERVAL '2 days 22 hours', NULL, NULL);

-- ============================================================
-- VERIFICATION QUERIES
-- ============================================================

-- Count total alerts
-- SELECT COUNT(*) FROM alerts;

-- Alerts by severity
-- SELECT severity, COUNT(*) as count
-- FROM alerts
-- GROUP BY severity
-- ORDER BY CASE severity
--   WHEN 'critical' THEN 1
--   WHEN 'high' THEN 2
--   WHEN 'medium' THEN 3
--   WHEN 'low' THEN 4
-- END;

-- Alerts by type
-- SELECT type, COUNT(*) as count
-- FROM alerts
-- GROUP BY type
-- ORDER BY count DESC;

-- Alerts by status
-- SELECT status, COUNT(*) as count
-- FROM alerts
-- GROUP BY status;

-- Critical and High severity alerts
-- SELECT title, severity, type, timestamp, district
-- FROM alerts
-- WHERE severity IN ('critical', 'high')
-- ORDER BY timestamp DESC;

-- Recent alerts (last 24 hours)
-- SELECT title, severity, type, timestamp
-- FROM alerts
-- WHERE timestamp > NOW() - INTERVAL '24 hours'
-- ORDER BY timestamp DESC;

-- Alerts by district
-- SELECT district, COUNT(*) as count
-- FROM alerts
-- WHERE district IS NOT NULL
-- GROUP BY district
-- ORDER BY count DESC;

-- Active critical alerts requiring immediate action
-- SELECT title, description, timestamp, ward, district
-- FROM alerts
-- WHERE severity = 'critical'
--   AND status = 'active'
-- ORDER BY timestamp DESC;

-- ============================================================
-- END OF SEED FILE
-- ============================================================
