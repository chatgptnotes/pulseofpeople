-- =====================================================
-- ISSUE CATEGORIES
-- Key Political Issues for Tamil Nadu Elections
-- TVK Campaign Focus Areas
-- Date: 2025-11-08
-- =====================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- 1. ISSUE CATEGORIES TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS issue_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    name_tamil TEXT NOT NULL,
    description TEXT,
    detailed_description TEXT,

    -- Classification
    category TEXT NOT NULL,                   -- 'Economic', 'Social', 'Infrastructure', 'Governance', 'Cultural', 'Regional'
    sub_category TEXT,
    parent_issue TEXT,                        -- For hierarchical grouping

    -- Priority and relevance
    priority_level TEXT NOT NULL CHECK (priority_level IN ('Critical', 'High', 'Medium', 'Low')),
    tvk_stance TEXT,                          -- TVK's position on this issue
    tvk_priority TEXT CHECK (tvk_priority IN ('Top', 'High', 'Medium', 'Low')),

    -- Relevance mapping
    relevant_segments TEXT[],                 -- Which voter segments care about this
    geographic_focus TEXT[],                  -- 'Urban', 'Rural', 'Coastal', 'All', 'Chennai', 'South TN', etc.
    relevant_districts TEXT[],                -- Specific district codes where this is hot

    -- Sentiment tracking
    keywords TEXT[],                          -- For sentiment analysis
    hashtags TEXT[],                          -- For social media monitoring
    related_hashtags TEXT[],

    -- Political context
    incumbent_performance TEXT,               -- How DMK government is performing on this
    opposition_stance TEXT,                   -- What AIADMK/BJP are saying
    media_coverage_level TEXT CHECK (media_coverage_level IN ('Very High', 'High', 'Medium', 'Low')),

    -- Campaign strategy
    messaging_points TEXT[],                  -- Key talking points for TVK
    target_demographics TEXT[],
    campaign_activities TEXT[],               -- Suggested campaign activities

    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    is_hot_topic BOOLEAN DEFAULT FALSE,       -- Currently trending
    season TEXT,                              -- When this issue peaks: 'Monsoon', 'Summer', 'Election Time', 'Always'
    notes TEXT,

    -- Multi-tenancy
    tenant_id TEXT,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,

    -- Constraints
    CONSTRAINT valid_category CHECK (category IN (
        'Economic', 'Social', 'Infrastructure', 'Governance',
        'Cultural', 'Regional', 'Environmental', 'Education', 'Healthcare'
    ))
);

-- Create indexes
CREATE INDEX idx_issue_categories_code ON issue_categories(code);
CREATE INDEX idx_issue_categories_category ON issue_categories(category);
CREATE INDEX idx_issue_categories_priority ON issue_categories(priority_level);
CREATE INDEX idx_issue_categories_tvk_priority ON issue_categories(tvk_priority);
CREATE INDEX idx_issue_categories_hot_topic ON issue_categories(is_hot_topic);
CREATE INDEX idx_issue_categories_keywords ON issue_categories USING GIN(keywords);

-- =====================================================
-- 2. INSERT ISSUES - ECONOMIC CATEGORY
-- =====================================================

INSERT INTO issue_categories (
    code, name, name_tamil, description, detailed_description, category,
    priority_level, tvk_stance, tvk_priority, relevant_segments,
    geographic_focus, keywords, hashtags, messaging_points,
    incumbent_performance, media_coverage_level, is_hot_topic
) VALUES

-- JOBS - CRITICAL ISSUE
(
    'JOBS',
    'Employment & Job Creation',
    'வேலைவாய்ப்பு',
    'Unemployment crisis, especially among educated youth',
    'Tamil Nadu has high educated unemployment. Youth are migrating to other states. Private sector job growth is slow. Government job recruitment has delays.',
    'Economic',
    'Critical',
    'Promise 1 crore jobs in 5 years. Focus on IT, manufacturing, start-ups. Fast-track government recruitment.',
    'Top',
    ARRAY['AGE_18_25', 'AGE_26_35', 'OCC_UNEMPLOYED', 'OCC_STUDENTS', 'OCC_PRIVATE', 'GEO_URBAN'],
    ARRAY['All', 'Urban'],
    ARRAY['jobs', 'employment', 'unemployment', 'recruitment', 'வேலைவாய்ப்பு', 'தொழில்வாய்ப்பு'],
    ARRAY['#JobsForTN', '#TNUnemployment', '#YouthJobs', '#வேலைவாய்ப்பு'],
    ARRAY[
        'Create 1 crore jobs in 5 years',
        'Fast-track all pending government recruitments',
        'Attract major IT and manufacturing companies',
        'Support start-ups and entrepreneurship',
        'Skills training for unemployed youth'
    ],
    'Mixed - Some IT growth but unemployment remains high',
    'Very High',
    TRUE
),

