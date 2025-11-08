-- =====================================================
-- TV BROADCAST ANALYSIS - SEED DATA
-- =====================================================
-- Realistic seed data for Tamil Nadu TV channels and shows
-- Run this AFTER the schema migration
-- =====================================================

-- =====================================================
-- 1. SEED TV CHANNELS (Tamil Nadu + National)
-- =====================================================

INSERT INTO tv_channels (
  channel_code, name, language, type, viewership_count, credibility_score,
  bias, region, prime_time_start, prime_time_end, is_live, current_show, is_active
) VALUES
  -- Tamil News Channels
  ('sun-news', 'Sun News', 'Tamil', 'news', 3200000, 85.00, 'center', 'Tamil Nadu', '19:00', '23:00', true, 'News @ 9', true),
  ('puthiya-thalaimurai', 'Puthiya Thalaimurai', 'Tamil', 'news', 2800000, 88.00, 'center', 'Tamil Nadu', '18:30', '22:30', true, 'Prime Time', true),
  ('thanthi-tv', 'Thanthi TV', 'Tamil', 'news', 2600000, 86.00, 'center', 'Tamil Nadu', '19:00', '22:00', true, 'Evening Bulletin', true),
  ('news7-tamil', 'News7 Tamil', 'Tamil', 'news', 2200000, 84.00, 'center', 'Tamil Nadu', '19:00', '22:00', true, 'Prime Time News', true),
  ('polimer-news', 'Polimer News', 'Tamil', 'news', 2000000, 83.00, 'center', 'Tamil Nadu', '19:00', '22:30', true, 'Evening Report', true),

  -- National News Channels
  ('ndtv', 'NDTV', 'English', 'news', 4500000, 89.00, 'center', 'National', '19:00', '23:00', true, 'The 9 O''Clock News', true),
  ('aaj-tak', 'Aaj Tak', 'Hindi', 'news', 5200000, 82.00, 'center', 'National', '19:00', '23:00', true, 'Aaj Ki Baat', true),
  ('india-today', 'India Today', 'English', 'news', 3800000, 87.00, 'center', 'National', '19:00', '22:00', true, 'News Today', true),
  ('cnn-news18', 'CNN-News18', 'English', 'news', 3500000, 88.00, 'center', 'National', '19:00', '23:00', true, 'Viewpoint', true),
  ('times-now', 'Times Now', 'English', 'news', 3200000, 81.00, 'right', 'National', '19:00', '23:00', true, 'The NewsHour', true),

  -- Regional Entertainment
  ('sun-tv', 'Sun TV', 'Tamil', 'entertainment', 8500000, 90.00, 'neutral', 'Tamil Nadu', '19:30', '22:30', false, '', true),
  ('vijay-tv', 'Vijay TV', 'Tamil', 'entertainment', 7200000, 89.00, 'neutral', 'Tamil Nadu', '19:00', '23:00', false, '', true),
  ('zee-tamil', 'Zee Tamil', 'Tamil', 'entertainment', 6800000, 87.00, 'neutral', 'Tamil Nadu', '19:00', '22:30', false, '', true),
  ('colors-tamil', 'Colors Tamil', 'Tamil', 'entertainment', 5500000, 86.00, 'neutral', 'Tamil Nadu', '19:30', '22:30', false, '', true)
ON CONFLICT (channel_code) DO UPDATE SET
  viewership_count = EXCLUDED.viewership_count,
  credibility_score = EXCLUDED.credibility_score,
  is_live = EXCLUDED.is_live,
  current_show = EXCLUDED.current_show,
  updated_at = NOW();

-- =====================================================
-- 2. SEED TV SHOWS (Popular Tamil News Shows)
-- =====================================================

INSERT INTO tv_shows (
  channel_id, name, description, show_type, time_slot,
  day_of_week, duration_minutes, average_viewership,
  credibility_rating, anchor_name, is_active
)
SELECT
  c.id,
  show.name,
  show.description,
  show.show_type,
  show.time_slot,
  show.day_of_week,
  show.duration_minutes,
  show.average_viewership,
  show.credibility_rating,
  show.anchor_name,
  show.is_active
