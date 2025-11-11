-- =====================================================
-- POLITICAL PARTIES & STRUCTURES
-- TVK and all major Tamil Nadu parties
-- Date: 2025-11-08
-- =====================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- 1. POLITICAL PARTIES TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS political_parties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    name_tamil TEXT,
    full_name TEXT,
    abbreviation TEXT,

    -- Party identity
    founded_year INTEGER,
    founder TEXT,
    current_leader TEXT,
    current_leader_tamil TEXT,
    ideology TEXT,                            -- 'Dravidian', 'Hindu Nationalism', 'Socialist', etc.

    -- Electoral alliance
    alliance TEXT,                            -- 'NDA', 'INDIA', 'Independent'
    alliance_role TEXT,                       -- 'Lead', 'Member', 'Independent'

    -- Visual identity
    party_symbol TEXT,
    party_symbol_tamil TEXT,
    party_color TEXT,                         -- Hex color code
    party_flag_url TEXT,
    party_logo_url TEXT,

    -- Contact information
    headquarters_address TEXT,
    headquarters_city TEXT,
    headquarters_state TEXT,
    phone TEXT,
    email TEXT,
    website TEXT,

    -- Social media
    twitter_handle TEXT,
    facebook_page TEXT,
    instagram_handle TEXT,
    youtube_channel TEXT,
    telegram_channel TEXT,

    -- Electoral presence
    states_present TEXT[],
    recognition_level TEXT,                   -- 'National', 'State', 'Registered'

    -- Current strength (2021 election for Tamil Nadu)
    tn_mlas_2021 INTEGER DEFAULT 0,
    tn_vote_share_2021 DECIMAL(5,2),
    total_mps INTEGER DEFAULT 0,
    total_mlas_national INTEGER DEFAULT 0,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_national_party BOOLEAN DEFAULT FALSE,
    is_state_party BOOLEAN DEFAULT FALSE,
    is_regional_party BOOLEAN DEFAULT FALSE,

    -- Multi-tenancy
    tenant_id TEXT,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,

    -- Constraints
    CONSTRAINT valid_recognition CHECK (recognition_level IN ('National', 'State', 'Registered', 'Unrecognized'))
);

-- Create indexes
CREATE INDEX idx_parties_code ON political_parties(code);
CREATE INDEX idx_parties_name ON political_parties(name);
CREATE INDEX idx_parties_alliance ON political_parties(alliance);
CREATE INDEX idx_parties_recognition ON political_parties(recognition_level);
CREATE INDEX idx_parties_active ON political_parties(is_active);

-- =====================================================
-- 2. INSERT PARTIES - TVK FIRST
-- =====================================================

INSERT INTO political_parties (
    code, name, name_tamil, full_name, founded_year, founder, current_leader, current_leader_tamil,
    ideology, alliance, alliance_role, party_symbol, party_symbol_tamil, party_color,
    website, twitter_handle, states_present, recognition_level,
    is_active, is_regional_party
) VALUES

-- ⭐ TVK - Tamilaga Vettri Kazhagam (YOUR PARTY)
(
    'TVK',
    'TVK',
    'தமிழக வெற்றி கழகம்',
    'Tamilaga Vettri Kazhagam',
    2024,
    'Vijay',
    'Vijay',
    'விஜய்',
    'Dravidian, Social Justice',
    'Independent',
    'Independent',
    'TBD',                                    -- Symbol to be allotted by Election Commission
    'ஒதுக்கப்படும்',
    '#FF0000',                                -- Red (update with actual color)
    'https://tvk.org.in',
    '@TVKOfficial',
    ARRAY['TN', 'PY'],
    'Registered',
    TRUE,
    TRUE
);

-- =====================================================
-- 3. INSERT OTHER MAJOR TAMIL NADU PARTIES
-- =====================================================