-- AGRICULTURE
(
    'AGRICULTURE',
    'Agriculture & Farmers Welfare',
    'விவசாயம் மற்றும் விவசாயிகள் நலன்',
    'Farm distress, water scarcity, low crop prices, debt',
    'Tamil Nadu farmers face severe challenges: water scarcity, low MSP, rising input costs, debt burden. Farm suicides continue. Need comprehensive support.',
    'Economic',
    'Critical',
    'Comprehensive farm loan waiver. Implement Swaminathan Commission recommendations. Ensure water for all farms. MSP guarantee.',
    'Top',
    ARRAY['OCC_FARMERS', 'GEO_RURAL', 'GEO_SOUTH_TN'],
    ARRAY['Rural', 'All'],
    ARRAY['agriculture', 'farmers', 'farm loan', 'MSP', 'crop', 'irrigation', 'விவசாயம்', 'விவசாயிகள்'],
    ARRAY['#FarmerRights', '#TNFarmers', '#LoanWaiver', '#விவசாயிகள்'],
    ARRAY[
        'Complete farm loan waiver',
        'MSP for all crops',
        'Free electricity for farm wells',
        'Modern irrigation facilities',
        'Direct income support ₹10,000/month'
    ],
    'Some schemes but farm distress continues',
    'High',
    TRUE
),

-- ECONOMY
(
    'ECONOMY',
    'Economic Development',
    'பொருளாதார வளர்ச்சி',
    'State economy, GDP growth, investment climate',
    'TN needs to attract more investments, create better business environment, boost GDP growth. Manufacturing and services sectors need push.',
    'Economic',
    'High',
    'Make TN the #1 investment destination in India. Ease of doing business. Support MSME sector.',
    'High',
    ARRAY['OCC_BUSINESS', 'OCC_PRIVATE', 'INC_HIGH', 'GEO_COIMBATORE'],
    ARRAY['Urban', 'All'],
    ARRAY['economy', 'GDP', 'growth', 'investment', 'business', 'பொருளாதாரம்'],
    ARRAY['#TNEconomy', '#InvestInTN', '#BusinessGrowth'],
    ARRAY[
        'Single-window clearance for industries',
        'Tax incentives for manufacturing',
        'Support for MSMEs',
        'World-class infrastructure'
    ],
    'Moderate - Some growth but more needed',
    'Medium',
    FALSE
),

-- START-UP ECOSYSTEM
(
    'STARTUPS',
    'Start-up Ecosystem',
    'தொடக்க நிறுவனங்கள்',
    'Support for entrepreneurs, start-ups, innovation',
    'TN has potential to be a major start-up hub but lacks ecosystem support. Need funding, mentorship, infrastructure.',
    'Economic',
    'High',
    'Create TN Start-up Fund worth ₹1000 crore. Build innovation hubs in all major cities. Tax holidays for start-ups.',
    'High',
    ARRAY['AGE_18_25', 'AGE_26_35', 'OCC_STUDENTS', 'OCC_PRIVATE', 'GEO_URBAN', 'GEO_CHENNAI'],
    ARRAY['Urban', 'Chennai', 'Coimbatore'],
    ARRAY['startup', 'entrepreneur', 'innovation', 'funding', 'incubator'],
    ARRAY['#TNStartups', '#Innovation', '#Entrepreneurship'],
    ARRAY[
        'Start-up fund of ₹1000 crore',
        'Innovation hubs in all districts',
        '5-year tax holiday',
        'Mentorship programs'
    ],
    'Limited initiatives, needs major push',
    'Medium',
    FALSE
);

-- =====================================================
-- 3. INSERT ISSUES - SOCIAL CATEGORY
-- =====================================================

INSERT INTO issue_categories (
    code, name, name_tamil, description, detailed_description, category,
    priority_level, tvk_stance, tvk_priority, relevant_segments,
    geographic_focus, keywords, hashtags, messaging_points,
    incumbent_performance, media_coverage_level, is_hot_topic
) VALUES