FROM (VALUES
  -- Sun News Shows
  ('sun-news', 'Kelvikku Enna Bathil', 'Political debate show with leaders', 'debate', '20:00-21:00', ARRAY['Monday','Tuesday','Wednesday','Thursday','Friday'], 60, 1200000, 87.00, 'Srivatsan', true),
  ('sun-news', 'News @ 9', 'Prime time news bulletin', 'news', '21:00-22:00', ARRAY['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'], 60, 2800000, 89.00, 'Rangaraj Pandey', true),

  -- Puthiya Thalaimurai Shows
  ('puthiya-thalaimurai', 'Kaalathin Kural', 'Evening political discussion', 'talk-show', '19:00-20:00', ARRAY['Monday','Tuesday','Wednesday','Thursday','Friday'], 60, 1500000, 91.00, 'Bhavani', true),
  ('puthiya-thalaimurai', 'Visaranai', 'Investigative journalism', 'documentary', '22:00-23:00', ARRAY['Saturday'], 60, 900000, 93.00, 'Sriram', true),

  -- Thanthi TV Shows
  ('thanthi-tv', 'Arattai Arangam', 'Public opinion show', 'talk-show', '20:00-21:00', ARRAY['Monday','Wednesday','Friday'], 60, 1100000, 86.00, 'Gayathri', true),
  ('thanthi-tv', 'Evening Bulletin', 'Prime time news', 'news', '21:00-22:00', ARRAY['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'], 60, 2400000, 88.00, 'Deepak', true),

  -- News7 Tamil Shows
  ('news7-tamil', 'Kelvi Neram', 'Political interview show', 'talk-show', '20:30-21:30', ARRAY['Tuesday','Thursday'], 60, 950000, 85.00, 'Karuna', true),

  -- NDTV Shows
  ('ndtv', 'Left Right & Centre', 'Political analysis', 'debate', '20:00-20:30', ARRAY['Monday','Tuesday','Wednesday','Thursday','Friday'], 30, 1800000, 92.00, 'Nidhi Razdan', true),
  ('ndtv', 'The 9 O''Clock News', 'Prime time news', 'news', '21:00-22:00', ARRAY['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'], 60, 4200000, 94.00, 'Ravish Kumar', true)
) AS show(channel_code, name, description, show_type, time_slot, day_of_week, duration_minutes, average_viewership, credibility_rating, anchor_name, is_active)
JOIN tv_channels c ON c.channel_code = show.channel_code
ON CONFLICT DO NOTHING;

-- =====================================================
-- 3. SEED BROADCAST SEGMENTS (Sample Recent Coverage)
-- =====================================================

-- Insert sample segments for today
INSERT INTO broadcast_segments (
  channel_id, show_id, channel_code, show_name, segment_title,
  broadcast_date, start_time, end_time, topic, description,
  mentions, political_parties, sentiment, sentiment_score,
  viewer_engagement_score, priority, is_flagged, data_source
)
SELECT
  c.id as channel_id,
  s.id as show_id,
  seg.channel_code,
  seg.show_name,
  seg.segment_title,
  seg.broadcast_date,
  seg.start_time,
  seg.end_time,
  seg.topic,
  seg.description,
  seg.mentions,
  seg.political_parties,
  seg.sentiment,
  seg.sentiment_score,
  seg.viewer_engagement_score,
  seg.priority,
  seg.is_flagged,
  'manual' as data_source
