-- =====================================================
-- VOTER SEGMENTS & DEMOGRAPHICS
-- Tamil Nadu Voter Classification for Campaign Targeting
-- Date: 2025-11-08
-- =====================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- 1. VOTER SEGMENTS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS voter_segments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    segment_code TEXT UNIQUE NOT NULL,
    segment_name TEXT NOT NULL,
    segment_name_tamil TEXT NOT NULL,
    description TEXT,

    -- Classification
    segment_category TEXT NOT NULL,           -- 'Age', 'Occupation', 'Income', 'Social', 'Religion', 'Gender', 'Geography'
    parent_segment TEXT,                      -- For hierarchical grouping

    -- Targeting strategy
    key_issues TEXT[],                        -- Main concerns of this segment
    preferred_channels TEXT[],                -- How to reach them
    messaging_strategy TEXT,
    communication_style TEXT,                 -- 'Formal', 'Casual', 'Emotional', 'Data-driven'

    -- Size estimates (Tamil Nadu)
    estimated_voters BIGINT,
    percentage_of_electorate DECIMAL(5,2),

    -- Political behavior
    voting_pattern TEXT,                      -- 'Swing', 'Loyal', 'First-time', 'Irregular'
    traditional_leaning TEXT,                 -- 'DMK', 'AIADMK', 'Neutral', 'Anti-incumbent'
    influence_level TEXT CHECK (influence_level IN ('High', 'Medium', 'Low')),

    -- Priority for TVK
    tvk_priority TEXT CHECK (tvk_priority IN ('Critical', 'High', 'Medium', 'Low')),
    tvk_win_probability DECIMAL(3,2),        -- 0.00 to 1.00

    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,

    -- Multi-tenancy
    tenant_id TEXT,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,

    -- Constraints
    CONSTRAINT valid_category CHECK (segment_category IN (
        'Age', 'Occupation', 'Income', 'Social', 'Religion',
        'Gender', 'Geography', 'Education', 'Behavior'
    ))
);

-- Create indexes
CREATE INDEX idx_voter_segments_code ON voter_segments(segment_code);
CREATE INDEX idx_voter_segments_category ON voter_segments(segment_category);
CREATE INDEX idx_voter_segments_priority ON voter_segments(tvk_priority);
CREATE INDEX idx_voter_segments_active ON voter_segments(is_active);

-- =====================================================
-- 2. INSERT VOTER SEGMENTS - AGE-BASED
-- =====================================================

INSERT INTO voter_segments (
    segment_code, segment_name, segment_name_tamil, description,
    segment_category, key_issues, preferred_channels, messaging_strategy,
    estimated_voters, percentage_of_electorate, voting_pattern,
    traditional_leaning, influence_level, tvk_priority, tvk_win_probability
) VALUES