-- EDUCATION
(
    'EDUCATION',
    'Education Quality',
    'கல்வி தரம்',
    'School and college education, quality, access, affordability',
    'Government schools lack infrastructure. Teacher shortage. Private education is expensive. Need to improve quality across the board.',
    'Education',
    'Critical',
    'World-class government schools. More engineering and medical colleges. Free quality education for all.',
    'Top',
    ARRAY['AGE_18_25', 'OCC_STUDENTS', 'GEN_FEMALE', 'INC_LOW', 'INC_MIDDLE'],
    ARRAY['All'],
    ARRAY['education', 'schools', 'colleges', 'students', 'teachers', 'கல்வி', 'பள்ளி'],
    ARRAY['#QualityEducation', '#TNSchools', '#FreeEducation', '#கல்வி'],
    ARRAY[
        'Model schools in every constituency',
        'More colleges and universities',
        'Free laptops and tablets for students',
        'Teacher recruitment on priority',
        'Skill development centers'
    ],
    'Breakfast scheme good, but infrastructure needs work',
    'High',
    TRUE
),

-- NEET EXAM - HOT TOPIC IN TN
(
    'NEET',
    'NEET Exam Opposition',
    'நீட் தேர்வு எதிர்ப்பு',
    'Medical entrance exam NEET, opposition from TN',
    'NEET is seen as unfair to Tamil Nadu students, especially rural and government school students. Demand for exemption or scrapping.',
    'Education',
    'Critical',
    'Strong opposition to NEET. Demand exemption for TN. Restore old admission system based on Class 12 marks.',
    'Top',
    ARRAY['AGE_18_25', 'OCC_STUDENTS', 'GEO_RURAL', 'INC_LOW', 'INC_MIDDLE'],
    ARRAY['All', 'Rural'],
    ARRAY['NEET', 'medical admission', 'entrance exam', 'நீட்', 'மருத்துவ சேர்க்கை'],
    ARRAY['#StopNEET', '#NEETHurtsRural', '#JusticeForStudents', '#நீட்எதிர்ப்பு'],
    ARRAY[
        'Will pass bill in assembly against NEET',
        'Restore admission based on 12th marks',
        'Free NEET coaching for rural students meanwhile',
        'Justice for students who lost opportunities'
    ],
    'Bill passed but needs Governor/Central approval',
    'Very High',
    TRUE
),

-- HEALTHCARE
(
    'HEALTHCARE',
    'Healthcare Services',
    'சுகாதாரம்',
    'Public health infrastructure, hospitals, medicines',
    'Government hospitals overcrowded. Doctor shortage. Need more primary health centers. Expensive private healthcare.',
    'Healthcare',
    'Critical',
    'Strengthen government hospitals. Free medicines and tests. More doctors and nurses. Health insurance for all.',
    'High',
    ARRAY['AGE_36_50', 'AGE_51_PLUS', 'GEN_FEMALE', 'INC_LOW', 'INC_MIDDLE', 'GEO_RURAL'],
    ARRAY['All'],
    ARRAY['health', 'hospital', 'doctor', 'medicine', 'healthcare', 'சுகாதாரம்', 'மருத்துவம்'],
    ARRAY['#HealthForAll', '#TNHealthcare', '#FreeHealthcare'],
    ARRAY[
        'One government hospital per constituency',
        'Free medicines for all',
        'More doctors and nurses',
        'Mobile health clinics for villages',
        '₹5 lakh health insurance for families'
    ],
    'Decent but needs expansion and upgrades',
    'High',
    FALSE
),

-- SOCIAL JUSTICE
(
    'SOCIAL_JUSTICE',
    'Social Justice & Equality',
    'சமூக நீதி',
    'Caste equality, reservation, anti-discrimination',
    'Social justice is central to TN politics. Protection of reservation, affirmative action, anti-caste discrimination measures.',
    'Social',
    'High',
    'Protect and expand reservation. Ensure social equality. Punish caste-based discrimination. Empowerment of marginalized.',
    'High',
    ARRAY['SOC_SC', 'SOC_ST', 'SOC_OBC'],
    ARRAY['All'],
    ARRAY['social justice', 'reservation', 'equality', 'caste', 'discrimination', 'சமூக நீதி', 'இடஒதுக்கீடு'],
    ARRAY['#SocialJustice', '#ReservationRights', '#Equality'],
    ARRAY[
        'Protect reservation in all sectors',
        'Stringent laws against discrimination',
        'Special courts for atrocity cases',
        'Empowerment funds for SC/ST/OBC'
    ],
    'Generally supportive, continues Dravidian legacy',
    'Medium',
    FALSE
),

