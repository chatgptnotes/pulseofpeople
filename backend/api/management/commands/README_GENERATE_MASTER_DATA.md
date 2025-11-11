# Generate Master Data Command

## Overview

The `generate_master_data` Django management command creates comprehensive master data for the Pulse of People platform. It generates realistic Tamil Nadu geographic and political data including states, districts, constituencies, polling booths, political parties, issue categories, voter segments, and organization setup.

## Usage

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Generate all master data
python manage.py generate_master_data

# Clear existing data and regenerate
python manage.py generate_master_data --clear

# Show help
python manage.py generate_master_data --help
```

## What Gets Generated

### Phase 1: Geographic Data

#### 1. States (2)
- **Tamil Nadu**: 38 districts, 234 assembly constituencies
- **Puducherry**: 4 districts, 30 assembly constituencies

#### 2. Districts (42)
**Tamil Nadu (38 districts):**
- Chennai, Coimbatore, Madurai, Salem, Tiruchirappalli, Tirunelveli
- Erode, Vellore, Kanyakumari, Thanjavur, Dindigul, Tiruppur
- Virudhunagar, Namakkal, Cuddalore, Karur, Dharmapuri, Krishnagiri
- Nagapattinam, Pudukkottai, Ramanathapuram, Sivaganga, Theni
- Thoothukudi, Tiruvannamalai, Viluppuram, Ariyalur, Kanchipuram
- Kallakurichi, Mayiladuthurai, Perambalur, Ranipet, Tirupathur
- Tiruvarur, Tiruvallur, Nilgiris, Chengalpattu, Tenkasi

Each district includes:
- District code (TN01-TN38)
- Headquarters location
- Population estimates
- Area in square kilometers

**Puducherry (4 districts):**
- Puducherry, Karaikal, Mahe, Yanam

#### 3. Constituencies (234)
All 234 real Tamil Nadu Assembly constituencies with:
- Constituency number (1-234)
- District mapping
- Reservation status (General/SC/ST)
- Geographic center coordinates (latitude/longitude)
- Constituency type (assembly/parliamentary)
- Approximate voter count

**Major Constituency Groups:**
- Chennai: 18 constituencies (Gummidipoondi, Ponneri, Tiruvottiyur, Anna Nagar, T. Nagar, Mylapore, etc.)
- Coimbatore: 10 constituencies
- Madurai: 8 constituencies
- Salem: 8 constituencies
- Tiruchirappalli: 7 constituencies
- And more...

#### 4. Polling Booths (10,000+)
Realistic polling booth data distributed across constituencies:
- **Booth Distribution:**
  - Urban constituencies (Chennai, Coimbatore, Madurai, Salem): 60-100 booths each
  - Other constituencies: 30-50 booths each

**Each booth includes:**
- Unique booth number (001, 002, 003, etc.)
- Building name (schools, community halls, government offices)
- GPS coordinates (latitude/longitude) within constituency boundaries
- Area/zone information
- Voter demographics:
  - Total voters (600-1200 per booth)
  - Male voters
  - Female voters
- Accessibility status (75% wheelchair accessible)

**Building name templates used:**
- Government Higher Secondary School
- Corporation Primary School
- Government Elementary School
- Municipal High School
- Government Girls High School
- Panchayat Union Primary School
- Community Hall
- Village Panchayat Office

### Phase 2: Political Data

#### 5. Political Parties (10)

1. **TVK (Tamilaga Vettri Kazhagam)**
   - Symbol: Elephant
   - Founded: 2024-02-02
   - Ideology: Secular Social Justice, Tamil Nationalism
   - Status: State party
   - Description: Founded by actor Vijay, focuses on secular social justice, anti-casteism, education reform, and Tamil cultural pride

2. **DMK (Dravida Munnetra Kazhagam)**
   - Symbol: Rising Sun
   - Founded: 1949-09-17
   - Ideology: Dravidian, Social Democracy, Secularism
   - Status: State party
   - Currently ruling Tamil Nadu

3. **AIADMK**
   - Symbol: Two Leaves
   - Founded: 1972-10-17
   - Ideology: Dravidian, Social Conservatism
   - Status: State party

4. **BJP (Bharatiya Janata Party)**
   - Symbol: Lotus
   - Status: National party
   - Ideology: Hindu Nationalism, Right-wing

5. **INC (Indian National Congress)**
   - Symbol: Hand
   - Status: National party
   - Founded: 1885-12-28

6. **PMK (Pattali Makkal Katchi)**
   - Symbol: Mango
   - Status: State party
   - Focus: Vanniyar community representation

7. **MDMK (Marumalarchi Dravida Munnetra Kazhagam)**
   - Symbol: Spinning Top
   - Status: State party
   - Led by Vaiko

8. **DMDK**
   - Symbol: Murasu (Drum)
   - Founded by actor Vijayakanth

9. **CPI(M)**
   - Symbol: Hammer and Sickle
   - Status: National party

10. **NTK (Naam Tamilar Katchi)**
    - Symbol: Battery Torch
    - Led by Seeman

#### 6. Issue Categories (25+)

All issues include TVK stance, priority level, keywords, hashtags, and severity ratings.

**Critical Priority (9-10):**
1. **Jobs & Employment**
   - TVK Stance: Strongly Supportive
   - Keywords: unemployment, jobs, youth employment, IT sector, skill development
   - Hashtags: #JobsForYouth, #TNJobs, #SkillTN

2. **Water Supply & Management**
   - TVK Stance: Strongly Supportive
   - Keywords: water, cauvery, drought, drinking water, irrigation
   - Hashtags: #WaterForTN, #CauveryRights, #SaveWater

3. **NEET Opposition**
   - TVK Stance: Strongly Against NEET
   - Keywords: NEET, medical admission, student deaths, education rights
   - Hashtags: #NoToNEET, #BanNEET, #TNAgainstNEET

4. **Cauvery Water Dispute**
   - TVK Stance: Strongly Supportive of TN Rights
   - Keywords: Cauvery, water dispute, Karnataka, farmer water
   - Hashtags: #CauveryForTN, #TNWaterRights

**High Priority (7-8):**
5. Healthcare Access
6. Education Quality
7. Caste Discrimination
8. Women Safety & Empowerment
9. Farmers Welfare
10. Fishermen Rights
11. Tamil Language Rights
12. Law & Order
13. Corruption

**Medium Priority (5-6):**
14. Small Business Support
15. Road Infrastructure
16. Public Transport
17. Electricity & Power
18. Air Pollution
19. Waste Management
20. Coastal Erosion
21. Cultural Heritage
22. Affordable Housing
23. Urban Planning
24. TASMAC & Liquor Policy
25. Sand Mining

#### 7. Voter Segments (50+)

**Occupational Segments:**
- Fishermen Community (500K, Priority 9)
- Farmers (10M, Priority 9)
- IT Workers (1.5M, Priority 7)
- Daily Wage Workers (8M, Priority 8)
- Small Business Owners (3M, Priority 7)
- Government Employees (2M, Priority 6)
- Auto & Taxi Drivers (800K, Priority 6)
- Weavers (300K, Priority 7)
- Street Vendors (1.2M, Priority 6)
- Healthcare Workers (500K, Priority 6)
- Teachers & Educators (800K, Priority 7)
- Industrial Workers (4M, Priority 7)

**Age-based Segments:**
- Youth (18-25): 8M voters, Priority 10
- Young Professionals (26-35): 10M, Priority 8
- Middle-aged (36-50): 15M, Priority 7
- Senior Citizens (60+): 7M, Priority 6

**Gender-based Segments:**
- Women: 35M, Priority 9
- Working Women: 12M, Priority 8
- Homemakers: 15M, Priority 7

**Education-based Segments:**
- College Students: 4M, Priority 9
- School Students (18+): 2M, Priority 8
- Graduates: 8M, Priority 7
- Illiterate Voters: 5M, Priority 7

**Social Category Segments:**
- SC Communities: 10M, Priority 9
- ST Communities: 800K, Priority 9
- OBC Communities: 20M, Priority 8
- Forward Caste: 10M, Priority 6
- Minorities: 6M, Priority 7

**Urban/Rural Segments:**
- Urban Middle Class: 12M, Priority 7
- Rural Voters: 30M, Priority 8
- Slum Dwellers: 5M, Priority 8

**Economic Segments:**
- Below Poverty Line: 10M, Priority 9
- Middle Income: 20M, Priority 7
- Upper Middle Class: 3M, Priority 5

**Regional Segments:**
- Coastal Communities: 8M, Priority 8
- Hill Area Residents: 1M, Priority 6
- Delta Region Farmers: 5M, Priority 9
- Western Belt Workers: 6M, Priority 7

**Political Segments:**
- First-time Voters: 3M, Priority 10
- Swing Voters: 8M, Priority 9
- Party Loyalists: 15M, Priority 6

### Phase 3: Organization Setup

#### 8. TVK Organization (1)
- Name: Tamilaga Vettri Kazhagam
- Type: Political Party
- Subscription: Enterprise plan (10,000 max users)
- Social Media: Twitter, Facebook, Instagram, YouTube
- Brand Colors: #FF6B00 (primary), #FFD700 (secondary)
- Features enabled: Analytics, Maps, Bulk Upload

## Data Characteristics

### Realistic Data Features

1. **Geographic Accuracy:**
   - Real district names and headquarters
   - Accurate population estimates based on 2021 census data
   - Actual area measurements in square kilometers
   - GPS coordinates within Tamil Nadu boundaries (8.0-13.5°N, 76.5-80.5°E)

2. **Political Realism:**
   - All 234 real Tamil Nadu assembly constituency names
   - Correct reservation status (General/SC/ST)
   - Proper district-constituency mapping
   - Realistic voter distribution (150K-350K per constituency)

3. **Booth Distribution:**
   - Higher booth density in urban areas
   - Realistic voter counts (600-1200 per booth)
   - Gender distribution in voter demographics
   - 75% accessibility compliance

4. **Issue Categories:**
   - Based on real Tamil Nadu political issues
   - TVK's actual political stance
   - Real hashtags and keywords used in campaigns
   - Priority levels matching ground reality

5. **Voter Segments:**
   - Population estimates based on demographic data
   - Occupational distribution matching TN economy
   - Social category representation
   - Age and gender distributions

## Performance

- Uses Django's `bulk_create` for efficient database operations
- Transaction management ensures data integrity
- Progress indicators show generation status
- Typical execution time: 2-5 minutes for full dataset

## Database Impact

**Approximate record counts:**
- States: 2
- Districts: 42
- Constituencies: 234
- Polling Booths: ~10,000
- Political Parties: 10
- Issue Categories: 25
- Voter Segments: 50
- Organizations: 1

**Total: ~10,364 records**

## Options

### --clear Flag
Clears all existing master data before generation:
- Deletes all polling booths
- Deletes all constituencies
- Deletes all districts
- Deletes all states
- Deletes all issue categories
- Deletes all voter segments
- Deletes all political parties
- Deletes TVK organization

**Warning:** Use with caution in production environments!

```bash
python manage.py generate_master_data --clear
```

## Error Handling

The command includes comprehensive error handling:
- Transaction rollback on any failure
- Foreign key validation
- Duplicate prevention (get_or_create pattern)
- District existence validation before constituency creation
- Full stack traces with --traceback option

## Output Format

```
================================================================================
PULSE OF PEOPLE - MASTER DATA GENERATION
================================================================================