-- Youth (18-25) - CRITICAL for TVK (Vijay's fan base)
(
    'AGE_18_25',
    'Youth (18-25)',
    'இளைஞர்கள் (18-25)',
    'First-time and young voters, highly influenced by cinema and social media',
    'Age',
    ARRAY['Jobs', 'Education', 'Technology', 'Entertainment', 'Future Opportunities'],
    ARRAY['Instagram', 'Twitter', 'YouTube', 'TikTok', 'College Campaigns', 'Film Events'],
    'High-energy, aspirational messaging. Focus on change, innovation, and future. Use Vijay''s star power.',
    8500000,
    13.5,
    'Swing',
    'Neutral',
    'High',
    'Critical',
    0.75
),

-- Young Adults (26-35) - HIGH priority
(
    'AGE_26_35',
    'Young Adults (26-35)',
    'இளம் வயதினர் (26-35)',
    'Young professionals and families, career-focused, tech-savvy',
    'Age',
    ARRAY['Jobs', 'Housing', 'Healthcare', 'Child Education', 'Start-up Ecosystem'],
    ARRAY['Social Media', 'WhatsApp', 'LinkedIn', 'Door-to-door', 'Town Halls'],
    'Professional, solution-oriented. Focus on economic development, career growth, quality of life.',
    12000000,
    19.0,
    'Swing',
    'Neutral',
    'High',
    'High',
    0.65
),

-- Middle Age (36-50) - MEDIUM priority
(
    'AGE_36_50',
    'Middle Age (36-50)',
    'நடுத்தர வயதினர் (36-50)',
    'Established careers, family responsibilities, seeking stability',
    'Age',
    ARRAY['Economy', 'Children Education', 'Healthcare', 'Law & Order', 'Infrastructure'],
    ARRAY['TV', 'Newspaper', 'WhatsApp', 'Public Meetings', 'Community Events'],
    'Balanced, rational. Focus on governance track record, family welfare, economic stability.',
    15000000,
    23.8,
    'Regular',
    'DMK/AIADMK',
    'Medium',
    'Medium',
    0.45
),

-- Senior Citizens (51+) - LOW priority (loyal to traditional parties)
(
    'AGE_51_PLUS',
    'Senior Citizens (51+)',
    'மூத்த குடிமக்கள் (51+)',
    'Experienced voters, traditional outlook, welfare-focused',
    'Age',
    ARRAY['Pension', 'Healthcare', 'Law & Order', 'Respect for Elders', 'Free Schemes'],
    ARRAY['TV', 'Newspaper', 'Temple Meetings', 'Community Leaders', 'Door-to-door'],
    'Respectful, traditional. Focus on welfare schemes, healthcare, social security.',
    10000000,
    15.9,
    'Loyal',
    'DMK/AIADMK',
    'Low',
    'Low',
    0.25
);

-- =====================================================
-- 3. INSERT VOTER SEGMENTS - OCCUPATION-BASED
-- =====================================================

INSERT INTO voter_segments (
    segment_code, segment_name, segment_name_tamil, description,
    segment_category, key_issues, preferred_channels, messaging_strategy,
    estimated_voters, percentage_of_electorate, voting_pattern,
    traditional_leaning, tvk_priority, tvk_win_probability
) VALUES

-- Farmers - HIGH priority
(
    'OCC_FARMERS',
    'Farmers',
    'விவசாயிகள்',
    'Agricultural workers, small and marginal farmers, landowners',
    'Occupation',
    ARRAY['Agriculture Support', 'Water/Irrigation', 'MSP', 'Debt Relief', 'Fertilizer Prices'],
    ARRAY['Village Meetings', 'Agricultural Fairs', 'Temple Gatherings', 'Local Leaders'],
    'Empathetic, supportive. Address agrarian distress, water crisis, loan waivers.',
    8000000,
    12.7,
    'Swing',
    'AIADMK',
    'High',
    0.55
),

-- Laborers - HIGH priority
(
    'OCC_LABOR',
    'Labourers',
    'தொழிலாளர்கள்',
    'Daily wage workers, construction workers, unorganized sector',
    'Occupation',
    ARRAY['Wages', 'Social Security', 'Housing', 'Basic Amenities', 'Job Security'],
    ARRAY['Factory Gate Meetings', 'Trade Unions', 'WhatsApp', 'Local Leaders'],
    'Direct, empowering. Focus on minimum wages, labor rights, social security.',
    12000000,
    19.0,
    'Swing',
    'DMK',
    'High',
    0.60
),

-- Government Employees - LOW priority (established interests)
(
    'OCC_GOVT',
    'Government Employees',
    'அரசு ஊழியர்கள்',
    'State and central government workers, teachers, police',
    'Occupation',
    ARRAY['Salary', 'Pension', 'Job Security', 'Old Pension Scheme', 'Transfers'],
    ARRAY['Union Meetings', 'Associations', 'WhatsApp Groups'],
    'Professional, policy-focused. Address OPS restoration, salary hikes.',
    2000000,
    3.2,
    'Regular',
    'DMK',
    'Low',
    0.35
),

-- Private Sector - CRITICAL for TVK
(
    'OCC_PRIVATE',
    'Private Sector',
    'தனியார் துறை',
    'IT professionals, corporate employees, private company workers',
    'Occupation',
    ARRAY['Jobs', 'Economy', 'Infrastructure', 'Work-Life Balance', 'Opportunities'],
    ARRAY['LinkedIn', 'Instagram', 'Office Campaigns', 'Tech Events'],
    'Modern, progressive. Focus on economic growth, innovation, start-up culture.',
    10000000,
    15.9,
    'Swing',
    'Neutral',
    'Critical',
    0.70
),

-- Business Owners - MEDIUM priority
(
    'OCC_BUSINESS',
    'Business Owners',
    'வணிகர்கள்',
    'Shop owners, traders, small and medium business owners',
    'Occupation',
    ARRAY['Economy', 'Tax Policies', 'Infrastructure', 'Ease of Business', 'Law & Order'],
    ARRAY['Chamber of Commerce', 'Trade Associations', 'WhatsApp', 'Business Meetings'],
    'Business-friendly. Focus on ease of doing business, tax relief, infrastructure.',
    3000000,
    4.8,
    'Regular',
    'AIADMK',
    'Medium',
    0.50
),

-- Students - CRITICAL for TVK (Vijay appeal)
(
    'OCC_STUDENTS',
    'Students',
    'மாணவர்கள்',
    'College and university students, young learners',
    'Occupation',
    ARRAY['Education Quality', 'Jobs', 'Skills Training', 'NEET Exam', 'Campus Facilities'],
    ARRAY['Instagram', 'Twitter', 'College Events', 'Student Unions', 'Film Promotions'],
    'Youth-centric, energetic. Focus on education reform, NEET opposition, job creation.',
    5000000,
    7.9,
    'First-time',
    'Neutral',
    'Critical',
    0.80
),

-- Unemployed Youth - CRITICAL for TVK
(
    'OCC_UNEMPLOYED',
    'Unemployed Youth',
    'வேலையில்லாத இளைஞர்கள்',
    'Educated but jobless, seeking opportunities',
    'Occupation',
    ARRAY['Jobs', 'Skills Training', 'Unemployment Allowance', 'Government Jobs', 'Start-up Support'],
    ARRAY['Social Media', 'Job Fairs', 'Youth Forums', 'WhatsApp Groups'],
    'Hopeful, solution-oriented. Promise job creation, skills training, entrepreneurship support.',
    6000000,
    9.5,
    'Swing',
    'Anti-incumbent',
    'Critical',
    0.75
);

-- =====================================================
-- 4. INSERT VOTER SEGMENTS - INCOME-BASED
-- =====================================================

INSERT INTO voter_segments (
    segment_code, segment_name, segment_name_tamil, description,
    segment_category, key_issues, preferred_channels, messaging_strategy,
    estimated_voters, percentage_of_electorate, voting_pattern,
    tvk_priority, tvk_win_probability
) VALUES

(
    'INC_LOW',
    'Low Income',
    'குறைந்த வருமானம்',
    'Below Poverty Line and Low-Income Group',
    'Income',
    ARRAY['Employment', 'Welfare Schemes', 'Healthcare', 'Ration', 'Housing'],
    ARRAY['Door-to-door', 'Community Meetings', 'Local Leaders', 'Temples'],
    'Welfare-focused. Emphasize free schemes, social security, empowerment.',
    18000000,
    28.6,
    'Loyal',
    'High',
    0.50
),

(
    'INC_MIDDLE',
    'Middle Income',
    'நடுத்தர வருமானம்',
    'Middle-class families, salaried class',
    'Income',
    ARRAY['Infrastructure', 'Education', 'Healthcare', 'Tax Relief', 'Quality of Life'],
    ARRAY['WhatsApp', 'Social Media', 'TV', 'Public Meetings'],
    'Quality-focused. Better infrastructure, education, healthcare at affordable cost.',
    20000000,
    31.7,
    'Swing',
    'Critical',
    0.65
),

(
    'INC_HIGH',
    'High Income',
    'அதிக வருமானம்',
    'Upper middle class and wealthy',
    'Income',
    ARRAY['Economy', 'Infrastructure', 'Law & Order', 'Investments', 'Growth'],
    ARRAY['LinkedIn', 'Business Forums', 'English Media', 'Clubs'],
    'Development-focused. Economic growth, good governance, world-class infrastructure.',
    3000000,
    4.8,
    'Regular',
    'Medium',
    0.55
);

-- =====================================================
-- 5. INSERT VOTER SEGMENTS - SOCIAL/CASTE-BASED
-- =====================================================

INSERT INTO voter_segments (
    segment_code, segment_name, segment_name_tamil, description,
    segment_category, key_issues, preferred_channels, messaging_strategy,
    estimated_voters, percentage_of_electorate, voting_pattern,
    traditional_leaning, tvk_priority, tvk_win_probability
) VALUES

(
    'SOC_SC',
    'Scheduled Castes',
    'அட்டவணை சாதியினர்',
    'SC community, diverse sub-castes',
    'Social',
    ARRAY['Social Justice', 'Reservation', 'Welfare', 'Anti-discrimination', 'Empowerment'],
    ARRAY['Community Leaders', 'Caste Associations', 'WhatsApp', 'Public Meetings'],
    'Social justice focused. Emphasize equality, empowerment, representation.',
    10000000,
    15.9,
    'Loyal',
    'DMK',
    'High',
    0.55
),

(
    'SOC_ST',
    'Scheduled Tribes',
    'அட்டவணை பழங்குடியினர்',
    'Tribal communities in hill areas',
    'Social',
    ARRAY['Tribal Welfare', 'Forest Rights', 'Education', 'Healthcare', 'Land Rights'],
    ARRAY['Tribal Leaders', 'Community Meetings', 'NGOs'],
    'Inclusive. Address tribal rights, land issues, healthcare access.',
    500000,
    0.8,
    'Loyal',
    'DMK',
    'Medium',
    0.45
),

(
    'SOC_OBC',
    'Other Backward Classes',
    'பிற்படுத்தப்பட்ட வகுப்பினர்',
    'OBC communities, largest voting bloc in TN',
    'Social',
    ARRAY['Reservation', 'Education', 'Jobs', 'Business Support', 'Political Representation'],
    ARRAY['Caste Associations', 'Community Leaders', 'WhatsApp', 'Village Meetings'],
    'Empowerment-focused. Economic development, education, entrepreneurship support.',
    25000000,
    39.7,
    'Swing',
    'DMK/AIADMK',
    'Critical',
    0.60
),

(
    'SOC_FORWARD',
    'Forward Castes',
    'முன்னேறிய சாதியினர்',
    'Upper castes, economically diverse',
    'Social',
    ARRAY['Merit', 'Economy', 'Infrastructure', 'Education Quality', 'Development'],
    ARRAY['Professional Networks', 'WhatsApp', 'Newspapers', 'Social Media'],
    'Merit-based. Focus on development, quality education, economic growth.',
    7000000,
    11.1,
    'Swing',
    'AIADMK/BJP',
    'Medium',
    0.50
),

-- Special sub-groups with high political importance
(
    'SOC_VANNIYAR',
    'Vanniyar Community',
    'வன்னியர் சமூகம்',
    'Vanniyar caste, strong PMK base',
    'Social',
    ARRAY['20% Reservation', 'Education', 'Government Jobs', 'Land Rights'],
    ARRAY['PMK Influence', 'Caste Forums', 'Village Leaders'],
    'Specific to community concerns. Address reservation demands, education access.',
    7000000,
    11.1,
    'Loyal',
    'PMK/AIADMK',
    'High',
    0.45
),

(
    'SOC_THEVAR',
    'Thevar Community',
    'தேவர் சமூகம்',
    'Thevar communities in southern TN',
    'Social',
    ARRAY['Political Representation', 'Agriculture', 'Water', 'Respect', 'Leadership'],
    ARRAY['Community Leaders', 'Temple Events', 'Caste Associations'],
    'Leadership-focused. Respect community pride, address regional issues.',
    5000000,
    7.9,
    'Loyal',
    'AIADMK',
    'Medium',
    0.40
);

-- =====================================================
-- 6. INSERT VOTER SEGMENTS - RELIGION-BASED
-- =====================================================

INSERT INTO voter_segments (
    segment_code, segment_name, segment_name_tamil, description,
    segment_category, key_issues, preferred_channels, messaging_strategy,
    estimated_voters, percentage_of_electorate, voting_pattern,
    traditional_leaning, tvk_priority, tvk_win_probability
) VALUES

(
    'REL_HINDU',
    'Hindus',
    'இந்துக்கள்',
    'Hindu majority, diverse practices',
    'Religion',
    ARRAY['Temple Administration', 'Hindu Rights', 'Culture', 'Education', 'Festivals'],
    ARRAY['Temples', 'Religious Events', 'Community Leaders', 'WhatsApp'],
    'Secular but culturally respectful. Address temple autonomy, cultural preservation.',
    52000000,
    82.5,
    'Diverse',
    'Diverse',
    'Critical',
    0.60
),

(
    'REL_MUSLIM',
    'Muslims',
    'முஸ்லிம்கள்',
    'Muslim minority community',
    'Religion',
    ARRAY['Minority Welfare', 'Education', 'Jobs', 'Security', 'Waqf Board'],
    ARRAY['Mosques', 'Community Leaders', 'Muslim Organizations', 'WhatsApp'],
    'Inclusive, secular. Focus on minority rights, education, economic empowerment.',
    4000000,
    6.3,
    'Loyal',
    'DMK/INC',
    'High',
    0.50
),

(
    'REL_CHRISTIAN',
    'Christians',
    'கிறிஸ்தவர்கள்',
    'Christian minority, strong in southern districts',
    'Religion',
    ARRAY['Minority Rights', 'Education', 'Church Issues', 'Healthcare', 'Anti-conversion Laws'],
    ARRAY['Churches', 'Bishops', 'Christian Organizations', 'Schools'],
    'Secular, inclusive. Protect minority rights, support church-run institutions.',
    4000000,
    6.3,
    'Loyal',
    'DMK/INC',
    'High',
    0.55
),

(
    'REL_OTHER',
    'Other Religions',
    'பிற சமயங்கள்',
    'Jains, Buddhists, Sikhs, others',
    'Religion',
    ARRAY['Religious Freedom', 'Cultural Rights', 'Business Support'],
    ARRAY['Community Organizations', 'Religious Centers'],
    'Inclusive, respectful. Ensure religious freedom, cultural respect.',
    500000,
    0.8,
    'Swing',
    'Neutral',
    'Low',
    0.50
);

-- =====================================================
-- 7. INSERT VOTER SEGMENTS - GENDER-BASED
-- =====================================================

INSERT INTO voter_segments (
    segment_code, segment_name, segment_name_tamil, description,
    segment_category, key_issues, preferred_channels, messaging_strategy,
    estimated_voters, percentage_of_electorate, voting_pattern,
    tvk_priority, tvk_win_probability
) VALUES

(
    'GEN_MALE',
    'Male Voters',
    'ஆண் வாக்காளர்கள்',
    'Male electorate across all demographics',
    'Gender',
    ARRAY['Jobs', 'Economy', 'Infrastructure', 'Sports', 'Development'],
    ARRAY['Social Media', 'TV', 'Public Meetings', 'Tea Shops', 'Sports Events'],
    'Development-focused. Jobs, economic growth, infrastructure.',
    31000000,
    49.2,
    'Diverse',
    'Critical',
    0.60
),

(
    'GEN_FEMALE',
    'Female Voters',
    'பெண் வாக்காளர்கள்',
    'Female electorate, increasingly influential',
    'Gender',
    ARRAY['Safety', 'Healthcare', 'Education', 'Free Schemes', 'Women Empowerment'],
    ARRAY['Women''s Groups', 'Self-Help Groups', 'Door-to-door', 'WhatsApp', 'Schools'],
    'Safety and welfare focused. Women''s security, health, children''s education.',
    32000000,
    50.8,
    'Regular',
    'Critical',
    0.65
),

(
    'GEN_FTV',
    'First-Time Voters',
    'முதல் முறை வாக்காளர்கள்',
    'New voters (18-21), excited and idealistic',
    'Gender',
    ARRAY['Jobs', 'Education', 'Future', 'Change', 'Youth Issues'],
    ARRAY['Instagram', 'TikTok', 'YouTube', 'College Campaigns', 'Celebrity Events'],
    'Energetic, change-oriented. New politics, fresh leadership (Vijay appeal).',
    4000000,
    6.3,
    'First-time',
    'Critical',
    0.85
);

-- =====================================================
-- 8. INSERT VOTER SEGMENTS - GEOGRAPHY-BASED
-- =====================================================

INSERT INTO voter_segments (
    segment_code, segment_name, segment_name_tamil, description,
    segment_category, key_issues, preferred_channels, messaging_strategy,
    estimated_voters, percentage_of_electorate, voting_pattern,
    tvk_priority, tvk_win_probability
) VALUES

(
    'GEO_URBAN',
    'Urban Voters',
    'நகர்ப்புற வாக்காளர்கள்',
    'City and town residents',
    'Geography',
    ARRAY['Infrastructure', 'Traffic', 'Pollution', 'Jobs', 'Quality of Life'],
    ARRAY['Social Media', 'TV', 'Newspapers', 'Corporate Events', 'Apartment Campaigns'],
    'Modern, quality-focused. Better infrastructure, governance, living standards.',
    25000000,
    39.7,
    'Swing',
    'Critical',
    0.70
),

(
    'GEO_RURAL',
    'Rural Voters',
    'கிராமப்புற வாக்காளர்கள்',
    'Village residents, agricultural focus',
    'Geography',
    ARRAY['Agriculture', 'Water', 'Electricity', 'Roads', 'Basic Amenities'],
    ARRAY['Village Meetings', 'Temple Gatherings', 'Local Leaders', 'Agricultural Fairs'],
    'Agrarian-focused. Water, electricity, road connectivity, farm support.',
    38000000,
    60.3,
    'Traditional',
    'High',
    0.50
),

(
    'GEO_CHENNAI',
    'Chennai Metro',
    'சென்னை பெருநகரம்',
    'Chennai and suburbs, cosmopolitan',
    'Geography',
    ARRAY['Metro', 'Traffic', 'Floods', 'Jobs', 'Cost of Living'],
    ARRAY['Social Media', 'English Media', 'Metro Campaigns', 'Office Promotions'],
    'Urban, progressive. Focus on Chennai-specific issues, infrastructure.',
    8000000,
    12.7,
    'Swing',
    'Critical',
    0.75
),

(
    'GEO_COIMBATORE',
    'Coimbatore Region',
    'கோயம்புத்தூர் பிராந்தியம்',
    'Industrial belt, business-oriented',
    'Geography',
    ARRAY['Industry', 'Jobs', 'Infrastructure', 'Business Environment'],
    ARRAY['Business Forums', 'Trade Associations', 'Newspapers', 'WhatsApp'],
    'Business-friendly. Industrial growth, ease of business, infrastructure.',
    5000000,
    7.9,
    'Swing',
    'High',
    0.60
),

(
    'GEO_SOUTH_TN',
    'Southern Tamil Nadu',
    'தென் தமிழகம்',
    'Southern districts, traditional strongholds',
    'Geography',
    ARRAY['Agriculture', 'Water', 'Temples', 'Education', 'Regional Pride'],
    ARRAY['Village Meetings', 'Caste Leaders', 'Temple Events'],
    'Regional pride. Water sharing, agriculture support, cultural respect.',
    15000000,
    23.8,
    'Traditional',
    'Medium',
    0.45
);

-- =====================================================
-- 9. CREATE VIEWS
-- =====================================================

-- View for priority segments
CREATE OR REPLACE VIEW tvk_priority_segments AS
SELECT
    segment_code,
    segment_name,
    segment_name_tamil,
    segment_category,
    estimated_voters,
    percentage_of_electorate,
    tvk_priority,
    tvk_win_probability,
    voting_pattern,
    key_issues
FROM voter_segments
WHERE tvk_priority IN ('Critical', 'High')
AND is_active = TRUE
ORDER BY
    CASE tvk_priority
        WHEN 'Critical' THEN 1
        WHEN 'High' THEN 2
    END,
    estimated_voters DESC;

-- View for segment size by category
CREATE OR REPLACE VIEW segment_distribution AS
SELECT
    segment_category,
    COUNT(*) as segment_count,
    SUM(estimated_voters) as total_voters,
    ROUND(AVG(tvk_win_probability), 2) as avg_win_probability
FROM voter_segments
WHERE is_active = TRUE
GROUP BY segment_category
ORDER BY total_voters DESC;

-- =====================================================
-- 10. TRIGGERS
-- =====================================================

CREATE OR REPLACE FUNCTION update_voter_segment_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_voter_segments_timestamp
    BEFORE UPDATE ON voter_segments
    FOR EACH ROW
    EXECUTE FUNCTION update_voter_segment_updated_at();

-- =====================================================
-- 11. ROW LEVEL SECURITY
-- =====================================================

ALTER TABLE voter_segments ENABLE ROW LEVEL SECURITY;

CREATE POLICY voter_segments_select_policy ON voter_segments
    FOR SELECT
    USING (auth.role() = 'authenticated');

CREATE POLICY voter_segments_admin_policy ON voter_segments
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid()
            AND role IN ('admin', 'super_admin')
        )
    );