-- WOMEN SAFETY
(
    'WOMEN_SAFETY',
    'Women Safety & Empowerment',
    'பெண்கள் பாதுகாப்பு',
    'Safety, crimes against women, empowerment, equal opportunities',
    'Increasing crimes against women. Need better safety measures, faster justice, economic empowerment.',
    'Social',
    'Critical',
    'Zero tolerance for crimes against women. Fast-track courts. Women-only police stations. Economic empowerment programs.',
    'High',
    ARRAY['GEN_FEMALE', 'AGE_18_25', 'AGE_26_35'],
    ARRAY['Urban', 'All'],
    ARRAY['women safety', 'women rights', 'harassment', 'empowerment', 'பெண்கள் பாதுகாப்பு'],
    ARRAY['#WomenSafety', '#TNWomen', '#SafeTN'],
    ARRAY[
        'Women-only police stations in all districts',
        'Fast-track courts for crimes against women',
        'Self-defense training programs',
        'Economic empowerment schemes',
        '33% reservation for women in government jobs'
    ],
    'Mixed - Some schemes but crimes continue',
    'Very High',
    TRUE
);

-- =====================================================
-- 4. INSERT ISSUES - INFRASTRUCTURE CATEGORY
-- =====================================================

INSERT INTO issue_categories (
    code, name, name_tamil, description, detailed_description, category,
    priority_level, tvk_stance, tvk_priority, relevant_segments,
    geographic_focus, keywords, hashtags, messaging_points,
    incumbent_performance, media_coverage_level, is_hot_topic
) VALUES

-- WATER SUPPLY
(
    'WATER',
    'Water Supply & Management',
    'நீர் வழங்கல்',
    'Drinking water, irrigation, water scarcity',
    'Severe water crisis in summer. Chennai faces acute shortage. Villages depend on tankers. Cauvery dispute affects farmers.',
    'Infrastructure',
    'Critical',
    'Permanent solution to water crisis. Desalination plants. Inter-linking of rivers. Rainwater harvesting mandatory.',
    'Top',
    ARRAY['OCC_FARMERS', 'GEO_RURAL', 'GEO_CHENNAI', 'GEO_SOUTH_TN'],
    ARRAY['All'],
    ARRAY['water', 'drinking water', 'water crisis', 'irrigation', 'cauvery', 'நீர்', 'குடிநீர்'],
    ARRAY['#WaterForTN', '#CauveryWater', '#TNWaterCrisis', '#நீர்பஞ்சம்'],
    ARRAY[
        '10 new desalination plants for Chennai',
        'Ensure Cauvery water for TN farmers',
        'Mandatory rainwater harvesting',
        '24x7 drinking water for all villages',
        'Modernize irrigation infrastructure'
    ],
    'Some progress but crisis remains in summer',
    'Very High',
    TRUE
),

-- INFRASTRUCTURE
(
    'INFRASTRUCTURE',
    'Roads & Infrastructure',
    'சாலை மற்றும் உள்கட்டமைப்பு',
    'Roads, flyovers, bridges, public infrastructure',
    'Road quality poor in many areas. Traffic congestion in cities. Need better infrastructure for development.',
    'Infrastructure',
    'High',
    'World-class roads and infrastructure. Six-lane highways. Modern bridges. Urban infrastructure upgrade.',
    'High',
    ARRAY['GEO_URBAN', 'GEO_CHENNAI', 'OCC_BUSINESS', 'INC_MIDDLE', 'INC_HIGH'],
    ARRAY['Urban', 'All'],
    ARRAY['infrastructure', 'roads', 'flyover', 'bridge', 'highway', 'சாலை', 'உள்கட்டமைப்பு'],
    ARRAY['#TNInfrastructure', '#BetterRoads', '#ModernTN'],
    ARRAY[
        'All highways to six-lane standard',
        'Flyovers at major traffic points',
        'Rural road connectivity 100%',
        'Modern bus terminals and railway stations'
    ],
    'Good progress in some areas, mixed overall',
    'Medium',
    FALSE
),

