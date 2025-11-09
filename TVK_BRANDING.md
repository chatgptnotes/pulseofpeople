# TVK Platform Branding Guide

## Overview

This platform is specifically built for **Tamilaga Vettri Kazhagam (TVK)**, a political party founded by Vijay in Tamil Nadu.

---

## Organization Details

### Basic Information
- **Full Name**: Tamilaga Vettri Kazhagam
- **Short Name**: TVK
- **Founder**: Vijay
- **Established**: 2023
- **Headquarters**: Chennai, Tamil Nadu
- **State**: Tamil Nadu
- **Party Symbol**: Rising Sun

### Political Positioning
- **Ideology**: Social Democracy
- **Alliance**: Independent
- **Target Audience**: Youth, Social Justice advocates, Tamil Nadu voters

---

## Branding Assets

### Logo
- **File**: `/TVKAsset1_1024x1024.webp`
- **Size**: 1024x1024 pixels
- **Format**: WebP (optimized for web)

### Color Scheme
- **Primary Color**: `#FFD700` (Gold) - Represents prosperity and victory
- **Secondary Color**: `#FF0000` (Red) - Represents courage and sacrifice
- **Accent Color**: `#1976D2` (Blue) - Represents trust and stability

### Tagline
- **Tamil**: வெற்றிக் கொடி பறக்குது
- **English**: The Victory Flag Flies

---

## Contact Information

### Official Channels
- **Website**: https://www.tvk.org.in
- **Email**: contact@tvk.org.in
- **Phone**: +91-44-XXXXXXXX

