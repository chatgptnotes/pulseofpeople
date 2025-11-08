# Seed Data Recommendations for TVK Party Project
## Tamil Nadu & Pondicherry Political Campaign Platform

**Date**: 2025-11-06
**Party**: TVK (Tamilaga Vettri Kazhagam)
**Geographic Coverage**: Tamil Nadu + Pondicherry

---

## Table of Contents
1. [Overview](#overview)
2. [Core Master Data](#core-master-data)
3. [TVK-Specific Data](#tvk-specific-data)
4. [Political Landscape Data](#political-landscape-data)
5. [Campaign Infrastructure Data](#campaign-infrastructure-data)
6. [Sentiment & Analytics Seed Data](#sentiment--analytics-seed-data)
7. [Implementation Priority](#implementation-priority)

---

## Overview

For a comprehensive TVK Party sentiment analysis and campaign management platform, you need seed data across multiple domains:

```
1. Geographic Masters     (States, Districts, Constituencies, Booths)
2. TVK Party Structure    (Leadership, Hierarchy, Members, Cadre)
3. Political Landscape    (All parties, Alliances, Key leaders)
4. Campaign Infrastructure (Offices, Resources, Teams)
5. Voter Segments         (Demographics, Categories, Personas)
6. Issue Categories       (Key topics TVK focuses on)
7. Media Outlets          (News sources, Social platforms)
8. Influencer Database    (Political, Social, Media influencers)
9. Historical Elections   (Past results, Trends)
10. Sample Sentiment Data (For testing & demo)
```

---

## Core Master Data

### 1. Geographic Hierarchy ✅ IN PROGRESS

**Files to Create**:
```
supabase/seeds/
├── 02_states_seed.sql          ⏳ HIGH PRIORITY
├── 03_districts_seed.sql       ⏳ HIGH PRIORITY
├── 04_constituencies_seed.sql  ✅ Template created
└── 05_polling_booths_seed.sql  ⏳ MEDIUM PRIORITY (70K+ records)
```

**Priority**: **HIGH** (Foundation for everything else)

**02_states_seed.sql** - Create this next:
```sql
-- States seed data
INSERT INTO states (code, name, name_tamil, total_districts, total_constituencies, center_lat, center_lng) VALUES
('TN', 'Tamil Nadu', 'தமிழ்நாடு', 38, 234, 11.1271, 78.6569),
('PY', 'Pondicherry', 'புதுச்சேரி', 4, 30, 11.9416, 79.8083);
```

**03_districts_seed.sql** - Create this next:
```sql
-- Tamil Nadu Districts (38)
INSERT INTO districts (code, name, name_tamil, state_code, center_lat, center_lng, headquarters) VALUES
('TN01', 'Ariyalur', 'அரியலூர்', 'TN', 11.1401, 79.0766, 'Ariyalur'),
('TN02', 'Chengalpattu', 'செங்கல்பட்டு', 'TN', 12.6917, 79.9752, 'Chengalpattu'),
('TN03', 'Chennai', 'சென்னை', 'TN', 13.0827, 80.2707, 'Chennai'),
-- ... (35 more districts)

-- Pondicherry Districts (4)
('PY01', 'Puducherry', 'புதுச்சேரி', 'PY', 11.9341, 79.8306, 'Puducherry'),
('PY02', 'Karaikal', 'காரைக்கால்', 'PY', 10.9254, 79.8380, 'Karaikal'),
('PY03', 'Mahe', 'மாஹே', 'PY', 11.7008, 75.5368, 'Mahe'),
('PY04', 'Yanam', 'ஆனம்', 'PY', 16.7333, 82.2167, 'Yanam');
```

---

## TVK-Specific Data

### 2. TVK Party Structure

**Files to Create**:
```
supabase/seeds/
├── 10_tvk_party_structure.sql      ⏳ HIGH PRIORITY
├── 11_tvk_leadership.sql           ⏳ HIGH PRIORITY
├── 12_tvk_district_units.sql       ⏳ HIGH PRIORITY
├── 13_tvk_constituency_teams.sql   ⏳ MEDIUM PRIORITY
└── 14_tvk_cadre_hierarchy.sql      ⏳ MEDIUM PRIORITY
```

**Priority**: **HIGH** (Your own party structure)

#### 10_tvk_party_structure.sql

```sql
-- =====================================================
-- TVK PARTY MASTER DATA
-- =====================================================

-- Party information
CREATE TABLE IF NOT EXISTS political_parties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code TEXT UNIQUE NOT NULL,           -- 'TVK', 'DMK', 'AIADMK', 'BJP', 'CONG'
    name TEXT NOT NULL,
    name_tamil TEXT,
    full_name TEXT,
    founded_year INTEGER,
    founder TEXT,
    current_leader TEXT,
    alliance TEXT,                       -- 'NDA', 'UPA', 'Independent'

    -- Identity
    party_symbol TEXT,                   -- 'Two Leaves', 'Rising Sun', etc.
    party_color TEXT,                    -- Hex color code
    flag_url TEXT,
    logo_url TEXT,

    -- Contact
    headquarters_address TEXT,
    phone TEXT,
    email TEXT,
    website TEXT,
    social_media JSONB,                  -- {twitter, facebook, instagram, youtube}

    -- Electoral presence
    states_present TEXT[],               -- ['TN', 'PY', 'KA', ...]
    total_mlas INTEGER DEFAULT 0,
    total_mps INTEGER DEFAULT 0,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_national_party BOOLEAN DEFAULT FALSE,
    is_state_party BOOLEAN DEFAULT FALSE,
    is_regional_party BOOLEAN DEFAULT TRUE,

    -- Multi-tenancy
    tenant_id TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert TVK Party
INSERT INTO political_parties (
    code, name, name_tamil, full_name, founded_year, founder, current_leader,
    alliance, party_symbol, party_color, website, social_media,
    states_present, is_regional_party, is_active
) VALUES (
    'TVK',
    'TVK',
    'தமிழக வெற்றி கழகம்',
    'Tamilaga Vettri Kazhagam',
    2024,  -- Update with actual founding year
    'Vijay',  -- Update with actual founder
    'Vijay',  -- Update with current leader

    'Independent',  -- Or update with actual alliance
    'TBD',  -- Party symbol (to be allotted by Election Commission)
    '#FF0000',  -- Update with actual party color

    'https://tvk.org.in',  -- Update with actual website

    -- Social media handles
    '{"twitter": "@TVKofficial", "facebook": "TVKofficial", "instagram": "tvk_official", "youtube": "TVKofficial"}'::JSONB,

    ARRAY['TN', 'PY'],  -- States where TVK is present

    TRUE,  -- Regional party
    TRUE   -- Active
);

-- Insert other major Tamil Nadu parties for comparison
INSERT INTO political_parties (code, name, name_tamil, full_name, founded_year, current_leader, party_symbol, party_color, states_present) VALUES
('DMK', 'DMK', 'திமுக', 'Dravida Munnetra Kazhagam', 1949, 'M.K. Stalin', 'Rising Sun', '#FF0000', ARRAY['TN', 'PY']),
('AIADMK', 'AIADMK', 'அதிமுக', 'All India Anna Dravida Munnetra Kazhagam', 1972, 'Edappadi K. Palaniswami', 'Two Leaves', '#006400', ARRAY['TN', 'PY']),
('BJP', 'BJP', 'பாஜக', 'Bharatiya Janata Party', 1980, 'K. Annamalai (TN)', 'Lotus', '#FF9933', ARRAY['TN', 'PY', 'KA', 'KL', 'AP', 'TS', 'ALL']),
('INC', 'Congress', 'காங்கிரஸ்', 'Indian National Congress', 1885, 'K. Selvaperunthagai (TN)', 'Hand', '#00FFFF', ARRAY['TN', 'PY', 'KA', 'KL', 'AP', 'TS', 'ALL']),
('PMK', 'PMK', 'பாமக', 'Pattali Makkal Katchi', 1989, 'Anbumani Ramadoss', 'Mango', '#FFFF00', ARRAY['TN', 'PY']),
('MDMK', 'MDMK', 'மதிமுக', 'Marumalarchi Dravida Munnetra Kazhagam', 1994, 'Vaiko', 'Top', '#800080', ARRAY['TN']),
('VCK', 'VCK', 'வீசிக', 'Viduthalai Chiruthaigal Katchi', 1994, 'Thol. Thirumavalavan', 'Pot', '#FF0000', ARRAY['TN']),
('NTK', 'NTK', 'நாம் தமிழர் கட்சி', 'Naam Tamilar Katchi', 2010, 'Seeman', 'Battery Torch', '#FFD700', ARRAY['TN', 'PY']);
```

#### 11_tvk_leadership.sql

```sql
-- =====================================================
-- TVK LEADERSHIP & KEY MEMBERS
-- =====================================================

CREATE TABLE IF NOT EXISTS party_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    party_code TEXT NOT NULL REFERENCES political_parties(code),

    -- Personal info
    name TEXT NOT NULL,
    name_tamil TEXT,
    date_of_birth DATE,
    age INTEGER,
    gender TEXT,

    -- Role in party
    position TEXT NOT NULL,                    -- 'President', 'General Secretary', 'District Secretary'
    position_level TEXT,                       -- 'State', 'District', 'Constituency', 'Booth'
    geographic_unit TEXT,                      -- District code or constituency code
    appointed_date DATE,

    -- Contact
    phone TEXT,
    email TEXT,
    address TEXT,

    -- Social media
    twitter_handle TEXT,
    facebook_profile TEXT,
    instagram_handle TEXT,

    -- Political background
    previous_positions JSONB,                  -- Array of past positions
    previous_parties TEXT[],                   -- If switched parties
    electoral_history JSONB,                   -- Past election results

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_public_figure BOOLEAN DEFAULT TRUE,

    -- Multi-tenancy
    tenant_id TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert TVK leadership (Update with actual data)
INSERT INTO party_members (party_code, name, name_tamil, position, position_level, is_active) VALUES
('TVK', 'Vijay', 'விஜய்', 'Founder & President', 'State', TRUE),
-- Add other key TVK leaders
('TVK', '[District Secretary Name]', '[Tamil Name]', 'District Secretary', 'District', TRUE),
('TVK', '[Chennai North Organizer]', '[Tamil Name]', 'Constituency Organizer', 'Constituency', TRUE);
-- Add more members...
```

#### 12_tvk_district_units.sql

```sql
-- =====================================================
-- TVK DISTRICT UNITS & OFFICES
-- =====================================================

CREATE TABLE IF NOT EXISTS party_district_units (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    party_code TEXT NOT NULL REFERENCES political_parties(code),
    district_code TEXT NOT NULL REFERENCES districts(code),

    -- Office details
    office_name TEXT,
    office_address TEXT,
    office_lat DECIMAL(10,8),
    office_lng DECIMAL(11,8),
    office_phone TEXT,

    -- Leadership
    district_secretary_id UUID REFERENCES party_members(id),
    assistant_secretary_id UUID REFERENCES party_members(id),

    -- Strength
    total_members INTEGER DEFAULT 0,
    active_members INTEGER DEFAULT 0,
    booth_committees INTEGER DEFAULT 0,

    -- Status
    office_status TEXT DEFAULT 'Active',      -- 'Active', 'Under Construction', 'Closed'
    established_date DATE,

    tenant_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert TVK district units for all 38 TN + 4 PY districts
INSERT INTO party_district_units (party_code, district_code, office_name, office_status, established_date) VALUES
('TVK', 'TN03', 'TVK Chennai District Office', 'Active', '2024-01-01'),
('TVK', 'TN04', 'TVK Coimbatore District Office', 'Active', '2024-01-01'),
-- Add all 42 districts...
('TVK', 'TN14', 'TVK Madurai District Office', 'Active', '2024-01-01');
```

---

## Political Landscape Data

### 3. Competitor Parties & Alliances

**Files to Create**:
```
supabase/seeds/
├── 20_all_parties_seed.sql             ⏳ HIGH PRIORITY
├── 21_political_alliances.sql          ⏳ HIGH PRIORITY
├── 22_key_political_leaders.sql        ⏳ MEDIUM PRIORITY
└── 23_party_performance_history.sql    ⏳ LOW PRIORITY
```

**Priority**: **HIGH** (Know your competition)

#### 20_all_parties_seed.sql
Already covered in section 10, but expand to include:
- All registered parties in Tamil Nadu
- Independent candidates
- Party merger/split history

#### 21_political_alliances.sql

```sql
-- =====================================================
-- POLITICAL ALLIANCES IN TAMIL NADU
-- =====================================================

CREATE TABLE IF NOT EXISTS political_alliances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    name_tamil TEXT,
    lead_party_code TEXT REFERENCES political_parties(code),
    member_parties TEXT[],                    -- Array of party codes
    formation_date DATE,
    dissolution_date DATE,
    is_active BOOLEAN DEFAULT TRUE,

    -- Electoral performance
    total_seats_2021 INTEGER,
    total_votes_2021 BIGINT,
    vote_share_2021 DECIMAL(5,2),

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Current major alliances (as of 2021 election)
INSERT INTO political_alliances (name, name_tamil, lead_party_code, member_parties, formation_date, is_active) VALUES
('DMK Alliance', 'திமுக கூட்டணி', 'DMK', ARRAY['DMK', 'INC', 'VCK', 'MDMK', 'CPI', 'CPM', 'IUML'], '2021-01-01', TRUE),
('AIADMK Alliance', 'அதிமுக கூட்டணி', 'AIADMK', ARRAY['AIADMK', 'BJP', 'PMK'], '2021-01-01', FALSE),
('NDA Alliance', 'தேசிய ஜனநாயக கூட்டணி', 'BJP', ARRAY['BJP', 'AIADMK', 'PMK'], '2024-01-01', TRUE);
-- Note: TVK might form its own alliance or remain independent
```

---

## Campaign Infrastructure Data

### 4. TVK Campaign Assets

**Files to Create**:
```
supabase/seeds/
├── 30_tvk_campaign_offices.sql         ⏳ MEDIUM PRIORITY
├── 31_tvk_booth_committees.sql         ⏳ MEDIUM PRIORITY
├── 32_tvk_volunteers.sql               ⏳ MEDIUM PRIORITY
└── 33_tvk_resources_inventory.sql      ⏳ LOW PRIORITY
```

#### 30_tvk_campaign_offices.sql

```sql
-- All TVK party offices (district, constituency, booth level)
-- Link to geographic hierarchy

CREATE TABLE IF NOT EXISTS campaign_offices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    party_code TEXT NOT NULL REFERENCES political_parties(code),

    office_type TEXT NOT NULL,                -- 'State HQ', 'District', 'Constituency', 'Booth'
    office_name TEXT NOT NULL,

    -- Location
    state_code TEXT REFERENCES states(code),
    district_code TEXT REFERENCES districts(code),
    constituency_code TEXT REFERENCES assembly_constituencies(code),
    address TEXT NOT NULL,
    location_lat DECIMAL(10,8),
    location_lng DECIMAL(11,8),

    -- Contact
    phone TEXT,
    email TEXT,
    in_charge_name TEXT,
    in_charge_phone TEXT,

    -- Capacity
    capacity INTEGER,                         -- Number of people it can accommodate
    has_meeting_room BOOLEAN DEFAULT FALSE,
    has_computers BOOLEAN DEFAULT FALSE,

    -- Status
    status TEXT DEFAULT 'Active',
    established_date DATE,

    tenant_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Voter Segments & Demographics

### 5. Voter Classification

**Files to Create**:
```
supabase/seeds/
├── 40_voter_segments.sql               ⏳ HIGH PRIORITY
├── 41_demographic_categories.sql       ⏳ HIGH PRIORITY
└── 42_voter_personas.sql               ⏳ MEDIUM PRIORITY
```

#### 40_voter_segments.sql

```sql
-- =====================================================
-- VOTER SEGMENTATION MASTER DATA
-- =====================================================

CREATE TABLE IF NOT EXISTS voter_segments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    segment_code TEXT UNIQUE NOT NULL,
    segment_name TEXT NOT NULL,
    segment_name_tamil TEXT,
    description TEXT,

    -- Classification
    segment_category TEXT,                    -- 'Age', 'Income', 'Occupation', 'Caste', 'Religion'

    -- Targeting strategy
    key_issues TEXT[],                        -- Issues this segment cares about
    preferred_channels TEXT[],                -- How to reach them: 'Social Media', 'Door-to-door', 'Rally'
    messaging_strategy TEXT,

    -- Estimated size in TN
    estimated_voters BIGINT,
    percentage_of_electorate DECIMAL(5,2),

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert voter segments
INSERT INTO voter_segments (segment_code, segment_name, segment_name_tamil, segment_category, key_issues, estimated_voters) VALUES

-- Age-based segments
('Y18-25', 'Youth (18-25)', 'இளைஞர்கள் (18-25)', 'Age', ARRAY['Jobs', 'Education', 'Technology'], 8500000),
('A26-35', 'Young Adults (26-35)', 'இளம் வயது (26-35)', 'Age', ARRAY['Jobs', 'Housing', 'Healthcare'], 12000000),
('M36-50', 'Middle Age (36-50)', 'நடுத்தர வயது (36-50)', 'Age', ARRAY['Economy', 'Children Education', 'Healthcare'], 15000000),
('S51', 'Senior Citizens (51+)', 'மூத்த குடிமக்கள் (51+)', 'Age', ARRAY['Pension', 'Healthcare', 'Law & Order'], 10000000),

-- Occupation-based segments
('FARM', 'Farmers', 'விவசாயிகள்', 'Occupation', ARRAY['Agriculture', 'Water', 'MSP'], 8000000),
('LABOR', 'Labourers', 'தொழிலாளர்கள்', 'Occupation', ARRAY['Wages', 'Social Security', 'Housing'], 12000000),
('GOVT', 'Government Employees', 'அரசு ஊழியர்கள்', 'Occupation', ARRAY['Salary', 'Pension', 'Job Security'], 2000000),
('PRIV', 'Private Sector', 'தனியார் துறை', 'Occupation', ARRAY['Jobs', 'Economy', 'Infrastructure'], 10000000),
('BUS', 'Business Owners', 'வணிகர்கள்', 'Occupation', ARRAY['Economy', 'Tax', 'Infrastructure'], 3000000),
('STUD', 'Students', 'மாணவர்கள்', 'Occupation', ARRAY['Education', 'Jobs', 'Skills'], 5000000),

-- Income-based segments
('INC_LOW', 'Low Income', 'குறைந்த வருமானம்', 'Income', ARRAY['Employment', 'Welfare', 'Healthcare'], 18000000),
('INC_MID', 'Middle Income', 'நடுத்தர வருமானம்', 'Income', ARRAY['Infrastructure', 'Education', 'Healthcare'], 20000000),
('INC_HIGH', 'High Income', 'அதிக வருமானம்', 'Income', ARRAY['Economy', 'Infrastructure', 'Law & Order'], 3000000),

-- Urban/Rural
('URBAN', 'Urban Voters', 'நகர்ப்புற வாக்காளர்கள்', 'Geography', ARRAY['Infrastructure', 'Traffic', 'Pollution'], 18000000),
('RURAL', 'Rural Voters', 'கிராமப்புற வாக்காளர்கள்', 'Geography', ARRAY['Agriculture', 'Water', 'Electricity'], 23000000),

-- Caste-based (SC/ST/OBC/General)
('SC', 'Scheduled Castes', 'அட்டவணை சாதியினர்', 'Social', ARRAY['Social Justice', 'Reservation', 'Welfare'], 10000000),
('ST', 'Scheduled Tribes', 'அட்டவணை பழங்குடியினர்', 'Social', ARRAY['Tribal Welfare', 'Forest Rights', 'Education'], 500000),
('OBC', 'Other Backward Classes', 'பிற்படுத்தப்பட்ட வகுப்பினர்', 'Social', ARRAY['Reservation', 'Education', 'Jobs'], 20000000),
('GEN', 'General Category', 'பொது பிரிவினர்', 'Social', ARRAY['Merit', 'Economy', 'Infrastructure'], 10000000),

-- Religion-based
('HINDU', 'Hindus', 'இந்துக்கள்', 'Religion', ARRAY['Temple Rights', 'Culture', 'Education'], 35000000),
('MUSLIM', 'Muslims', 'முஸ்லிம்கள்', 'Religion', ARRAY['Minority Welfare', 'Education', 'Jobs'], 3500000),
('CHRISTIAN', 'Christians', 'கிறிஸ்தவர்கள்', 'Religion', ARRAY['Minority Rights', 'Education', 'Healthcare'], 3000000),

-- Gender
('MALE', 'Male Voters', 'ஆண் வாக்காளர்கள்', 'Gender', ARRAY['Jobs', 'Economy', 'Infrastructure'], 22000000),
('FEMALE', 'Female Voters', 'பெண் வாக்காளர்கள்', 'Gender', ARRAY['Safety', 'Healthcare', 'Education'], 23000000),
('FTV', 'First-Time Voters', 'முதல் முறை வாக்காளர்கள்', 'Age', ARRAY['Jobs', 'Education', 'Future'], 4000000);
```

---

## Issue Categories

### 6. Key Issues for TVK Campaign

**Files to Create**:
```
supabase/seeds/
├── 50_issue_categories.sql             ⏳ HIGH PRIORITY
└── 51_tvk_issue_positions.sql          ⏳ MEDIUM PRIORITY
```

#### 50_issue_categories.sql

```sql
-- =====================================================
-- ISSUE CATEGORIES FOR TAMIL NADU POLITICS
-- =====================================================

CREATE TABLE IF NOT EXISTS issue_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    name_tamil TEXT,
    description TEXT,

    -- Classification
    category TEXT,                            -- 'Economic', 'Social', 'Infrastructure', 'Governance'
    priority_level TEXT,                      -- 'High', 'Medium', 'Low'

    -- Relevance
    relevant_segments TEXT[],                 -- Which voter segments care about this
    geographic_focus TEXT[],                  -- 'Urban', 'Rural', 'Coastal', 'All'

    -- Keywords for sentiment analysis
    keywords TEXT[],
    hashtags TEXT[],

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert key Tamil Nadu issues
INSERT INTO issue_categories (code, name, name_tamil, category, priority_level, relevant_segments, keywords) VALUES

-- Economic Issues
('JOBS', 'Employment & Jobs', 'வேலைவாய்ப்பு', 'Economic', 'High', ARRAY['Y18-25', 'A26-35', 'STUD'], ARRAY['jobs', 'employment', 'unemployment', 'recruitment']),
('AGRI', 'Agriculture & Farmers', 'விவசாயம் & விவசாயிகள்', 'Economic', 'High', ARRAY['FARM', 'RURAL'], ARRAY['agriculture', 'farmers', 'crop', 'MSP', 'irrigation']),
('ECON', 'Economic Development', 'பொருளாதார வளர்ச்சி', 'Economic', 'High', ARRAY['BUS', 'INC_MID', 'INC_HIGH'], ARRAY['economy', 'GDP', 'growth', 'investment']),

-- Social Issues
('EDU', 'Education', 'கல்வி', 'Social', 'High', ARRAY['STUD', 'Y18-25', 'FEMALE'], ARRAY['education', 'schools', 'colleges', 'students']),
('HEALTH', 'Healthcare', 'சுகாதாரம்', 'Social', 'High', ARRAY['S51', 'FEMALE', 'INC_LOW'], ARRAY['health', 'hospital', 'medicine', 'doctor']),
('WOMEN', 'Women Safety & Empowerment', 'பெண்கள் பாதுகாப்பு', 'Social', 'High', ARRAY['FEMALE'], ARRAY['women', 'safety', 'empowerment', 'harassment']),
('SOCIAL_JUSTICE', 'Social Justice', 'சமூக நீதி', 'Social', 'High', ARRAY['SC', 'ST', 'OBC'], ARRAY['reservation', 'social justice', 'equality', 'caste']),

-- Infrastructure
('INFRA', 'Infrastructure', 'உள்கட்டமைப்பு', 'Infrastructure', 'High', ARRAY['URBAN', 'BUS'], ARRAY['infrastructure', 'roads', 'metro', 'flyover']),
('WATER', 'Water Supply', 'நீர் வழங்கல்', 'Infrastructure', 'High', ARRAY['FARM', 'RURAL', 'URBAN'], ARRAY['water', 'drinking water', 'irrigation', 'cauvery']),
('POWER', 'Electricity', 'மின்சாரம்', 'Infrastructure', 'Medium', ARRAY['FARM', 'BUS', 'URBAN'], ARRAY['electricity', 'power cut', 'power supply']),
('TRANSPORT', 'Public Transport', 'பொது போக்குவரத்து', 'Infrastructure', 'Medium', ARRAY['URBAN', 'LABOR'], ARRAY['transport', 'bus', 'metro', 'train']),

-- Governance
('CORRUPT', 'Corruption', 'ஊழல்', 'Governance', 'High', ARRAY['ALL'], ARRAY['corruption', 'scam', 'bribe', 'fraud']),
('LAW_ORDER', 'Law & Order', 'சட்டம் & ஒழுங்கு', 'Governance', 'High', ARRAY['URBAN', 'FEMALE'], ARRAY['law', 'police', 'crime', 'safety']),
('ADMIN', 'Administration', 'நிர்வாகம்', 'Governance', 'Medium', ARRAY['ALL'], ARRAY['administration', 'government', 'bureaucracy']),

-- Regional Issues
('TAMIL', 'Tamil Language & Culture', 'தமிழ் மொழி & பண்பாடு', 'Cultural', 'High', ARRAY['ALL'], ARRAY['tamil', 'language', 'culture', 'heritage']),
('CAUVERY', 'Cauvery Water Dispute', 'காவிரி நீர் பிரச்சனை', 'Regional', 'High', ARRAY['FARM', 'RURAL'], ARRAY['cauvery', 'water dispute', 'karnataka']),
('NEET', 'NEET Exam Issue', 'நீட் தேர்வு', 'Education', 'High', ARRAY['STUD', 'Y18-25'], ARRAY['NEET', 'medical admission', 'entrance exam']),

-- Environment
('ENVIRON', 'Environment & Pollution', 'சுற்றுச்சூழல்', 'Environment', 'Medium', ARRAY['URBAN'], ARRAY['environment', 'pollution', 'climate', 'air quality']),
('COAST', 'Coastal & Fisheries', 'கடலோர & மீன்வளம்', 'Economic', 'Medium', ARRAY['RURAL'], ARRAY['fishermen', 'coastal', 'fishing', 'livelihood']);
```

---

## Media & Influencers

### 7. Media Outlets Database

**Files to Create**:
```
supabase/seeds/
├── 60_media_outlets.sql                ⏳ MEDIUM PRIORITY
├── 61_news_channels.sql                ⏳ MEDIUM PRIORITY
├── 62_social_platforms.sql             ⏳ LOW PRIORITY
└── 63_influencers_database.sql         ⏳ MEDIUM PRIORITY
```

#### 60_media_outlets.sql

```sql
-- =====================================================
-- TAMIL NADU MEDIA OUTLETS
-- =====================================================

CREATE TABLE IF NOT EXISTS media_outlets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    name_tamil TEXT,
    media_type TEXT NOT NULL,                 -- 'TV', 'Print', 'Online', 'Radio'
    category TEXT,                            -- 'News', 'Entertainment', 'Regional'

    -- Reach
    primary_language TEXT,                    -- 'Tamil', 'English', 'Bilingual'
    circulation BIGINT,                       -- For print
    viewership BIGINT,                        -- For TV
    monthly_visitors BIGINT,                  -- For online

    -- Contact
    website TEXT,
    twitter_handle TEXT,
    youtube_channel TEXT,

    -- Political lean (if any)
    political_lean TEXT,                      -- 'Left', 'Right', 'Center', 'Neutral', 'Unknown'

    -- Geographic coverage
    coverage_area TEXT[],                     -- ['TN', 'PY', 'National']

    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert major Tamil Nadu media outlets
INSERT INTO media_outlets (name, name_tamil, media_type, primary_language, political_lean, coverage_area) VALUES

-- TV Channels
('Sun TV', 'சன் டிவி', 'TV', 'Tamil', 'Neutral', ARRAY['TN', 'PY']),
('Puthiya Thalaimurai', 'புதிய தலைமுறை', 'TV', 'Tamil', 'Neutral', ARRAY['TN', 'PY']),
('Polimer News', 'பாலிமர் செய்திகள்', 'TV', 'Tamil', 'Neutral', ARRAY['TN', 'PY']),
('News 7 Tamil', 'நியூஸ் 7 தமிழ்', 'TV', 'Tamil', 'Neutral', ARRAY['TN', 'PY']),
('Thanthi TV', 'தந்தி டிவி', 'TV', 'Tamil', 'Neutral', ARRAY['TN', 'PY']),

-- Newspapers
('Dinamalar', 'தினமலர்', 'Print', 'Tamil', 'Neutral', ARRAY['TN', 'PY']),
('Dinamani', 'தினமணி', 'Print', 'Tamil', 'Neutral', ARRAY['TN', 'PY']),
('Dinathanthi', 'தினத்தந்தி', 'Print', 'Tamil', 'Neutral', ARRAY['TN', 'PY']),
('The Hindu (Tamil)', 'தி இந்து', 'Print', 'Tamil', 'Center', ARRAY['TN', 'PY', 'National']),
('Tamil Murasu', 'தமிழ் முரசு', 'Print', 'Tamil', 'Neutral', ARRAY['TN', 'PY']),

-- Online News
('Vikatan', 'விகடன்', 'Online', 'Tamil', 'Neutral', ARRAY['TN', 'PY']),
('The News Minute', 'தி நியூஸ் மினட்', 'Online', 'English', 'Left', ARRAY['TN', 'PY', 'National']),
('NewsTap', 'நியூஸ் டேப்', 'Online', 'Tamil', 'Neutral', ARRAY['TN', 'PY']);
```

---

## Historical Elections

### 8. Past Election Results

**Files to Create**:
```
supabase/seeds/
├── 70_election_2021_results.sql        ⏳ HIGH PRIORITY
├── 71_election_2016_results.sql        ⏳ MEDIUM PRIORITY
└── 72_election_trends.sql              ⏳ LOW PRIORITY
```

#### 70_election_2021_results.sql

```sql
-- =====================================================
-- 2021 TAMIL NADU ASSEMBLY ELECTION RESULTS
-- =====================================================

-- Already partially covered in elected_members table
-- Expand with more details:

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

-- Example: Complete 2021 results for all 234 constituencies
('TN001', 'K. Selvam', 'DMK', 'DMK Alliance', 2021, '2021-05-07', '2026-05-06', 108523, 52.3, 15234, 207500, TRUE),
-- ... (Add all 234 constituencies)

-- This data helps with:
-- 1. Understanding voting patterns
-- 2. Identifying swing constituencies
-- 3. Analyzing alliance performance
-- 4. Targeting winnable seats for TVK
```

---

## Sample Sentiment Data

### 9. Demo/Test Data

**Files to Create**:
```
supabase/seeds/
├── 80_sample_sentiment_data.sql        ⏳ LOW PRIORITY (Testing)
├── 81_sample_social_posts.sql          ⏳ LOW PRIORITY (Testing)
└── 82_sample_field_reports.sql         ⏳ LOW PRIORITY (Testing)
```

**Purpose**: For testing dashboards and analytics before real data flows in

---

## Implementation Priority

### 🔴 **HIGH PRIORITY** (Implement First - Week 1)

1. ✅ **Geography Masters** (Foundation)
   - ✅ Constituencies seed template
   - ⏳ States seed
   - ⏳ Districts seed

2. **TVK Party Structure** (Your Organization)
   - ⏳ TVK party information
   - ⏳ TVK leadership
   - ⏳ TVK district units

3. **Voter Segments** (Know Your Audience)
   - ⏳ Voter segmentation
   - ⏳ Demographic categories

4. **Issue Categories** (Campaign Topics)
   - ⏳ Key issues for Tamil Nadu
   - ⏳ TVK's positions on issues

5. **Political Parties** (Competition)
   - ⏳ All Tamil Nadu parties
   - ⏳ Political alliances

6. **2021 Election Results** (Baseline Data)
   - ⏳ Complete constituency-wise results

---

### 🟡 **MEDIUM PRIORITY** (Week 2-3)

7. **TVK Campaign Infrastructure**
   - Campaign offices
   - Booth committees
   - Volunteers

8. **Media Outlets**
   - TV channels, newspapers
   - Online news platforms

9. **Influencer Database**
   - Political influencers
   - Social media influencers
   - Celebrity supporters

10. **Historical Elections**
    - 2016 results
    - Past trends

---

### 🟢 **LOW PRIORITY** (Week 4+)

11. **Polling Booths** (70,000+ records)
    - Can be loaded incrementally by district
    - Or on-demand based on user selection

12. **Sample Data** (For Testing)
    - Sample sentiment data
    - Sample social posts
    - Sample field reports

13. **Advanced Analytics**
    - Party performance trends
    - Swing analysis
    - Voter migration patterns

---

## Quick Start Implementation

### Step 1: Run These in Order (Today)

```bash
# Already created:
# ✅ 01_constituency_seed_template.sql

# Create these next:
# 1. States
psql $DATABASE_URL -f supabase/seeds/02_states_seed.sql

# 2. Districts
psql $DATABASE_URL -f supabase/seeds/03_districts_seed.sql

# 3. TVK Party
psql $DATABASE_URL -f supabase/seeds/10_tvk_party_structure.sql

# 4. All Parties
psql $DATABASE_URL -f supabase/seeds/20_all_parties_seed.sql

# 5. Voter Segments
psql $DATABASE_URL -f supabase/seeds/40_voter_segments.sql

# 6. Issue Categories
psql $DATABASE_URL -f supabase/seeds/50_issue_categories.sql
```

### Step 2: Verify Data

```sql
-- Check states
SELECT * FROM states;

-- Check districts count
SELECT state_code, COUNT(*) as district_count FROM districts GROUP BY state_code;

-- Check TVK party
SELECT * FROM political_parties WHERE code = 'TVK';

-- Check voter segments
SELECT segment_category, COUNT(*) as count FROM voter_segments GROUP BY segment_category;

-- Check issues
SELECT category, COUNT(*) as count FROM issue_categories GROUP BY category;
```

---

## Data Sources

### Where to Get This Data

1. **Geographic Data**:
   - Election Commission of India: https://eci.gov.in
   - Tamil Nadu CEO: https://www.elections.tn.gov.in
   - OpenStreetMap

2. **Election Results**:
   - EC India historical data
   - News archives (The Hindu, Indian Express)
   - Political analysis sites

3. **Party Information**:
   - Official party websites
   - Wikipedia
   - News articles

4. **Voter Demographics**:
   - Census data
   - EC voter statistics
   - Political surveys

5. **Media Outlets**:
   - ABC (Audit Bureau of Circulations)
   - BARC (TV ratings)
   - SimilarWeb (web traffic)

---

## Summary

### Must-Have Seed Files (Priority Order)

1. ✅ `01_constituency_seed_template.sql` - Template created
2. ⏳ `02_states_seed.sql` - 2 records (TN, PY)
3. ⏳ `03_districts_seed.sql` - 42 records (38 TN + 4 PY)
4. ⏳ `10_tvk_party_structure.sql` - TVK party info
5. ⏳ `11_tvk_leadership.sql` - TVK leaders
6. ⏳ `20_all_parties_seed.sql` - All TN parties
7. ⏳ `21_political_alliances.sql` - Current alliances
8. ⏳ `40_voter_segments.sql` - 20-30 segments
9. ⏳ `50_issue_categories.sql` - 15-20 key issues
10. ⏳ `70_election_2021_results.sql` - Baseline election data

---

**Next Steps**:
1. Create files 02-10 from the list above
2. Run migrations to create new tables (political_parties, voter_segments, issue_categories)
3. Import seed data
4. Verify everything works
5. Start building UI components that use this data

Would you like me to create any specific seed file from this list?