-- CHENNAI METRO
(
    'METRO',
    'Chennai Metro Expansion',
    'சென்னை மெட்ரோ விரிவாக்கம்',
    'Metro rail expansion, public transport',
    'Chennai Metro Phase 1 success but needs rapid expansion to cover entire city and suburbs. Reduce traffic congestion.',
    'Infrastructure',
    'High',
    'Fast-track Metro expansion to all Chennai suburbs. Connect airport, key IT corridors. Affordable fares.',
    'High',
    ARRAY['GEO_CHENNAI', 'GEO_URBAN', 'OCC_PRIVATE', 'AGE_26_35'],
    ARRAY['Chennai'],
    ARRAY['metro', 'Chennai metro', 'public transport', 'rail', 'மெட்ரோ'],
    ARRAY['#ChennaiMetro', '#TNMetro', '#PublicTransport'],
    ARRAY[
        'Complete Phase 2 in 3 years',
        'Start Phase 3 immediately',
        'Connect all suburbs',
        'Student and senior citizen discounts'
    ],
    'Phase 2 under construction, needs faster pace',
    'Medium',
    FALSE
),

-- ELECTRICITY
(
    'ELECTRICITY',
    'Power Supply',
    'மின்சார வழங்கல்',
    'Electricity supply, power cuts, tariffs',
    'Frequent power cuts in summer. High electricity bills. Industrial power needs. Need stable, affordable power.',
    'Infrastructure',
    'High',
    'Uninterrupted 24x7 power supply. No power cuts. Reduce electricity tariffs. Promote solar and renewable energy.',
    'Medium',
    ARRAY['OCC_FARMERS', 'OCC_BUSINESS', 'GEO_RURAL', 'INC_LOW', 'INC_MIDDLE'],
    ARRAY['All', 'Rural'],
    ARRAY['electricity', 'power', 'power cut', 'tariff', 'மின்சாரம்', 'மின்வெட்டு'],
    ARRAY['#PowerForTN', '#NoPowerCuts', '#மின்சாரம்'],
    ARRAY[
        '24x7 power for all',
        'Free electricity for farmers',
        'Reduce domestic tariffs',
        'Solar power incentives'
    ],
    'Improved but power cuts still occur',
    'Medium',
    FALSE
);

-- =====================================================
-- 5. INSERT ISSUES - GOVERNANCE CATEGORY
-- =====================================================

INSERT INTO issue_categories (
    code, name, name_tamil, description, detailed_description, category,
    priority_level, tvk_stance, tvk_priority, relevant_segments,
    geographic_focus, keywords, hashtags, messaging_points,
    incumbent_performance, media_coverage_level, is_hot_topic
) VALUES

-- CORRUPTION
(
    'CORRUPTION',
    'Anti-Corruption',
    'ஊழல் ஒழிப்பு',
    'Corruption in government, bribes, scams',
    'Corruption remains a major issue. Sand mining, liquor sale, government contracts - all areas of concern. Need transparency.',
    'Governance',
    'Critical',
    'Zero tolerance for corruption. Lokayukta with teeth. Transparent governance. Online services to reduce human interface.',
    'Top',
    ARRAY['ALL'],
    ARRAY['All'],
    ARRAY['corruption', 'bribe', 'scam', 'fraud', 'transparency', 'ஊழல்', 'லஞ்சம்'],
    ARRAY['#CorruptionFree', '#TransparentGov', '#CleanTN', '#ஊழல்ஒழிப்பு'],
    ARRAY[
        'Strong Lokayukta Act',
        'Fast-track corruption cases',
        'Online government services',
        'Whistleblower protection',
        'Asset declaration mandatory'
    ],
    'Mixed - Some actions but perceptions remain',
    'High',
    TRUE
),

-- LAW & ORDER
(
    'LAW_ORDER',
    'Law & Order',
    'சட்டம் ஒழுங்கு',
    'Crime rate, police efficiency, public safety',
    'Crime rate concerns in urban areas. Drug menace. Need better policing and faster justice.',
    'Governance',
    'High',
    'Strengthen police force. Fast-track courts. Strict action against drug trafficking. Community policing.',
    'High',
    ARRAY['GEO_URBAN', 'GEO_CHENNAI', 'GEN_FEMALE', 'INC_MIDDLE', 'INC_HIGH'],
    ARRAY['Urban', 'All'],
    ARRAY['law and order', 'crime', 'police', 'safety', 'drugs', 'சட்டம்', 'குற்றம்'],
    ARRAY['#SafeTN', '#LawAndOrder', '#StopCrime'],
    ARRAY[
        'More police stations and personnel',
        'Fast-track courts',
        'CCTV in all public areas',
        'Zero tolerance for drugs',
        'Better street lighting'
    ],
    'Generally stable but room for improvement',
    'Medium',
    FALSE
),