-- DMK - Dravida Munnetra Kazhagam (Ruling party 2021)
INSERT INTO political_parties (
    code, name, name_tamil, full_name, founded_year, founder, current_leader, current_leader_tamil,
    ideology, alliance, alliance_role, party_symbol, party_symbol_tamil, party_color,
    website, twitter_handle, facebook_page, states_present, recognition_level,
    tn_mlas_2021, tn_vote_share_2021, is_active, is_state_party
) VALUES (
    'DMK',
    'DMK',
    'திமுக',
    'Dravida Munnetra Kazhagam',
    1949,
    'C. N. Annadurai',
    'M. K. Stalin',
    'மு. க. ஸ்டாலின்',
    'Dravidian, Social Democracy',
    'INDIA',
    'Lead',
    'Rising Sun',
    'உதய சூரியன்',
    '#FF0000',
    'https://www.dmk.in',
    '@arivalayam',
    'DMKParty',
    ARRAY['TN', 'PY'],
    'State',
    133,
    37.74,
    TRUE,
    TRUE
);

-- AIADMK - All India Anna Dravida Munnetra Kazhagam
INSERT INTO political_parties (
    code, name, name_tamil, full_name, founded_year, founder, current_leader, current_leader_tamil,
    ideology, alliance, alliance_role, party_symbol, party_symbol_tamil, party_color,
    website, twitter_handle, states_present, recognition_level,
    tn_mlas_2021, tn_vote_share_2021, is_active, is_state_party
) VALUES (
    'AIADMK',
    'AIADMK',
    'அதிமுக',
    'All India Anna Dravida Munnetra Kazhagam',
    1972,
    'M. G. Ramachandran',
    'Edappadi K. Palaniswami',
    'எடப்பாடி கே. பழனிச்சாமி',
    'Dravidian, Social Conservatism',
    'NDA',
    'Member',
    'Two Leaves',
    'இரட்டை இலை',
    '#006400',
    'https://www.aiadmk.in',
    '@AIADMKOfficial',
    ARRAY['TN', 'PY'],
    'State',
    66,
    33.29,
    TRUE,
    TRUE
);

-- BJP - Bharatiya Janata Party
INSERT INTO political_parties (
    code, name, name_tamil, full_name, founded_year, founder, current_leader, current_leader_tamil,
    ideology, alliance, alliance_role, party_symbol, party_symbol_tamil, party_color,
    website, twitter_handle, states_present, recognition_level,
    tn_mlas_2021, tn_vote_share_2021, is_active, is_national_party
) VALUES (
    'BJP',
    'BJP',
    'பாஜக',
    'Bharatiya Janata Party',
    1980,
    'Atal Bihari Vajpayee, L.K. Advani',
    'K. Annamalai (TN President)',
    'கே. அண்ணாமலை',
    'Hindu Nationalism, Conservatism',
    'NDA',
    'Lead',
    'Lotus',
    'தாமரை',
    '#FF9933',
    'https://www.bjp.org',
    '@BJP4India',
    ARRAY['ALL'],
    'National',
    4,
    2.62,
    TRUE,
    TRUE
);

-- INC - Indian National Congress
INSERT INTO political_parties (
    code, name, name_tamil, full_name, founded_year, founder, current_leader, current_leader_tamil,
    ideology, alliance, alliance_role, party_symbol, party_symbol_tamil, party_color,
    website, twitter_handle, states_present, recognition_level,
    tn_mlas_2021, tn_vote_share_2021, is_active, is_national_party
) VALUES (
    'INC',
    'Congress',
    'காங்கிரஸ்',
    'Indian National Congress',
    1885,
    'A. O. Hume, Allan Octavian Hume',
    'K. Selvaperunthagai (TN President)',
    'கே. செல்வப்பெருந்தகை',
    'Social Democracy, Secularism',
    'INDIA',
    'Member',
    'Hand',
    'கை',
    '#00BFFF',
    'https://www.inc.in',
    '@INCIndia',
    ARRAY['ALL'],
    'National',
    18,
    6.38,
    TRUE,
    TRUE
);

-- PMK - Pattali Makkal Katchi
INSERT INTO political_parties (
    code, name, name_tamil, full_name, founded_year, founder, current_leader, current_leader_tamil,
    ideology, alliance, alliance_role, party_symbol, party_symbol_tamil, party_color,
    website, twitter_handle, states_present, recognition_level,
    tn_mlas_2021, tn_vote_share_2021, is_active, is_regional_party
) VALUES (
    'PMK',
    'PMK',
    'பாமக',
    'Pattali Makkal Katchi',
    1989,
    'S. Ramadoss',
    'Anbumani Ramadoss',
    'அன்புமணி ராமதாஸ்',
    'Vanniyar Rights, Social Justice',
    'NDA',
    'Member',
    'Mango',
    'மாம்பழம்',
    '#FFFF00',
    'https://www.pmk.org.in',
    '@PMKparty',
    ARRAY['TN', 'PY'],
    'State',
    5,
    5.95,
    TRUE,
    TRUE
);