[PHASE 1] Geographic Data
--------------------------------------------------------------------------------
Creating States...
  [Created] Tamil Nadu
  [Created] Puducherry
Creating Districts...
  [Created] TN: Ariyalur (Pop: 754,894)
  [Created] TN: Chengalpattu (Pop: 2,556,244)
  ...
Creating Constituencies...
  [20/234] Created: Kavundampalayam
  [40/234] Created: Madurai Central
  ...
  [Complete] Created 234 constituencies
Creating Polling Booths...
  [Complete] Created 10,234 polling booths

[PHASE 2] Political Data
--------------------------------------------------------------------------------
Creating Political Parties...
  [Created] TVK - Tamilaga Vettri Kazhagam
  [Created] DMK - Dravida Munnetra Kazhagam
  ...
Creating Issue Categories...
  [Created] Jobs & Employment (Priority: 10)
  [Created] Water Supply & Management (Priority: 10)
  ...
Creating Voter Segments...
  [10/50] Created: IT Workers
  [20/50] Created: College Students
  ...
  [Complete] Created 50 voter segments

[PHASE 3] Organization Setup
--------------------------------------------------------------------------------
Creating TVK Organization...
  [Created] Tamilaga Vettri Kazhagam

================================================================================
DATA GENERATION COMPLETE
================================================================================

  States:                   2
  Districts:               42
  Constituencies:         234
  Polling Booths:      10,234
  Political Parties:       10
  Issue Categories:        25
  Voter Segments:          50
  Organizations:            1