-- GOOD GOVERNANCE
(
    'GOVERNANCE',
    'Good Governance',
    'நல்லாட்சி',
    'Efficient administration, citizen services, transparency',
    'Government processes are slow and opaque. Need citizen-centric governance with accountability.',
    'Governance',
    'High',
    'Digital governance. All services online. Time-bound delivery. Citizen feedback system.',
    'Medium',
    ARRAY['ALL'],
    ARRAY['All'],
    ARRAY['governance', 'administration', 'bureaucracy', 'services', 'நல்லாட்சி'],
    ARRAY['#GoodGovernance', '#DigitalTN', '#EfficientGov'],
    ARRAY[
        'All services online within 1 year',
        'Time-bound service delivery',
        'Grievance redressal within 30 days',
        'Transparent decision-making'
    ],
    'Some progress with e-governance',
    'Low',
    FALSE
);

-- =====================================================
-- 6. INSERT ISSUES - CULTURAL/REGIONAL CATEGORY
-- =====================================================

INSERT INTO issue_categories (
    code, name, name_tamil, description, detailed_description, category,
    priority_level, tvk_stance, tvk_priority, relevant_segments,
    geographic_focus, keywords, hashtags, messaging_points,
    incumbent_performance, media_coverage_level, is_hot_topic
) VALUES

-- TAMIL LANGUAGE
(
    'TAMIL',
    'Tamil Language & Culture',
    'தமிழ் மொழி மற்றும் பண்பாடு',
    'Protection of Tamil, opposition to Hindi imposition',
    'Emotional issue in TN. Strong opposition to Hindi imposition. Pride in Tamil heritage and culture.',
    'Cultural',
    'Critical',
    'Tamil will be the language of administration. No Hindi imposition. Protect and promote Tamil culture and heritage.',
    'Top',
    ARRAY['ALL'],
    ARRAY['All'],
    ARRAY['tamil', 'language', 'culture', 'hindi imposition', 'heritage', 'தமிழ்', 'மொழி'],
    ARRAY['#TamilPride', '#NoHindiImposition', '#SaveTamil', '#தமிழ்மொழி'],
    ARRAY[
        'Tamil as medium of instruction',
        'Oppose Hindi imposition',
        'Promote Tamil literature and arts',
        'Protect Tamil heritage sites',
        'Tamil mandatory in all signboards'
    ],
    'Strong stance, well-received',
    'High',
    TRUE
),

-- CAUVERY WATER DISPUTE
(
    'CAUVERY',
    'Cauvery Water Dispute',
    'காவிரி நீர் பிரச்சனை',
    'Water sharing dispute with Karnataka',
    'Long-standing issue. Karnataka not releasing TN share. Affects delta farmers. Emotional and livelihood issue.',
    'Regional',
    'Critical',
    'Ensure TN gets full Cauvery share as per tribunal orders. Legal and political pressure on Karnataka.',
    'Top',
    ARRAY['OCC_FARMERS', 'GEO_SOUTH_TN', 'GEO_RURAL'],
    ARRAY['South TN', 'Cauvery Delta'],
    ARRAY['cauvery', 'water dispute', 'Karnataka', 'water share', 'காவிரி', 'நீர்பங்கீடு'],
    ARRAY['#CauveryForTN', '#TNFarmersRight', '#காவிரிநீர்'],
    ARRAY[
        'Full implementation of tribunal orders',
        'Legal action against Karnataka',
        'Central government intervention',
        'Alternative water sources for delta'
    ],
    'Fighting legally but slow progress',
    'Very High',
    TRUE
),

-- LIQUOR POLICY
(
    'LIQUOR',
    'Liquor Policy & Prohibition',
    'மது கொள்கை',
    'TASMAC shops, prohibition demand, de-addiction',
    'Controversial issue. Some demand total prohibition. Others focus on regulation and revenue. Health and social impact.',
    'Social',
    'High',
    'Phased prohibition. Reduce TASMAC shops. Focus on de-addiction centers. Ban arrack and cheap liquor.',
    'Medium',
    ARRAY['GEN_FEMALE', 'GEO_RURAL', 'REL_HINDU'],
    ARRAY['All', 'Rural'],
    ARRAY['liquor', 'TASMAC', 'prohibition', 'alcohol', 'de-addiction', 'மது', 'மதுவிலக்கு'],
    ARRAY['#TotalProhibition', '#CloseTASMAC', '#SaveFamilies', '#மதுவிலக்கு'],
    ARRAY[
        'Reduce TASMAC shops by 50%',
        'Ban cheap arrack and liquor',
        'De-addiction centers in all districts',
        'Phased total prohibition'
    ],
    'Maintains TASMAC for revenue, opposition angry',
    'Medium',
    FALSE
),