-- =====================================================
-- 12. HELPER FUNCTIONS
-- =====================================================

-- Get segments by priority
CREATE OR REPLACE FUNCTION get_segments_by_priority(p_priority TEXT)
RETURNS TABLE (
    code TEXT,
    name TEXT,
    tamil_name TEXT,
    voters BIGINT,
    win_prob DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        segment_code,
        segment_name,
        segment_name_tamil,
        estimated_voters,
        tvk_win_probability
    FROM voter_segments
    WHERE tvk_priority = p_priority
    AND is_active = TRUE
    ORDER BY estimated_voters DESC;
END;
$$ LANGUAGE plpgsql;

-- Calculate total addressable voters
CREATE OR REPLACE FUNCTION calculate_addressable_voters()
RETURNS TABLE (
    priority_level TEXT,
    total_segments INTEGER,
    total_voters BIGINT,
    avg_win_probability DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        tvk_priority,
        COUNT(*)::INTEGER,
        SUM(estimated_voters),
        ROUND(AVG(tvk_win_probability), 2)
    FROM voter_segments
    WHERE is_active = TRUE
    GROUP BY tvk_priority
    ORDER BY
        CASE tvk_priority
            WHEN 'Critical' THEN 1
            WHEN 'High' THEN 2
            WHEN 'Medium' THEN 3
            WHEN 'Low' THEN 4
        END;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 13. COMMENTS
-- =====================================================

COMMENT ON TABLE voter_segments IS 'Voter classification for targeted campaign strategy';
COMMENT ON COLUMN voter_segments.tvk_priority IS 'Priority level for TVK campaign focus';
COMMENT ON COLUMN voter_segments.tvk_win_probability IS 'Estimated probability of winning this segment (0.00-1.00)';
COMMENT ON COLUMN voter_segments.key_issues IS 'Main concerns and priorities for this voter segment';
COMMENT ON COLUMN voter_segments.preferred_channels IS 'Best communication channels to reach this segment';

-- =====================================================
-- 14. VALIDATION QUERIES
-- =====================================================

-- Check total segments
-- SELECT COUNT(*) FROM voter_segments;

-- Check critical and high priority segments
-- SELECT * FROM tvk_priority_segments;

-- Check voter distribution by category
-- SELECT * FROM segment_distribution;

-- Calculate addressable voters by priority
-- SELECT * FROM calculate_addressable_voters();

-- Check segments with high win probability
-- SELECT segment_name, estimated_voters, tvk_win_probability
-- FROM voter_segments
-- WHERE tvk_win_probability >= 0.60
-- ORDER BY tvk_win_probability DESC;

-- =====================================================
-- END OF MIGRATION
-- =====================================================