================================================================================
Run: python manage.py generate_master_data --clear
     to regenerate all data from scratch
================================================================================
```

## Use Cases

1. **Development Setup:**
   - Quickly populate database with realistic test data
   - Test geographic hierarchy (State → District → Constituency → Booth)
   - Validate data relationships and foreign keys

2. **Testing:**
   - Test API endpoints with comprehensive data
   - Validate map visualizations with GPS coordinates
   - Test data filtering and search functionality

3. **Demo/Presentation:**
   - Show realistic Tamil Nadu political data
   - Demonstrate platform capabilities
   - Present to stakeholders with actual constituency names

4. **Production Initial Setup:**
   - Populate master tables before going live
   - Establish base data for user assignments
   - Set up organization structure

## Dependencies

Required Python packages (already in requirements.txt):
- Django 5.2+
- faker (for realistic data generation)

## Integration with Other Commands

This command complements other seed commands:
- Run this BEFORE: `seed_voters.py` (needs constituencies and booths)
- Run this BEFORE: `seed_feedback.py` (needs issue categories and segments)
- Run this BEFORE: `seed_field_reports.py` (needs geographic data)
- Run this AFTER: `seed_permissions.py` (independent of master data)

## Recommended Workflow

```bash
# 1. Clear and regenerate master data
python manage.py generate_master_data --clear