-- JALLIKATTU
(
    'JALLIKATTU',
    'Jallikattu & Cultural Rights',
    'ஜல்லிக்கட்டு',
    'Traditional bull-taming sport, cultural identity',
    'Mass protests in 2017. Symbol of Tamil cultural identity. Legalized after sustained protests.',
    'Cultural',
    'Medium',
    'Full support for Jallikattu and traditional sports. Protect cultural practices.',
    'Low',
    ARRAY['GEO_SOUTH_TN', 'GEO_RURAL', 'SOC_THEVAR'],
    ARRAY['South TN', 'Rural'],
    ARRAY['jallikattu', 'bull taming', 'culture', 'tradition', 'ஜல்லிக்கட்டு'],
    ARRAY['#Jallikattu', '#TamilCulture', '#ஜல்லிக்கட்டு'],
    ARRAY[
        'Support and promote Jallikattu',
        'Protect traditional sports',
        'Cultural festivals funding'
    ],
    'Supportive, issue largely resolved',
    'Low',
    FALSE
);

-- =====================================================
-- 7. INSERT ISSUES - ENVIRONMENTAL CATEGORY
-- =====================================================

INSERT INTO issue_categories (
    code, name, name_tamil, description, detailed_description, category,
    priority_level, tvk_stance, tvk_priority, relevant_segments,
    geographic_focus, keywords, hashtags, messaging_points,
    incumbent_performance, media_coverage_level, is_hot_topic
) VALUES

-- POLLUTION
(
    'POLLUTION',
    'Environment & Pollution',
    'சுற்றுச்சூழல் மாசு',
    'Air, water pollution, waste management',
    'Chennai air quality poor. Industrial pollution. Plastic waste problem. Need environmental protection.',
    'Environmental',
    'Medium',
    'Strict pollution controls. Promote electric vehicles. Waste segregation. Green spaces in cities.',
    'Medium',
    ARRAY['GEO_URBAN', 'GEO_CHENNAI', 'INC_MIDDLE', 'INC_HIGH'],
    ARRAY['Urban', 'Chennai'],
    ARRAY['pollution', 'environment', 'air quality', 'waste', 'மாசு', 'சுற்றுச்சூழல்'],
    ARRAY['#CleanTN', '#GreenTN', '#StopPollution'],
    ARRAY[
        'Strict pollution norms for industries',
        'Promote electric vehicles',
        'Waste segregation mandatory',
        'More parks and green spaces'
    ],
    'Some initiatives but needs more focus',
    'Low',
    FALSE
),

-- COASTAL ISSUES
(
    'COASTAL',
    'Coastal & Fisheries',
    'கடலோர மற்றும் மீன்வளம்',
    'Fishermen welfare, sea erosion, port development',
    'Coastal erosion threat. Fishermen face livelihood challenges. Need port modernization and fisheries support.',
    'Economic',
    'Medium',
    'Coastal protection measures. Support fishermen with insurance and subsidies. Modern fishing harbors.',
    'Medium',
    ARRAY['GEO_COASTAL', 'OCC_FISHERMEN'],
    ARRAY['Coastal'],
    ARRAY['coast', 'fishermen', 'sea erosion', 'port', 'கடலோரம்', 'மீன்வளம்'],
    ARRAY['#TNCoast', '#FishermenRights', '#SaveCoast'],
    ARRAY[
        'Coastal protection from erosion',
        'Modern fishing harbors',
        'Insurance for fishermen',
        'Subsidy for fishing equipment'
    ],
    'Some support but coastal erosion continues',
    'Low',
    FALSE
);

-- =====================================================
-- 8. CREATE VIEWS
-- =====================================================

-- View for TVK top priority issues
CREATE OR REPLACE VIEW tvk_top_issues AS
SELECT
    code,
    name,
    name_tamil,
    category,
    tvk_priority,
    tvk_stance,
    relevant_segments,
    messaging_points,
    is_hot_topic