### Social Media
- **Twitter**: [@TVKOfficial](https://twitter.com/TVKOfficial)
- **Facebook**: [TVKOfficial](https://facebook.com/TVKOfficial)
- **Instagram**: [@tvk_official](https://instagram.com/tvk_official)
- **YouTube**: [TVK Official](https://youtube.com/@TVKOfficial)

---

## Focus Areas

TVK's political agenda centers on:

1. **Youth Empowerment**
   - Job creation for youth
   - Skill development programs
   - Entrepreneurship support

2. **Social Justice**
   - Equality for all communities
   - Representation for marginalized groups
   - Anti-discrimination policies

3. **Economic Development**
   - Tamil Nadu's industrial growth
   - Support for MSMEs
   - Infrastructure development

4. **Education Reform**
   - Quality education access
   - Digital literacy programs
   - Vocational training

5. **Healthcare Access**
   - Universal healthcare
   - Rural health infrastructure
   - Preventive care programs

6. **Women Empowerment**
   - Safety and security
   - Economic independence
   - Political representation

7. **Agricultural Welfare**
   - Farmer support schemes
   - Modern farming techniques
   - Fair pricing mechanisms

8. **Environmental Protection**
   - Sustainable development
   - Green energy initiatives
   - Conservation programs

---

## Platform Configuration

### Organization ID
```
11111111-1111-1111-1111-111111111111
```

All TVK voter data, constituencies, and polling booths are linked to this organization ID.

### Branding Configuration File
**Location**: `frontend/src/config/tvk-branding.ts`

```typescript
import TVK_CONFIG from '@/config/tvk-branding';

// Access organization details
const orgName = TVK_CONFIG.organization.name; // "Tamilaga Vettri Kazhagam"
const primaryColor = TVK_CONFIG.branding.primaryColor; // "#FFD700"
const logo = TVK_CONFIG.branding.logoPath; // "/TVKAsset1_1024x1024.webp"
```

---

## Database Configuration

### Organizations Table
The TVK organization record in the database:

```sql
SELECT * FROM organizations WHERE id = '11111111-1111-1111-1111-111111111111';
```

**Fields**:
- `name`: "Tamilaga Vettri Kazhagam"
- `slug`: "tvk"
- `type`: "political_party"
- `logo_url`: "/TVKAsset1_1024x1024.webp"
- `website`: "https://www.tvk.org.in"
- `subscription_status`: "active"

### Settings (JSONB)
```json
{
  "party_color": "#FFD700",
  "party_symbol": "Rising Sun",
  "established_year": 2023,
  "headquarters": "Chennai, Tamil Nadu",
  "social_media": {
    "twitter": "@TVKOfficial",
    "facebook": "TVKOfficial",
    "instagram": "@tvk_official"
  }
}
```

### Metadata (JSONB)
```json
{
  "party_full_name": "Tamilaga Vettri Kazhagam",
  "party_short_name": "TVK",
  "founder": "Vijay",
  "ideology": "Social Democracy",
  "alliance": "Independent",
  "state": "Tamil Nadu",
  "focus_areas": [
    "Youth Empowerment",
    "Social Justice",
    "Economic Development",
    "Education Reform",
    "Healthcare Access"
  ]
}
```

---

## Voter Database

### Current Statistics
- **Total Voters**: 55,000
- **Coverage**: Tamil Nadu
- **Constituencies**: 5 (Chennai North, Chennai Central, Chennai South, Coimbatore, Madurai)
- **Polling Booths**: 10 (all with GPS coordinates)

### Voter Demographics
- Realistic Tamil names
- Age distribution: 18-80 years
- Gender distribution: Male, Female, Other
- Religion: Hindu, Muslim, Christian, Sikh, others (Tamil Nadu distribution)
- Caste categories: General, OBC, SC, ST (Tamil Nadu distribution)
- Occupation: 20 realistic occupations common in Tamil Nadu

### Political Sentiment Tracking
- **Categories**: Strong Support, Support, Neutral, Oppose, Strong Oppose, Undecided
- **Sentiment Scores**: -100 to +100
- **Voter Types**: Core Supporter, Swing Voter, Opponent

---

## Competitor Organizations

For analysis and benchmarking, the platform includes data for:

### DMK (Dravida Munnetra Kazhagam)
- **Organization ID**: `22222222-2222-2222-2222-222222222222`
- **Purpose**: Competitor analysis

### AIADMK (All India Anna Dravida Munnetra Kazhagam)
- **Organization ID**: `33333333-3333-3333-3333-333333333333`
- **Purpose**: Competitor analysis

---

## Platform Features for TVK

### Enabled Features
- ✅ Voter Management
- ✅ Sentiment Tracking
- ✅ Booth Analysis
- ✅ Constituency Mapping
- ✅ Survey Management
- ✅ Campaign Planning
- ✅ Volunteer Management

### Coming Soon
- ⏳ Donation Tracking
- ⏳ Event Management
- ⏳ Broadcast Messaging

---

## Customization Guide

### Updating Organization Details

**Database Update**:
```sql
UPDATE organizations
SET
    name = 'New Name',
    website = 'https://newwebsite.com',
    settings = jsonb_set(settings, '{party_color}', '"#NewColor"')
WHERE id = '11111111-1111-1111-1111-111111111111';
```

**Frontend Config Update**:
Edit `frontend/src/config/tvk-branding.ts`:
```typescript
export const TVK_CONFIG = {
  organization: {
    name: 'Updated Name',
    // ... other fields
  },
  branding: {
    primaryColor: '#NewColor',
    // ... other fields
  }
};
```

### Adding New Logo
1. Place logo file in `/public/` directory
2. Update database:
   ```sql
   UPDATE organizations
   SET logo_url = '/new-logo.webp'
   WHERE id = '11111111-1111-1111-1111-111111111111';
   ```
3. Update config file:
   ```typescript
   branding: {
     logoPath: '/new-logo.webp'
   }
   ```

---

## Migration History

### 2025-11-09: TVK Branding Update
- Updated primary organization from placeholder to TVK
- Added TVK-specific metadata and settings
- Updated competitor organizations (DMK, AIADMK)
- Created branding configuration file
- Updated all documentation

**Migration File**: `supabase/migrations/20251109_update_to_tvk.sql`

---

## Support & Contact

For platform-related support:
- **Technical Issues**: Create issue on GitHub
- **Feature Requests**: Contact development team
- **TVK Organization Queries**: contact@tvk.org.in

---

**Last Updated**: 2025-11-09
**Platform Version**: 2.0
**Organization**: Tamilaga Vettri Kazhagam (TVK)