# 2. Create permissions
python manage.py seed_permissions

# 3. Create users
python manage.py createsuperadmin

# 4. Seed additional data
python manage.py seed_voters
python manage.py seed_campaigns
python manage.py seed_events
```

## Troubleshooting

### Command Not Found
```bash
# Make sure you're in the backend directory
cd backend

# Activate virtual environment
source venv/bin/activate
```

### ModuleNotFoundError: faker
```bash
# Install faker
pip install faker==33.1.0
```

### Database Errors
```bash
# Run migrations first
python manage.py migrate

# Check database connection in settings.py
```

### Transaction Errors
```bash
# Use --traceback for detailed error information
python manage.py generate_master_data --traceback
```

## Future Enhancements

Potential improvements:
1. Add Ward model and generate 1000+ wards
2. Import actual constituency boundary GeoJSON data
3. Add parliamentary constituency data
4. Generate booth-level historical voting data
5. Add Tamil translations for all names
6. Import real booth addresses from Election Commission data
7. Add booth photos/images
8. Generate booth agent assignments

## Contributing

To extend this command:
1. Add new data models to `api/models.py`
2. Create corresponding `create_*` methods
3. Add to transaction block in `handle()` method
4. Update statistics tracking
5. Update this documentation

## License

Part of the Pulse of People platform.
Copyright © 2024 TVK. All rights reserved.

## Support

For issues or questions:
- GitHub Issues: [pulseofpeople/issues]
- Email: dev@tvk.org
- Documentation: See CLAUDE.md for project overview