FROM issue_categories
WHERE tvk_priority IN ('Top', 'High')
AND is_active = TRUE
ORDER BY
    CASE tvk_priority
        WHEN 'Top' THEN 1
        WHEN 'High' THEN 2
    END,
    CASE priority_level
        WHEN 'Critical' THEN 1
        WHEN 'High' THEN 2
    END;

-- View for hot topics
CREATE OR REPLACE VIEW current_hot_topics AS
SELECT
    code,
    name,
    name_tamil,
    category,
    priority_level,
    keywords,
    hashtags,
    media_coverage_level
FROM issue_categories
WHERE is_hot_topic = TRUE
AND is_active = TRUE
ORDER BY
    CASE media_coverage_level
        WHEN 'Very High' THEN 1
        WHEN 'High' THEN 2
        WHEN 'Medium' THEN 3
    END;

-- View for issue distribution by category
CREATE OR REPLACE VIEW issue_distribution AS
SELECT
    category,
    COUNT(*) as issue_count,
    COUNT(CASE WHEN tvk_priority = 'Top' THEN 1 END) as top_priority,
    COUNT(CASE WHEN is_hot_topic = TRUE THEN 1 END) as hot_topics
FROM issue_categories
WHERE is_active = TRUE
GROUP BY category
ORDER BY issue_count DESC;

-- =====================================================
-- 9. TRIGGERS
-- =====================================================

CREATE OR REPLACE FUNCTION update_issue_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_issue_categories_timestamp
    BEFORE UPDATE ON issue_categories
    FOR EACH ROW
    EXECUTE FUNCTION update_issue_updated_at();

-- =====================================================
-- 10. ROW LEVEL SECURITY
-- =====================================================

ALTER TABLE issue_categories ENABLE ROW LEVEL SECURITY;

CREATE POLICY issue_categories_select_policy ON issue_categories
    FOR SELECT
    USING (auth.role() = 'authenticated');

CREATE POLICY issue_categories_admin_policy ON issue_categories
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid()
            AND role IN ('admin', 'super_admin')
        )
    );

-- =====================================================
-- 11. HELPER FUNCTIONS
-- =====================================================

-- Get issues by priority
CREATE OR REPLACE FUNCTION get_issues_by_priority(p_priority TEXT)
RETURNS TABLE (
    code TEXT,
    name TEXT,
    tamil_name TEXT,
    stance TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        issue_categories.code,
        issue_categories.name,
        issue_categories.name_tamil,
        issue_categories.tvk_stance
    FROM issue_categories
    WHERE issue_categories.tvk_priority = p_priority
    AND issue_categories.is_active = TRUE
    ORDER BY
        CASE priority_level
            WHEN 'Critical' THEN 1
            WHEN 'High' THEN 2
            WHEN 'Medium' THEN 3
        END;
END;
$$ LANGUAGE plpgsql;

-- Get issues by segment
CREATE OR REPLACE FUNCTION get_issues_for_segment(p_segment_code TEXT)
RETURNS TABLE (
    issue_code TEXT,
    issue_name TEXT,
    issue_tamil TEXT,
    priority TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        code,
        name,
        name_tamil,
        tvk_priority
    FROM issue_categories
    WHERE p_segment_code = ANY(relevant_segments)
    AND is_active = TRUE
    ORDER BY
        CASE tvk_priority
            WHEN 'Top' THEN 1
            WHEN 'High' THEN 2
            WHEN 'Medium' THEN 3
        END;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 12. COMMENTS
-- =====================================================

COMMENT ON TABLE issue_categories IS 'Key political issues for Tamil Nadu elections and TVK campaign';
COMMENT ON COLUMN issue_categories.tvk_stance IS 'TVK party''s official position on this issue';
COMMENT ON COLUMN issue_categories.tvk_priority IS 'Priority level for TVK campaign focus';
COMMENT ON COLUMN issue_categories.messaging_points IS 'Key talking points for TVK candidates and campaigners';

-- =====================================================
-- 13. VALIDATION QUERIES
-- =====================================================

-- Check total issues
-- SELECT COUNT(*) FROM issue_categories;

-- Check TVK top priority issues
-- SELECT * FROM tvk_top_issues;

-- Check hot topics
-- SELECT * FROM current_hot_topics;

-- Check issue distribution
-- SELECT * FROM issue_distribution;

-- Check issues by category
-- SELECT category, COUNT(*) as count
-- FROM issue_categories
-- WHERE is_active = TRUE
-- GROUP BY category
-- ORDER BY count DESC;

-- =====================================================
-- END OF MIGRATION
-- =====================================================