FROM (VALUES
  -- TVK Coverage Segments
  ('sun-news', 'News @ 9', 'TVK Party Formation Analysis', CURRENT_DATE, CURRENT_DATE + TIME '21:15:00', CURRENT_DATE + TIME '21:25:00', 'Actor Vijay launches TVK - Political Impact', 'Analysis of Tamilaga Vettri Kazhagam formation and its impact on Tamil Nadu politics', ARRAY['Vijay', 'Stalin', 'Annamalai'], ARRAY['TVK', 'DMK', 'BJP'], 'positive', 0.75, 92.00, 'high', false),

  ('puthiya-thalaimurai', 'Kaalathin Kural', 'TVK Ideology and Vision Discussion', CURRENT_DATE, CURRENT_DATE + TIME '19:30:00', CURRENT_DATE + TIME '19:50:00', 'TVK party manifesto expectations', 'Expert panel discusses expected policies and ideology of Vijay''s new party', ARRAY['Vijay', 'Seeman'], ARRAY['TVK', 'NTK'], 'neutral', 0.15, 88.00, 'high', false),

  ('thanthi-tv', 'Arattai Arangam', 'Public Opinion on TVK Entry', CURRENT_DATE - 1, CURRENT_DATE - 1 + TIME '20:30:00', CURRENT_DATE - 1 + TIME '20:50:00', 'Youth voters react to TVK', 'Ground report from college students about their views on Vijay entering politics', ARRAY['Vijay'], ARRAY['TVK'], 'positive', 0.68, 85.00, 'medium', false),

  -- DMK Coverage
  ('sun-news', 'Kelvikku Enna Bathil', 'DMK Government Welfare Schemes Review', CURRENT_DATE - 1, CURRENT_DATE - 1 + TIME '20:15:00', CURRENT_DATE - 1 + TIME '20:45:00', 'Analysis of DMK government performance', 'Discussion on welfare schemes implemented by DMK government in Tamil Nadu', ARRAY['Stalin', 'Udhayanidhi'], ARRAY['DMK'], 'neutral', 0.22, 76.00, 'medium', false),

  ('news7-tamil', 'Kelvi Neram', 'Stalin Interview Highlights', CURRENT_DATE - 2, CURRENT_DATE - 2 + TIME '20:45:00', CURRENT_DATE - 2 + TIME '21:15:00', 'CM Stalin on coalition politics', 'Exclusive interview with Chief Minister M.K. Stalin discussing alliances', ARRAY['Stalin', 'Rahul Gandhi'], ARRAY['DMK', 'Congress'], 'positive', 0.42, 91.00, 'high', false),

  -- BJP Coverage
  ('ndtv', 'Left Right & Centre', 'BJP Tamil Nadu Strategy Analysis', CURRENT_DATE, CURRENT_DATE + TIME '20:10:00', CURRENT_DATE + TIME '20:30:00', 'BJP attempts to expand in Tamil Nadu', 'Analysis of BJP strategies to gain foothold in Tamil Nadu politics', ARRAY['Annamalai', 'Modi'], ARRAY['BJP', 'AIADMK'], 'neutral', -0.08, 82.00, 'medium', false),

  -- Election Coverage
  ('puthiya-thalaimurai', 'Visaranai', 'Lok Sabha 2024 - Tamil Nadu Predictions', CURRENT_DATE - 3, CURRENT_DATE - 3 + TIME '22:15:00', CURRENT_DATE - 3 + TIME '22:55:00', 'Political analysts predict election outcomes', 'Detailed analysis of constituency-wise predictions for upcoming elections', ARRAY['Vijay', 'Stalin', 'Palaniswami'], ARRAY['TVK', 'DMK', 'AIADMK', 'BJP'], 'neutral', 0.05, 89.00, 'high', false),

  -- Social Issues
  ('thanthi-tv', 'Evening Bulletin', 'NEET Exam Controversy Debate', CURRENT_DATE - 4, CURRENT_DATE - 4 + TIME '21:20:00', CURRENT_DATE - 4 + TIME '21:40:00', 'Political parties stance on NEET', 'All parties'' positions on NEET exam abolition in Tamil Nadu', ARRAY['Stalin', 'Vijay', 'Ramadoss'], ARRAY['DMK', 'TVK', 'PMK'], 'negative', -0.35, 87.00, 'high', true),

  ('sun-news', 'News @ 9', 'Tamil Language Protection Bill', CURRENT_DATE - 5, CURRENT_DATE - 5 + TIME '21:35:00', CURRENT_DATE - 5 + TIME '21:50:00', 'Government introduces Tamil protection legislation', 'New bill to protect Tamil language in official communications', ARRAY['Stalin'], ARRAY['DMK'], 'positive', 0.82, 78.00, 'medium', false)

) AS seg(channel_code, show_name, segment_title, broadcast_date, start_time, end_time, topic, description, mentions, political_parties, sentiment, sentiment_score, viewer_engagement_score, priority, is_flagged)
JOIN tv_channels c ON c.channel_code = seg.channel_code
LEFT JOIN tv_shows s ON s.name = seg.show_name AND s.channel_id = c.id
ON CONFLICT DO NOTHING;