-- VCK - Viduthalai Chiruthaigal Katchi
INSERT INTO political_parties (
    code, name, name_tamil, full_name, founded_year, founder, current_leader, current_leader_tamil,
    ideology, alliance, alliance_role, party_symbol, party_symbol_tamil, party_color,
    website, twitter_handle, states_present, recognition_level,
    tn_mlas_2021, tn_vote_share_2021, is_active, is_regional_party
) VALUES (
    'VCK',
    'VCK',
    'விடுதலை சிறுத்தைகள் கட்சி',
    'Viduthalai Chiruthaigal Katchi',
    1994,
    'Thol. Thirumavalavan',
    'Thol. Thirumavalavan',
    'தொல். திருமாவளவன்',
    'Dalit Rights, Social Justice',
    'INDIA',
    'Member',
    'Pot',
    'பானை',
    '#FF0000',
    'https://www.vck.in',
    '@VCKparty',
    ARRAY['TN'],
    'State',
    4,
    2.21,
    TRUE,
    TRUE
);

-- MDMK - Marumalarchi Dravida Munnetra Kazhagam
INSERT INTO political_parties (
    code, name, name_tamil, full_name, founded_year, founder, current_leader, current_leader_tamil,
    ideology, alliance, alliance_role, party_symbol, party_symbol_tamil, party_color,
    website, twitter_handle, states_present, recognition_level,
    tn_mlas_2021, tn_vote_share_2021, is_active, is_regional_party
) VALUES (
    'MDMK',
    'MDMK',
    'மதிமுக',
    'Marumalarchi Dravida Munnetra Kazhagam',
    1994,
    'Vaiko',
    'Vaiko',
    'வைகோ',
    'Dravidian, Tamil Nationalism',
    'INDIA',
    'Member',
    'Top',
    'பம்பரம்',
    '#800080',
    'https://www.mdmk.org.in',
    '@MDMKOfficial',
    ARRAY['TN'],
    'Registered',
    0,
    0.88,
    TRUE,
    TRUE
);

-- NTK - Naam Tamilar Katchi
INSERT INTO political_parties (
    code, name, name_tamil, full_name, founded_year, founder, current_leader, current_leader_tamil,
    ideology, alliance, alliance_role, party_symbol, party_symbol_tamil, party_color,
    website, twitter_handle, states_present, recognition_level,
    tn_mlas_2021, tn_vote_share_2021, is_active, is_regional_party
) VALUES (
    'NTK',
    'NTK',
    'நாம் தமிழர் கட்சி',
    'Naam Tamilar Katchi',
    2010,
    'Seeman',
    'Seeman',
    'சீமான்',
    'Tamil Nationalism, Dravidian',
    'Independent',
    'Independent',
    'Battery Torch',
    'மின்கல விளக்கு',
    '#FFD700',
    'https://www.naamtamilar.org',
    '@NTKOfficial',
    ARRAY['TN', 'PY'],
    'Registered',
    0,
    6.57,
    TRUE,
    TRUE
);