-- =====================================================
-- 4. SEED VIEWERSHIP DATA (Sample BARC Ratings)
-- =====================================================

INSERT INTO tv_viewership_data (
  channel_id, show_id, date, time_slot,
  viewership_count, tvr, reach_percentage,
  age_group, gender, region
)
SELECT
  c.id,
  s.id,
  CURRENT_DATE,
  '21:00-22:00',
  rating.viewership,
  rating.tvr,
  rating.reach,
  'all',
  'all',
  'Tamil Nadu'
FROM (VALUES
  ('sun-news', 'News @ 9', 2800000, 6.8, 42.5),
  ('puthiya-thalaimurai', 'Kaalathin Kural', 1500000, 3.6, 28.3),
  ('thanthi-tv', 'Evening Bulletin', 2400000, 5.8, 38.9),
  ('ndtv', 'The 9 O''Clock News', 4200000, 4.2, 35.7)
) AS rating(channel_code, show_name, viewership, tvr, reach)
JOIN tv_channels c ON c.channel_code = rating.channel_code
JOIN tv_shows s ON s.name = rating.show_name AND s.channel_id = c.id
ON CONFLICT DO NOTHING;

-- =====================================================
-- 5. GENERATE SENTIMENT TRENDS (Daily Aggregates)
-- =====================================================

INSERT INTO tv_sentiment_trends (
  channel_id, date, period_type,
  avg_sentiment_score, positive_count, neutral_count, negative_count, total_segments
)
SELECT
  c.id,
  CURRENT_DATE,
  'daily',
  AVG(b.sentiment_score),
  COUNT(*) FILTER (WHERE b.sentiment = 'positive'),
  COUNT(*) FILTER (WHERE b.sentiment = 'neutral'),
  COUNT(*) FILTER (WHERE b.sentiment = 'negative'),
  COUNT(*)
FROM broadcast_segments b
JOIN tv_channels c ON c.id = b.channel_id
WHERE b.broadcast_date = CURRENT_DATE
GROUP BY c.id
ON CONFLICT DO NOTHING;

-- =====================================================
-- VERIFICATION QUERY
-- =====================================================

-- Show what was inserted
SELECT
  'Channels' as table_name,
  COUNT(*) as total_rows
FROM tv_channels
UNION ALL
SELECT
  'Shows' as table_name,
  COUNT(*) as total_rows
FROM tv_shows
UNION ALL
SELECT
  'Broadcast Segments' as table_name,
  COUNT(*) as total_rows
FROM broadcast_segments
UNION ALL
SELECT
  'Viewership Data' as table_name,
  COUNT(*) as total_rows
FROM tv_viewership_data;

-- Show recent segments
SELECT
  c.name as channel,
  s.name as show,
  b.segment_title,
  b.sentiment,
  b.sentiment_score,
  b.priority,
  string_agg(DISTINCT unnest, ', ') as mentions
FROM broadcast_segments b
JOIN tv_channels c ON c.id = b.channel_id
LEFT JOIN tv_shows s ON s.id = b.show_id
CROSS JOIN LATERAL unnest(b.mentions) as unnest
GROUP BY c.name, s.name, b.segment_title, b.sentiment, b.sentiment_score, b.priority, b.broadcast_date
ORDER BY b.broadcast_date DESC
LIMIT 10;

-- =====================================================
-- SEED DATA COMPLETE
-- =====================================================