-- MNM - Makkal Needhi Maiam (Kamal Haasan's party)
INSERT INTO political_parties (
    code, name, name_tamil, full_name, founded_year, founder, current_leader, current_leader_tamil,
    ideology, alliance, alliance_role, party_symbol, party_symbol_tamil, party_color,
    website, twitter_handle, states_present, recognition_level,
    tn_mlas_2021, tn_vote_share_2021, is_active, is_regional_party
) VALUES (
    'MNM',
    'MNM',
    'மக்கள் நீதி மய்யம்',
    'Makkal Needhi Maiam',
    2018,
    'Kamal Haasan',
    'Kamal Haasan',
    'கமல் ஹாசன்',
    'Secularism, Social Justice',
    'Independent',
    'Independent',
    'Battery Charger',
    'மின்கலம் சார்ஜர்',
    '#000000',
    'https://www.maiam.com',
    '@maiamofficial',
    ARRAY['TN', 'PY'],
    'Registered',
    0,
    2.63,
    TRUE,
    TRUE
);

-- CPM - Communist Party of India (Marxist)
INSERT INTO political_parties (
    code, name, name_tamil, full_name, founded_year, founder, current_leader, current_leader_tamil,
    ideology, alliance, alliance_role, party_symbol, party_symbol_tamil, party_color,
    website, twitter_handle, states_present, recognition_level,
    tn_mlas_2021, tn_vote_share_2021, is_active, is_national_party
) VALUES (
    'CPM',
    'CPM',
    'இந்திய கம்யூனிஸ்ட் கட்சி (மார்க்சிஸ்ட்)',
    'Communist Party of India (Marxist)',
    1964,
    'E.M.S. Namboodiripad',
    'K. Balakrishnan (TN Secretary)',
    'கே. பாலகிருஷ்ணன்',
    'Communism, Marxism',
    'INDIA',
    'Member',
    'Hammer, Sickle and Star',
    'அரிவாள் சுத்தியல் நட்சத்திரம்',
    '#FF0000',
    'https://cpim.org',
    '@cpimspeak',
    ARRAY['ALL'],
    'National',
    2,
    0.66,
    TRUE,
    TRUE
);

-- CPI - Communist Party of India
INSERT INTO political_parties (
    code, name, name_tamil, full_name, founded_year, founder, current_leader, current_leader_tamil,
    ideology, alliance, alliance_role, party_symbol, party_symbol_tamil, party_color,
    website, twitter_handle, states_present, recognition_level,
    tn_mlas_2021, tn_vote_share_2021, is_active, is_national_party
) VALUES (
    'CPI',
    'CPI',
    'இந்திய கம்யூனிஸ்ட் கட்சி',
    'Communist Party of India',
    1925,
    'M. Singaravelu',
    'R. Mutharasan (TN Secretary)',
    'ஆர். முத்தரசன்',
    'Communism, Marxism',
    'INDIA',
    'Member',
    'Ears of Corn and Sickle',
    'அரிவாள் கதிர்கள்',
    '#FF0000',
    'https://cpiindia.org',
    '@cpindia',
    ARRAY['ALL'],
    'National',
    2,
    0.58,
    TRUE,
    TRUE
);

-- IUML - Indian Union Muslim League
INSERT INTO political_parties (
    code, name, name_tamil, full_name, founded_year, founder, current_leader, current_leader_tamil,
    ideology, alliance, alliance_role, party_symbol, party_symbol_tamil, party_color,
    website, twitter_handle, states_present, recognition_level,
    tn_mlas_2021, tn_vote_share_2021, is_active, is_regional_party
) VALUES (
    'IUML',
    'IUML',
    'இந்திய யூனியன் முஸ்லிம் லீக்',
    'Indian Union Muslim League',
    1948,
    'Muhammad Ismail',
    'K. M. Kader Mohideen (TN President)',
    'கே. எம். காதர் மொய்தீன்',
    'Muslim Rights, Secularism',
    'INDIA',
    'Member',
    'Ladder',
    'ஏணி',
    '#008000',
    'https://iuml.com',
    '@iumlnational',
    ARRAY['TN', 'KL'],
    'State',
    1,
    0.49,
    TRUE,
    TRUE
);

-- AMMK - Amma Makkal Munnetra Kazhagam (TTV Dhinakaran)
INSERT INTO political_parties (
    code, name, name_tamil, full_name, founded_year, founder, current_leader, current_leader_tamil,
    ideology, alliance, alliance_role, party_symbol, party_symbol_tamil, party_color,
    website, twitter_handle, states_present, recognition_level,
    tn_mlas_2021, tn_vote_share_2021, is_active, is_regional_party
) VALUES (
    'AMMK',
    'AMMK',
    'அம்மா மக்கள் முன்னேற்ற கழகம்',
    'Amma Makkal Munnetra Kazhagam',
    2018,
    'T. T. V. Dhinakaran',
    'T. T. V. Dhinakaran',
    'டி. டி. வி. தினகரன்',
    'Dravidian, AIADMK Ideology',
    'Independent',
    'Independent',
    'Gift Box',
    'பரிசு பெட்டி',
    '#006400',
    'https://www.ammk.in',
    '@AMMKTV',
    ARRAY['TN'],
    'Registered',
    0,
    2.37,
    TRUE,
    TRUE
);

-- DMDK - Desiya Murpokku Dravida Kazhagam (Vijayakanth's party)
INSERT INTO political_parties (
    code, name, name_tamil, full_name, founded_year, founder, current_leader, current_leader_tamil,
    ideology, alliance, alliance_role, party_symbol, party_symbol_tamil, party_color,
    website, twitter_handle, states_present, recognition_level,
    tn_mlas_2021, tn_vote_share_2021, is_active, is_regional_party
) VALUES (
    'DMDK',
    'DMDK',
    'தேசிய முற்போக்கு திராவிட கழகம்',
    'Desiya Murpokku Dravida Kazhagam',
    2005,
    'Vijayakanth',
    'Premalatha Vijayakanth',
    'பிரேமலதா விஜயகாந்த்',
    'Dravidian, Social Justice',
    'Independent',
    'Independent',
    'Drum',
    'முரசு',
    '#FF0000',
    'https://www.dmdk.in',
    '@DMDKOfficial',
    ARRAY['TN'],
    'Registered',
    0,
    1.07,
    TRUE,
    TRUE
);

-- =====================================================
-- 4. POLITICAL ALLIANCES TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS political_alliances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    name_tamil TEXT,
    short_name TEXT,

    -- Leadership
    lead_party_code TEXT REFERENCES political_parties(code),
    convenor_name TEXT,

    -- Member parties (array of party codes)
    member_parties TEXT[],
    total_member_parties INTEGER DEFAULT 0,

    -- Electoral data (2021 TN election)
    formation_date DATE,
    dissolution_date DATE,
    tn_seats_2021 INTEGER,
    tn_votes_2021 BIGINT,
    tn_vote_share_2021 DECIMAL(5,2),

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    states_active TEXT[],

    -- Multi-tenancy
    tenant_id TEXT,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Insert major alliances
INSERT INTO political_alliances (
    code, name, name_tamil, short_name, lead_party_code, member_parties,
    total_member_parties, formation_date, is_active, states_active,
    tn_seats_2021, tn_vote_share_2021
) VALUES

-- DMK Alliance (Secular Progressive Alliance / INDIA bloc in TN)
(
    'DMKA',
    'DMK Alliance',
    'திமுக கூட்டணி',
    'DMK+',
    'DMK',
    ARRAY['DMK', 'INC', 'VCK', 'MDMK', 'CPM', 'CPI', 'IUML'],
    7,
    '2021-02-01',
    TRUE,
    ARRAY['TN', 'PY'],
    159,
    47.35
),

-- AIADMK Alliance (NDA in TN for 2021)
(
    'AIADMKA',
    'AIADMK Alliance',
    'அதிமுக கூட்டணி',
    'AIADMK+',
    'AIADMK',
    ARRAY['AIADMK', 'BJP', 'PMK'],
    3,
    '2021-02-01',
    FALSE,
    ARRAY['TN', 'PY'],
    75,
    41.86
);

-- =====================================================
-- 5. PARTY MEMBERS TABLE (Leadership & Key Figures)
-- =====================================================

CREATE TABLE IF NOT EXISTS party_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    party_code TEXT NOT NULL REFERENCES political_parties(code) ON DELETE CASCADE,

    -- Personal information
    name TEXT NOT NULL,
    name_tamil TEXT,
    date_of_birth DATE,
    age INTEGER,
    gender TEXT CHECK (gender IN ('Male', 'Female', 'Other')),

    -- Role in party
    position TEXT NOT NULL,
    position_tamil TEXT,
    position_level TEXT CHECK (position_level IN ('National', 'State', 'District', 'Constituency', 'Booth')),

    -- Geographic assignment
    state_code TEXT REFERENCES states(code),
    district_code TEXT REFERENCES districts(code),
    constituency_code TEXT REFERENCES assembly_constituencies(code),

    -- Dates
    appointed_date DATE,
    tenure_start DATE,
    tenure_end DATE,

    -- Contact
    phone TEXT,
    email TEXT,
    address TEXT,

    -- Social media
    twitter_handle TEXT,
    facebook_profile TEXT,
    instagram_handle TEXT,

    -- Political background
    previous_positions JSONB,
    previous_parties TEXT[],
    electoral_history JSONB,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_public_figure BOOLEAN DEFAULT FALSE,

    -- Multi-tenancy
    tenant_id TEXT,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_party_members_party ON party_members(party_code);
CREATE INDEX idx_party_members_position_level ON party_members(position_level);
CREATE INDEX idx_party_members_active ON party_members(is_active);

-- Insert key TVK leadership (update with actual data)
INSERT INTO party_members (
    party_code, name, name_tamil, position, position_tamil, position_level,
    state_code, appointed_date, is_active, is_public_figure
) VALUES
(
    'TVK',
    'Vijay',
    'விஜய்',
    'Founder & President',
    'நிறுவனர் & தலைவர்',
    'State',
    'TN',
    '2024-01-01',
    TRUE,
    TRUE
);
-- Add more TVK leadership members as they are appointed

-- =====================================================
-- 6. TRIGGERS
-- =====================================================

CREATE OR REPLACE FUNCTION update_party_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_parties_timestamp
    BEFORE UPDATE ON political_parties
    FOR EACH ROW
    EXECUTE FUNCTION update_party_updated_at();

CREATE TRIGGER update_alliances_timestamp
    BEFORE UPDATE ON political_alliances
    FOR EACH ROW
    EXECUTE FUNCTION update_party_updated_at();

CREATE TRIGGER update_party_members_timestamp
    BEFORE UPDATE ON party_members
    FOR EACH ROW
    EXECUTE FUNCTION update_party_updated_at();

-- =====================================================
-- 7. ROW LEVEL SECURITY
-- =====================================================

ALTER TABLE political_parties ENABLE ROW LEVEL SECURITY;
ALTER TABLE political_alliances ENABLE ROW LEVEL SECURITY;
ALTER TABLE party_members ENABLE ROW LEVEL SECURITY;

-- All authenticated users can read party data
CREATE POLICY parties_select_policy ON political_parties
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY alliances_select_policy ON political_alliances
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY party_members_select_policy ON party_members
    FOR SELECT USING (auth.role() = 'authenticated');

-- Only admins can modify
CREATE POLICY parties_admin_policy ON political_parties
    FOR ALL USING (
        EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role IN ('admin', 'super_admin'))
    );

-- =====================================================
-- 8. VIEWS
-- =====================================================

-- View for party performance in 2021 election
CREATE OR REPLACE VIEW party_performance_2021 AS
SELECT
    code,
    name,
    name_tamil,
    alliance,
    tn_mlas_2021 as seats_won,
    tn_vote_share_2021 as vote_share,
    CASE
        WHEN tn_mlas_2021 >= 118 THEN 'Majority'
        WHEN tn_mlas_2021 >= 50 THEN 'Strong Opposition'
        WHEN tn_mlas_2021 >= 10 THEN 'Significant Presence'
        WHEN tn_mlas_2021 > 0 THEN 'Minor Presence'
        ELSE 'No Seats'
    END as performance_category
FROM political_parties
WHERE is_active = TRUE
ORDER BY tn_mlas_2021 DESC, tn_vote_share_2021 DESC;

-- =====================================================
-- 9. HELPER FUNCTIONS
-- =====================================================

-- Get all parties in an alliance
CREATE OR REPLACE FUNCTION get_alliance_parties(p_alliance_code TEXT)
RETURNS TABLE (
    party_code TEXT,
    party_name TEXT,
    seats_won INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        pp.code,
        pp.name,
        pp.tn_mlas_2021
    FROM political_parties pp
    WHERE pp.code = ANY(
        SELECT unnest(member_parties)
        FROM political_alliances
        WHERE code = p_alliance_code
    )
    ORDER BY pp.tn_mlas_2021 DESC;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 10. COMMENTS
-- =====================================================

COMMENT ON TABLE political_parties IS 'Master table of all political parties in Tamil Nadu';
COMMENT ON TABLE political_alliances IS 'Electoral alliances and coalitions';
COMMENT ON TABLE party_members IS 'Party leadership and key members';
COMMENT ON COLUMN political_parties.tn_mlas_2021 IS 'MLAs won in 2021 Tamil Nadu Assembly Election';

-- =====================================================
-- END OF MIGRATION
-- =====================================================
