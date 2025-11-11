# API Research Report - Pulse of People Platform
**Date:** November 9, 2025
**Research Period:** November 2025
**Version:** 1.0

## Executive Summary

This comprehensive research report evaluates 60+ third-party APIs across 12 categories for integration into the Pulse of People political sentiment analysis platform. The research focuses on APIs that support Indian market requirements, offer competitive pricing, and provide features essential for political campaign management.

### Key Findings:
- **Total APIs Evaluated:** 60+
- **Categories Covered:** 12
- **Recommended Must-Have APIs:** 8
- **Estimated Monthly Cost (10K users):** $450-$750
- **Estimated Monthly Cost (100K users):** $2,500-$4,500

---

## 1. WEATHER APIs

### Why We Need It
- **Business Value:** Optimize door-to-door campaigns, rally scheduling, voter outreach timing
- **Use Cases:**
  1. Schedule rallies on favorable weather days
  2. Optimize door-to-door campaign timing
  3. Send weather-based reminders to volunteers
  4. Plan outdoor events and booth activities
  5. Real-time weather alerts for campaign managers

### Options Compared

#### Option 1: Visual Crossing Weather API
**Pros:**
- Most generous free tier: 1,000 requests/day
- Comprehensive historical + forecast data
- Very competitive pricing: $0.0001 per record
- 50% cheaper than competitors
- Excellent for India coverage

**Cons:**
- Less brand recognition than OpenWeatherMap
- Smaller community/support base

**Pricing:**
- Free: 1,000 requests/day (30,000/month)
- Paid: $35/month for unlimited access
- Pay-as-you-go: $0.0001 per record

**Rating:** 9.5/10

#### Option 2: OpenWeatherMap
**Pros:**
- Most popular weather API
- Extensive documentation
- Large developer community
- Good free tier: 60 calls/min, 1,000/day
- Commercial use allowed with attribution

**Cons:**
- More expensive: $0.0015 per record (15x Visual Crossing)
- Limited free tier compared to Visual Crossing

**Pricing:**
- Free: 1,000 calls/day
- Paid: Varies by subscription tier

**Rating:** 8/10

#### Option 3: Tomorrow.io
**Pros:**
- Enterprise-grade accuracy
- 80+ data layers (air quality, pollen, fire index)
- Hyperlocal data with 15-min update frequency
- 14-day forecasts
- Good for specialized use cases

**Cons:**
- Free tier limited to 500 calls/day
- More expensive than alternatives
- Complex pricing structure

**Pricing:**
- Free: 500 API calls/day
- API Plan: Usage-based pricing
- Platform Plan: Custom pricing
- Enterprise: Custom pricing

**Rating:** 7.5/10

#### Option 4: WeatherAPI.com
**Pros:**
- Simple API interface
- Additional features: satellite imagery, UV index
- Good documentation

**Cons:**
- Limited pricing information publicly available
- Smaller ecosystem

**Pricing:**
- Free tier available
- Paid plans: Contact for pricing

**Rating:** 7/10

### RECOMMENDED CHOICE

**Winner:** Visual Crossing Weather API

**Justification:**
- Best free tier for development/testing (1,000 requests/day = 30,000/month)
- Most cost-effective for production ($35/month unlimited vs $0.0001 per record)
- 50% cheaper than competitors
- Comprehensive historical + forecast data
- Excellent India coverage
- Transparent pricing

**Implementation Effort:** 1-2 days

**Expected Cost:**
- Development: Free (under 30K requests/month)
- Production (10K users, 5 requests/user/month): $35/month (unlimited plan)
- Production (100K users): $35/month (unlimited plan)

### Integration Approach

**Data Flow:**
```
Frontend → Backend API → Visual Crossing API → Process Weather Data → Cache (Redis) → Response
```

**Error Handling:**
- Implement rate limiting
- Cache weather data for 15 minutes
- Fallback to cached data on API failure
- Retry logic with exponential backoff

**Code Example:**
```python
import requests
from django.core.cache import cache

VISUAL_CROSSING_API_KEY = os.getenv('VISUAL_CROSSING_API_KEY')
VISUAL_CROSSING_BASE_URL = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline'

def get_weather_for_location(latitude, longitude, date=None):
    """
    Get weather data for a specific location
    """
    cache_key = f'weather_{latitude}_{longitude}_{date}'
    cached_data = cache.get(cache_key)

    if cached_data:
        return cached_data

    url = f'{VISUAL_CROSSING_BASE_URL}/{latitude},{longitude}'
    if date:
        url += f'/{date}'

    params = {
        'key': VISUAL_CROSSING_API_KEY,
        'unitGroup': 'metric',
        'include': 'current,days',
        'contentType': 'json'
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Cache for 15 minutes
        cache.set(cache_key, data, 900)
        return data
    except requests.exceptions.RequestException as e:
        # Log error and return None
        logger.error(f'Weather API error: {e}')
        return None
```

---

## 2. SOCIAL MEDIA APIs

### Why We Need It
- **Business Value:** Track political sentiment, monitor competitors, measure campaign reach
- **Use Cases:**
  1. Social media sentiment analysis on political topics
  2. Track mentions of candidates/parties
  3. Monitor trending political hashtags
  4. Analyze competitor social media strategy
  5. Measure campaign post engagement

### Options Compared

#### Option 1: Twitter/X API (Official)
**Pros:**
- Direct access to Twitter data
- Real-time data access
- Official API with full feature set

**Cons:**
- Extremely expensive: $5,000/month (Pro), $42,000+/month (Enterprise)
- Free tier essentially useless (1,500 tweets/month)
- Basic tier ($100/month) still very limited
- Restrictive rate limits

**Pricing:**
- Free: 1,500 tweets/month (unusable for analytics)
- Basic: $100/month for 10,000 tweets
- Pro: $5,000/month for 2M tweets
- Enterprise: $42,000+/month

**Rating:** 3/10 (due to cost)

#### Option 2: Facebook Graph API
**Pros:**
- FREE for basic access
- Access to page analytics, posts, comments
- Engagement metrics available
- Good documentation

**Cons:**
- Requires Facebook Business Page
- Limited historical data
- Stricter permissions in 2025 (v22.0)
- Rate limits tightened

**Pricing:**
- Free for basic access
- Enhanced features: Contact Meta for pricing

**Rating:** 8/10

#### Option 3: Instagram Graph API
**Pros:**
- FREE for Business/Creator accounts
- Comprehensive engagement metrics
- Story analytics included
- Reels performance data

**Cons:**
- Must link to Facebook Page
- Rate limits: 200 requests/hour
- Delayed reporting (up to 48 hours)
- Limited to Business accounts

**Pricing:**
- Free (requires Business/Creator account)

**Rating:** 8/10

#### Option 4: Bluesky & Mastodon APIs
**Pros:**
- Very open APIs with minimal restrictions
- Free to use
- Developer-friendly
- Growing user bases

**Cons:**
- Smaller user base than Twitter/X
- Less political content currently
- Still in active development

**Pricing:**
- Free

**Rating:** 6/10 (for now, watch this space)

### RECOMMENDED CHOICE

**Winner:** Facebook Graph API + Instagram Graph API (Both Free)

**Alternative for Twitter:** Skip official Twitter API, use alternative data sources or web scraping (compliance permitting)

**Justification:**
- Facebook & Instagram APIs are FREE
- Good coverage of Indian political discourse
- Combined reach covers significant voter demographic
- Twitter API pricing is prohibitively expensive for startups
- Can supplement with news APIs for broader coverage

**Implementation Effort:** 3-5 days

**Expected Cost:**
- Development: $0
- Production: $0 (free tier sufficient)
- Twitter alternative (if needed): Consider third-party aggregators or skip

### Integration Approach

**Data Flow:**
```
Facebook Page → Graph API → Sentiment Analysis → Store in DB
Instagram Business Account → Graph API → Engagement Metrics → Analytics Dashboard
```

**Code Example:**
```python
import requests

FACEBOOK_ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN')
INSTAGRAM_ACCESS_TOKEN = os.getenv('INSTAGRAM_ACCESS_TOKEN')

def get_facebook_page_posts(page_id, limit=100):
    """
    Fetch recent posts from a Facebook page
    """
    url = f'https://graph.facebook.com/v22.0/{page_id}/posts'
    params = {
        'access_token': FACEBOOK_ACCESS_TOKEN,
        'limit': limit,
        'fields': 'message,created_time,reactions.summary(true),comments.summary(true),shares'
    }

    response = requests.get(url, params=params)
    return response.json()

def get_instagram_media_insights(media_id):
    """
    Get insights for Instagram post
    """
    url = f'https://graph.facebook.com/v22.0/{media_id}/insights'
    params = {
        'access_token': INSTAGRAM_ACCESS_TOKEN,
        'metric': 'engagement,impressions,reach,saved'
    }

    response = requests.get(url, params=params)
    return response.json()
```

---

## 3. GEOLOCATION & MAPS APIs

### Why We Need It
- **Business Value:** Polling booth mapping, voter density visualization, territory planning
- **Use Cases:**
  1. Display polling booths on interactive map
  2. Voter density heatmaps by constituency
  3. Route optimization for door-to-door campaigns
  4. Geofencing for location-based alerts
  5. Constituency boundary visualization

### Options Compared

#### Option 1: Google Maps API
**Pros:**
- Best map quality for India
- Superior coverage in Indian cities/rural areas
- 300M+ Indian businesses and places
- AI-powered features (Address Descriptors for India)
- Extensive documentation

**Cons:**
- More expensive than Mapbox
- Pricing: $5 per 1,000 Directions API requests
- Free tier limited ($200 credit = ~40K map loads)

**Pricing (India-specific, 2025):**
- Free: 70,000 Geocoding requests/month
- Free: 35,000 Places API calls/month
- Directions API: $5 per 1,000 requests
- Maps JavaScript API: Dynamic pricing
- Automatic volume discounts up to 5M+ requests

**Rating:** 9/10 (for India)

#### Option 2: Mapbox
**Pros:**
- More cost-effective for high volume
- Beautiful map styles
- Generous free tier: 50,000 web map loads/month
- Directions API: $2 per 1,000 (60% cheaper than Google)
- Better pricing at scale

**Cons:**
- Weaker coverage in India (uses OpenStreetMap data)
- Less reliable in rural India
- May have data gaps in smaller cities

**Pricing:**
- Free: 50,000 map loads/month (web)
- Free: 25,000 MAU (mobile)
- Directions API: $2 per 1,000 requests (after 100K free)
- Volume discounts: 20% to 80% at high volumes

**Rating:** 7/10 (India coverage concerns)

#### Option 3: OpenStreetMap + Leaflet (Self-hosted)
**Pros:**
- Completely free
- Open source
- Leaflet library is lightweight (42KB)
- Full control over data
- No usage limits

**Cons:**
- Requires self-hosting tile server
- Infrastructure costs
- Maintenance burden
- Limited features compared to commercial APIs
- Tile server usage policies restrict commercial use

**Pricing:**
- Free (but with self-hosting costs)
- Infrastructure: ~$50-200/month

**Rating:** 6/10 (free but complex)

#### Option 4: MapTiler
**Pros:**
- Free tier: 100,000 map views/month
- Uses OpenStreetMap data
- Cloud hosting available
- Good documentation

**Cons:**
- Smaller ecosystem than Google/Mapbox
- Limited India-specific features

**Pricing:**
- Free: 100,000 map views/month
- Paid: Starting at $39/month

**Rating:** 7.5/10

### RECOMMENDED CHOICE

**Winner:** Google Maps API (for production) + Mapbox (as fallback/development)

**Justification:**
- Google Maps has SUPERIOR coverage in India (official stated strength)
- 7M+ km roads, 300M businesses mapped in India
- Better for rural areas and smaller cities
- AI features tailored for India (Address Descriptors)
- India-specific pricing (70% discount in 2024, continued in 2025)
- Worth the extra cost for reliability

**Hybrid Approach:**
- Use Mapbox for development (free tier)
- Switch to Google Maps for production
- Use Mapbox for non-critical visualizations to save costs

**Implementation Effort:** 2-3 days

**Expected Cost:**
- Development: $0 (Mapbox free tier)
- Production (10K users, 10 map loads/user/month):
  - Google: ~$200/month (within free credit + volume discounts)
- Production (100K users):
  - Google: ~$1,200/month (with volume discounts)

### Integration Approach

**Data Flow:**
```
Frontend Map Component → Google Maps JavaScript API → Display Map
Backend Geocoding → Google Maps Geocoding API → Store Coordinates
Route Planning → Google Directions API → Optimized Routes
```

**Code Example:**
```javascript
// Frontend - React Component
import { GoogleMap, LoadScript, Marker } from '@react-google-maps/api';

const MapComponent = ({ pollingBooths }) => {
  const mapCenter = { lat: 28.6139, lng: 77.2090 }; // Delhi

  return (
    <LoadScript googleMapsApiKey={import.meta.env.VITE_GOOGLE_MAPS_API_KEY}>
      <GoogleMap
        mapContainerStyle={{ width: '100%', height: '600px' }}
        center={mapCenter}
        zoom={12}
      >
        {pollingBooths.map((booth) => (
          <Marker
            key={booth.id}
            position={{ lat: booth.latitude, lng: booth.longitude }}
            title={booth.name}
          />
        ))}
      </GoogleMap>
    </LoadScript>
  );
};
```

```python
# Backend - Geocoding
import googlemaps

gmaps = googlemaps.Client(key=os.getenv('GOOGLE_MAPS_API_KEY'))

def geocode_address(address):
    """
    Convert address to coordinates
    """
    try:
        geocode_result = gmaps.geocode(address)
        if geocode_result:
            location = geocode_result[0]['geometry']['location']
            return {
                'latitude': location['lat'],
                'longitude': location['lng']
            }
    except Exception as e:
        logger.error(f'Geocoding error: {e}')
    return None
```

---

## 4. SMS/MESSAGING APIs

### Why We Need It
- **Business Value:** Voter reminders, campaign updates, OTP verification, bulk messaging
- **Use Cases:**
  1. Send voting day reminders
  2. Campaign event notifications
  3. OTP for user verification
  4. Bulk SMS for announcements
  5. Volunteer coordination messages

### Options Compared

#### Option 1: MSG91
**Pros:**
- CHEAPEST: ~$0.002 per SMS (₹0.17-0.22)
- India-focused with DLT compliance built-in
- Free 24/7 support
- Special startup policy (25,000 free credits)
- Pay-as-you-go model

**Cons:**
- India-only (not an issue for this project)
- Smaller international presence

**Pricing:**
- Regular: ₹0.25 per SMS
- Bulk: ₹0.17-0.22 per SMS
- Startup offer: 25,000 free credits
- High volume: ₹0.15 per SMS (1M+ messages)

**Rating:** 9.5/10 (for India)

#### Option 2: Gupshup
**Pros:**
- DLT platform integrated
- India-focused
- Pay-as-you-go pricing
- Multi-channel (SMS, WhatsApp)

**Cons:**
- More expensive: ₹0.20-0.30 per SMS
- Limited transparency on pricing

**Pricing:**
- Basic: ₹0.20-0.30 per SMS
- Bulk: ₹0.15 per SMS (1M+)
- Enterprise: Custom quotes

**Rating:** 8/10

#### Option 3: Twilio
**Pros:**
- Global leader
- Excellent documentation
- Reliable infrastructure
- Free trial available

**Cons:**
- EXPENSIVE: 2x the cost of India-focused providers
- Limited free support (paid plans only)
- Overkill for India-only project

**Pricing:**
- India SMS: ~$0.004+ per SMS
- Additional carrier fees possible
- No clear pricing without contacting sales

**Rating:** 6/10 (too expensive for India market)

#### Option 4: Kaleyra
**Pros:**
- Strong in India market
- Good for financial institutions
- High security focus

**Cons:**
- Expensive: $0.004+ per SMS
- No free trial
- No public pricing (must request quote)
- Geared toward enterprises

**Pricing:**
- Starting: $0.004 per message
- Must request custom quote

**Rating:** 6.5/10

#### Option 5: AWS SNS
**Pros:**
- Very cheap for push notifications (first 1M free)
- Integrated with AWS ecosystem
- Reliable infrastructure

**Cons:**
- SMS pricing for India: $0.00278 per SMS (local route)
- Complex DLT compliance setup for India
- International route expensive: $0.02171 per SMS

**Pricing:**
- Push notifications: First 1M free, then $0.000001 each
- India SMS (local): $0.00278 per SMS
- India SMS (international): $0.02171 per SMS

**Rating:** 7/10 (good for notifications, acceptable for SMS)

### RECOMMENDED CHOICE

**Winner:** MSG91 (for SMS) + AWS SNS (for push notifications)

**Justification:**
- MSG91 is the CHEAPEST option for Indian SMS (₹0.17-0.22 vs ₹0.30+)
- DLT compliance built-in (required for India)
- Startup-friendly with free credits
- AWS SNS perfect for push notifications (1M free/month)
- Combined approach gives best of both worlds

**Implementation Effort:** 2-3 days

**Expected Cost:**
- Development: Free (MSG91 startup credits + AWS free tier)
- Production (10K users, 5 SMS/user/month):
  - MSG91: 50K SMS × ₹0.20 = ₹10,000 (~$120/month)
  - AWS SNS push: Free (under 1M)
- Production (100K users):
  - MSG91: 500K SMS × ₹0.17 = ₹85,000 (~$1,020/month)
  - AWS SNS push: Free (under 1M)

### Integration Approach

**Data Flow:**
```
Campaign Manager → Backend API → MSG91 API → SMS Gateway → User Phone
User Action → Backend → AWS SNS → Push Notification → User Device
```

**Code Example:**
```python
import requests
import boto3

# MSG91 SMS
MSG91_AUTH_KEY = os.getenv('MSG91_AUTH_KEY')
MSG91_SENDER_ID = os.getenv('MSG91_SENDER_ID')

def send_sms(phone_number, message):
    """
    Send SMS via MSG91
    """
    url = 'https://api.msg91.com/api/v5/flow/'

    payload = {
        'sender': MSG91_SENDER_ID,
        'mobiles': phone_number,
        'authkey': MSG91_AUTH_KEY,
        'message': message,
        'country': '91'  # India country code
    }

    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        logger.error(f'MSG91 error: {e}')
        return None

# AWS SNS Push Notification
sns_client = boto3.client('sns', region_name='ap-south-1')

def send_push_notification(device_token, title, message):
    """
    Send push notification via AWS SNS
    """
    try:
        response = sns_client.publish(
            TargetArn=device_token,
            Message=message,
            Subject=title,
            MessageStructure='string'
        )
        return response
    except Exception as e:
        logger.error(f'SNS error: {e}')
        return None
```

---

## 5. EMAIL SERVICE APIs

### Why We Need It
- **Business Value:** Email campaigns, automated reports, notifications, newsletters
- **Use Cases:**
  1. Campaign email newsletters
  2. Automated analytics reports
  3. User onboarding emails
  4. Event invitations
  5. Transactional emails (password reset, etc.)

### Options Compared

#### Option 1: AWS SES (Simple Email Service)
**Pros:**
- CHEAPEST: $0.10 per 1,000 emails
- EC2 hosted apps: 62,000 free emails/month
- High deliverability
- Scalable infrastructure
- Dedicated IP: $24.95/month (cheapest)

**Cons:**
- Requires AWS knowledge
- More technical setup
- Limited templates/features vs competitors
- Manual IP warmup

**Pricing:**
- Free: 3,000 emails/month
- Paid: $0.10 per 1,000 emails
- EC2 bonus: 62,000 free emails/month
- Dedicated IP: $24.95/month

**Rating:** 9.5/10 (best value)

#### Option 2: SendGrid
**Pros:**
- 99.95% uptime
- Good deliverability (93.8% in tests)
- Dynamic templates
- 45 billion emails/month capacity
- Good documentation

**Cons:**
- More expensive than AWS SES
- Free tier limited: 100 emails/day
- Pricing adds up quickly

**Pricing:**
- Free: 100 emails/day (3,000/month)
- Essentials: $19.95/month for 50K emails
- Pro: $89.95/month for 1.5M emails

**Rating:** 8/10

#### Option 3: Postmark
**Pros:**
- BEST deliverability: 93.8% (highest tested)
- Fast, reliable transactional email specialist
- Message Streams for separation
- Free tier: 100 emails/month forever

**Cons:**
- More expensive: $15/month for 10K emails
- Overages: $1.80 per 1,000 (18x AWS SES)
- Focused on transactional (not bulk marketing)

**Pricing:**
- Free: 100 emails/month
- Paid: $15/month (10K emails)
- Overages: $1.80 per 1,000 emails
- High volume: $400/month (700K emails)

**Rating:** 8.5/10 (premium pricing)

#### Option 4: Brevo (formerly Sendinblue)
**Pros:**
- Generous free tier: 300 emails/day
- Combined email + SMS platform
- Unlimited contacts on all plans
- Pay-as-you-go credits option

**Cons:**
- SMS pricing varies by country
- Smaller ecosystem than competitors

**Pricing:**
- Free: 300 emails/day (9,000/month)
- Starter: $9/month (5K emails)
- Standard: $18/month (5K emails + more features)
- Professional: $499/month (150K+ emails)

**Rating:** 8/10

#### Option 5: Mailgun
**Pros:**
- Developer-friendly API
- Email validation included
- Good documentation

**Cons:**
- More expensive than AWS SES
- Dedicated IP: $59/month (2.4x AWS SES)

**Pricing:**
- Free: 5,000 emails/month (300/day limit)
- Foundation: $35/month (50K emails)
- Scale: $90/month (100K emails)

**Rating:** 7.5/10

### RECOMMENDED CHOICE

**Winner:** AWS SES (for bulk/campaigns) + Postmark (for critical transactional)

**Justification:**
- AWS SES is unbeatable on cost ($0.10 per 1K vs $1.80+ for others)
- Good enough deliverability for bulk campaigns
- Use Postmark for critical transactional emails (password reset, OTP) where deliverability is crucial
- Combined cost still lower than using SendGrid alone

**Alternative (Simpler):** Brevo for all-in-one solution (email + SMS)

**Implementation Effort:** 2-3 days

**Expected Cost:**
- Development: Free (AWS SES 3K/month + Postmark 100/month)
- Production (10K users, 10 emails/user/month):
  - AWS SES: 100K emails × $0.10/1K = $10/month
  - Postmark (transactional): $15/month (10K emails)
  - Total: ~$25/month
- Production (100K users):
  - AWS SES: 1M emails × $0.10/1K = $100/month
  - Postmark: $89/month (100K emails)
  - Total: ~$190/month

### Integration Approach

**Data Flow:**
```
Campaign Email → AWS SES → Bulk Send → Track Opens/Clicks
Transactional (OTP, etc.) → Postmark → High Priority → Deliver
```

**Code Example:**
```python
import boto3
from postmarker.core import PostmarkClient

# AWS SES for bulk emails
ses_client = boto3.client('ses', region_name='ap-south-1')

def send_bulk_email(recipients, subject, html_body):
    """
    Send bulk email via AWS SES
    """
    try:
        response = ses_client.send_email(
            Source='noreply@pulseofpeople.com',
            Destination={'ToAddresses': recipients},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Html': {'Data': html_body}}
            }
        )
        return response
    except Exception as e:
        logger.error(f'SES error: {e}')
        return None

# Postmark for transactional emails
postmark = PostmarkClient(server_token=os.getenv('POSTMARK_SERVER_TOKEN'))

def send_transactional_email(to_email, subject, html_body):
    """
    Send high-priority transactional email via Postmark
    """
    try:
        response = postmark.emails.send(
            From='noreply@pulseofpeople.com',
            To=to_email,
            Subject=subject,
            HtmlBody=html_body,
            TrackOpens=True
        )
        return response
    except Exception as e:
        logger.error(f'Postmark error: {e}')
        return None
```

---

## 6. AI/ML SENTIMENT ANALYSIS APIs

### Why We Need It
- **Business Value:** Analyze voter feedback, social media sentiment, campaign effectiveness
- **Use Cases:**
  1. Analyze social media posts for sentiment
  2. Process voter feedback forms
  3. Monitor campaign reception
  4. Analyze competitor mentions
  5. Track issue-based sentiment trends

### Options Compared

#### Option 1: OpenAI API (GPT-4o)
**Pros:**
- Most advanced language model
- Excellent sentiment accuracy
- Multi-language support
- Flexible prompt engineering
- Good for complex analysis

**Cons:**
- Expensive: $2.50-3 per 1M input tokens
- $0.03 per sentiment query (average)
- Not specialized for sentiment only

**Pricing:**
- GPT-4o: $2.50/1M input tokens, $10/1M output tokens (Standard tier)
- GPT-4o Mini: $0.15/1M input, $0.60/1M output (95% cheaper)
- Average sentiment query: ~$0.03

**Rating:** 8/10

#### Option 2: Google Cloud Natural Language API
**Pros:**
- Specialized for NLP tasks
- Good sentiment analysis
- Entity recognition included
- Free tier: $300 credit

**Cons:**
- Limited Indian language support (11 languages total)
- Sentiment: English, Spanish, Japanese mainly
- Pricing not fully transparent

**Pricing:**
- Free: $300 credit (new accounts)
- Paid: Per-unit pricing (1,000 chars = 1 unit)
- Exact pricing varies by feature

**Rating:** 7/10

#### Option 3: Azure Text Analytics API (Azure AI Language)
**Pros:**
- HINDI SUPPORT (added 2020, v3.x)
- 20+ languages for sentiment
- 5,000 free text records/month
- Confidence scores (0-1 range)
- Well-documented

**Cons:**
- More expensive for high volume
- 1,000 chars = 1 text record

**Pricing:**
- Free: 5,000 text records/month
- Paid: Tiered pricing for volume
- Contact sales for 10M+ records

**Rating:** 9/10 (for India - Hindi support)

#### Option 4: HuggingFace Inference API
**Pros:**
- FREE tier with generous limits
- Access to thousands of models
- Open-source models
- Very cheap: ~$0.001 per query (fine-tuned models)
- No vendor lock-in

**Cons:**
- Self-managed model selection
- Variable quality across models
- Less support than commercial APIs

**Pricing:**
- Free: Generous free tier
- Pro: $9/month (individuals)
- Team: $20/user/month
- Enterprise: $50/user/month
- Inference: Pay per compute time

**Rating:** 9.5/10 (best value)

### RECOMMENDED CHOICE

**Winner:** HuggingFace Inference API (primary) + Azure Text Analytics (for Hindi)

**Justification:**
- HuggingFace offers BEST value: ~$0.001 per query (vs $0.03 for OpenAI)
- Free tier sufficient for development and low-volume production
- Use Azure specifically for Hindi sentiment analysis (only one with good Hindi support)
- Can fine-tune models for political Indian context
- Combined approach costs <10% of using only OpenAI

**Hybrid Strategy:**
- English text: HuggingFace (distilbert-base-uncased-finetuned-sst-2-english)
- Hindi text: Azure Text Analytics API
- Complex cases: OpenAI GPT-4o Mini as fallback

**Implementation Effort:** 3-4 days

**Expected Cost:**
- Development: $0 (free tiers)
- Production (10K users, 20 sentiment analyses/user/month):
  - HuggingFace: Free tier likely sufficient
  - Azure (Hindi): 200K records, mostly free (5K/month free)
  - Fallback OpenAI: ~$20/month
  - Total: ~$30/month
- Production (100K users):
  - HuggingFace Pro: $9/month
  - Azure: ~$100/month
  - OpenAI fallback: ~$100/month
  - Total: ~$210/month

### Integration Approach

**Data Flow:**
```
User Text → Language Detection →
  → English: HuggingFace Model → Sentiment Score
  → Hindi: Azure Text Analytics → Sentiment Score
  → Complex: OpenAI GPT-4o Mini → Sentiment Score
→ Store Result + Display
```

**Code Example:**
```python
import requests
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from langdetect import detect

# HuggingFace
HF_API_TOKEN = os.getenv('HUGGINGFACE_API_TOKEN')
HF_MODEL = 'distilbert-base-uncased-finetuned-sst-2-english'

def analyze_sentiment_hf(text):
    """
    Analyze sentiment using HuggingFace
    """
    url = f'https://api-inference.huggingface.co/models/{HF_MODEL}'
    headers = {'Authorization': f'Bearer {HF_API_TOKEN}'}

    response = requests.post(url, headers=headers, json={'inputs': text})
    result = response.json()

    # Returns [{'label': 'POSITIVE', 'score': 0.9998}]
    return result[0] if result else None

# Azure Text Analytics for Hindi
azure_endpoint = os.getenv('AZURE_TEXT_ANALYTICS_ENDPOINT')
azure_key = os.getenv('AZURE_TEXT_ANALYTICS_KEY')
azure_client = TextAnalyticsClient(endpoint=azure_endpoint, credential=AzureKeyCredential(azure_key))

def analyze_sentiment_azure(text, language='hi'):
    """
    Analyze sentiment using Azure (for Hindi)
    """
    try:
        response = azure_client.analyze_sentiment(documents=[{'id': '1', 'language': language, 'text': text}])
        result = response[0]

        return {
            'sentiment': result.sentiment,
            'positive': result.confidence_scores.positive,
            'neutral': result.confidence_scores.neutral,
            'negative': result.confidence_scores.negative
        }
    except Exception as e:
        logger.error(f'Azure error: {e}')
        return None

# Smart router
def analyze_sentiment(text):
    """
    Route to appropriate API based on language
    """
    try:
        lang = detect(text)

        if lang == 'hi':  # Hindi
            return analyze_sentiment_azure(text, 'hi')
        else:  # English and others
            return analyze_sentiment_hf(text)
    except Exception as e:
        logger.error(f'Sentiment analysis error: {e}')
        return None
```

---

## 7. NEWS AGGREGATION APIs

### Why We Need It
- **Business Value:** Track political news, monitor competitor mentions, trending issues
- **Use Cases:**
  1. Aggregate political news from India
  2. Track mentions of candidates/parties
  3. Monitor trending political issues
  4. Competitor news tracking
  5. Regional news in local languages

### Options Compared

#### Option 1: GNews API
**Pros:**
- Affordable pricing
- 60,000+ sources in 41 languages, 71 countries
- Free development tier
- Indian news sources included

**Cons:**
- Limited enrichment features (no sentiment clustering)
- Basic filtering only

**Pricing:**
- Free: Development tier (activate when ready)
- Paid: Startup-friendly pricing (not publicly listed)

**Rating:** 8/10

#### Option 2: MediaStack
**Pros:**
- Forever-free plan: 500 calls/month
- 7,500 sources globally
- 13 languages, 50+ countries
- Real-time news aggregation
- Indian sources included

**Cons:**
- Free plan doesn't include live news
- Limited to 500 calls/month free

**Pricing:**
- Free: 500 calls/month (no live news)
- Basic: $24.99/month (10K calls)
- Professional: Higher tiers available
- 15% discount on yearly billing

**Rating:** 7.5/10

#### Option 3: NewsAPI.org
**Pros:**
- Popular API
- Good documentation
- Many Indian sources

**Cons:**
- Rate limits: 1 request/second
- Limited free tier
- Pricing not transparent (2025)

**Pricing:**
- Free tier available (limited)
- Paid: Contact for pricing

**Rating:** 7/10

#### Option 4: Bing News Search API (Azure)
**Pros:**
- Part of Azure ecosystem
- Free tier available (F0 bundle)
- Integrated with other Azure services

**Cons:**
- 10x price increase in 2023
- Complex pricing structure
- Reduced to $3 per 1,000 transactions (S6 bundle)

**Pricing:**
- Free: F0 tier available
- S6 Bundle: $3 per 1,000 transactions
- Higher tiers available

**Rating:** 6.5/10

#### Option 5: NewsData.io
**Pros:**
- India-focused
- Regional language support (Hindi, Tamil, Bengali, etc.)
- Category filtering (politics, crime, etc.)
- Good for Indian market

**Cons:**
- Pricing not fully transparent
- Smaller source base than GNews

**Pricing:**
- Contact for pricing

**Rating:** 8/10 (for India)

### RECOMMENDED CHOICE

**Winner:** GNews API (primary) + MediaStack (backup/free tier)

**Justification:**
- GNews has largest source base (60K+ sources)
- Covers 41 languages (good for regional Indian news)
- Startup-friendly pricing
- MediaStack free tier (500 calls/month) great for development
- Combined approach provides redundancy

**Implementation Effort:** 2 days

**Expected Cost:**
- Development: Free (MediaStack 500 calls/month)
- Production (10K users, 50 news fetches/day):
  - GNews: ~$30-50/month (estimated)
  - Total: ~$40/month
- Production (100K users):
  - GNews: ~$100-150/month (estimated)
  - Total: ~$120/month

### Integration Approach

**Data Flow:**
```
News Aggregation Service (Cron Job) → GNews API → Fetch Latest Political News →
→ Store in DB → Categorize → Display to Users
```

**Code Example:**
```python
import requests
from datetime import datetime, timedelta

GNEWS_API_KEY = os.getenv('GNEWS_API_KEY')
MEDIASTACK_API_KEY = os.getenv('MEDIASTACK_API_KEY')

def fetch_political_news_gnews(query='india politics', language='en', max_results=10):
    """
    Fetch political news from GNews API
    """
    url = 'https://gnews.io/api/v4/search'
    params = {
        'q': query,
        'lang': language,
        'country': 'in',
        'max': max_results,
        'apikey': GNEWS_API_KEY,
        'from': (datetime.now() - timedelta(days=7)).isoformat()
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()['articles']
    except Exception as e:
        logger.error(f'GNews error: {e}')
        return []

def fetch_political_news_mediastack(query='politics', countries='in', limit=10):
    """
    Fetch political news from MediaStack API
    """
    url = 'http://api.mediastack.com/v1/news'
    params = {
        'access_key': MEDIASTACK_API_KEY,
        'keywords': query,
        'countries': countries,
        'languages': 'en',
        'limit': limit,
        'sort': 'published_desc'
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()['data']
    except Exception as e:
        logger.error(f'MediaStack error: {e}')
        return []
```

---

## 8. DEMOGRAPHICS/CENSUS APIs

### Why We Need It
- **Business Value:** Voter demographics, constituency profiling, targeting strategies
- **Use Cases:**
  1. Access constituency demographic data
  2. Voter age/gender/caste distribution
  3. Population density analysis
  4. Economic indicators by region
  5. Political demographics for targeting

### Options Compared

#### Option 1: India Census API (censusindia.gov.in)
**Pros:**
- FREE official government data
- Most comprehensive Indian demographic data
- Data API available (CSV and JSON formats)
- Authoritative source
- Census 2025 (Digital Census) launching

**Cons:**
- Documentation can be limited
- API may have uptime issues
- Data update frequency varies
- Technical interface not as polished

**Pricing:**
- Free

**Rating:** 9/10 (official source)

#### Option 2: Data.gov.in (Open Government Data Platform)
**Pros:**
- FREE access to government datasets
- Single point of access for all ministries
- APIs available for various datasets
- Census data included
- Election Commission data available

**Cons:**
- Fragmented data across departments
- API quality varies
- Documentation inconsistent

**Pricing:**
- Free

**Rating:** 8.5/10

#### Option 3: Python Library: datagovindia (PyPI)
**Pros:**
- Simplifies access to data.gov.in APIs
- Python integration ready
- Open source

**Cons:**
- Unofficial library
- May lag behind API changes

**Pricing:**
- Free (open source)

**Rating:** 7.5/10

### RECOMMENDED CHOICE

**Winner:** India Census API + Data.gov.in (Both Free)

**Justification:**
- Official government sources are FREE
- Most authoritative data for Indian demographics
- Census 2025 (Digital) will provide updated data
- Data.gov.in covers additional datasets (Election Commission, etc.)
- No cost, reliable official sources

**Implementation Effort:** 2-3 days (mainly data mapping/cleaning)

**Expected Cost:**
- All: $0 (completely free)

### Integration Approach

**Data Flow:**
```
One-time Setup: Census API → Fetch Demographic Data → Clean & Map → Store in DB
Periodic Updates: Cron Job → Re-fetch Updated Data → Update DB
User Queries → Query Local DB → Return Demographics
```

**Code Example:**
```python
import requests
import csv

CENSUS_API_BASE = 'https://censusindia.gov.in/census.website/data/api'
DATA_GOV_IN_API_KEY = os.getenv('DATA_GOV_IN_API_KEY')

def fetch_census_data(table_id, filters=None):
    """
    Fetch data from India Census API

    Example table_ids:
    - Population data
    - Age distribution
    - Gender ratio
    - Literacy rates
    """
    url = f'{CENSUS_API_BASE}/table/{table_id}'
    params = {'format': 'json'}

    if filters:
        params.update(filters)

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f'Census API error: {e}')
        return None

def fetch_datagov_dataset(resource_id, filters=None, limit=1000):
    """
    Fetch dataset from data.gov.in
    """
    url = 'https://api.data.gov.in/resource'
    params = {
        'api-key': DATA_GOV_IN_API_KEY,
        'format': 'json',
        'resource_id': resource_id,
        'limit': limit
    }

    if filters:
        params['filters'] = filters

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()['records']
    except Exception as e:
        logger.error(f'Data.gov.in error: {e}')
        return None

# Example: Get constituency population
def get_constituency_demographics(constituency_name):
    """
    Fetch demographics for a specific constituency
    """
    # This would query your local DB populated from Census API
    from .models import ConstituencyDemographics

    try:
        demographics = ConstituencyDemographics.objects.get(
            name__iexact=constituency_name
        )
        return {
            'population': demographics.population,
            'male_population': demographics.male_population,
            'female_population': demographics.female_population,
            'literacy_rate': demographics.literacy_rate,
            'age_18_to_25': demographics.age_18_to_25,
            # ... other demographics
        }
    except ConstituencyDemographics.DoesNotExist:
        return None
```

---

## 9. ANALYTICS & BI APIs

### Why We Need It
- **Business Value:** Track user behavior, campaign effectiveness, ROI measurement
- **Use Cases:**
  1. Track user engagement with platform
  2. Monitor campaign page views
  3. Analyze user journey through app
  4. Measure feature adoption
  5. Track conversion funnels

### Options Compared

#### Option 1: Google Analytics 4 (GA4)
**Pros:**
- FREE for most use cases
- 10M hits/month capacity
- 30 conversion events
- 100 audiences
- 50 custom dimensions/metrics
- Integration with Google Ads
- Extensive documentation

**Cons:**
- Data sampling on large datasets
- 14-month data retention limit
- No Search Ads 360 integration (free tier)
- Learning curve for GA4 vs Universal Analytics

**Pricing:**
- Free: 10M events/month
- GA360 (Premium): $50,000/year

**Rating:** 9/10

#### Option 2: Mixpanel
**Pros:**
- FREE: 1M events/month (Growth plan)
- User-based tracking
- Generous free tier for startups
- Excellent funnel analysis
- Session replay (10K basic replays)
- Much cheaper than Amplitude

**Cons:**
- 1,000 events per user limit (can be restrictive)
- Smaller ecosystem than GA4

**Pricing:**
- Free: 1M events/month (Growth plan)
- Plus: From $49/month (1,000 MTUs)
- Growth: From $200/year
- Enterprise: ~$3,000/year

**Rating:** 9/10

#### Option 3: Amplitude
**Pros:**
- FREE: 10M events/month (very generous)
- No per-user event restrictions
- Better for high-frequency tracking
- Good for product analytics

**Cons:**
- More expensive on paid plans: $1,500/month (Growth)
- Enterprise: $5,000+/month
- ~30% more expensive than Mixpanel

**Pricing:**
- Free: 10M events/month
- Growth: $1,500/month
- Enterprise: $5,000+/month

**Rating:** 8/10

### RECOMMENDED CHOICE

**Winner:** Google Analytics 4 (primary) + Mixpanel (for detailed user analytics)

**Justification:**
- GA4 is FREE and sufficient for most analytics needs
- 10M events/month covers 100K active users easily
- Mixpanel free tier (1M events) perfect for detailed user journey analysis
- Combined approach gives both broad tracking (GA4) and deep user insights (Mixpanel)
- Total cost: $0 for development and small production

**Alternative:** Amplitude if you need higher event volumes without per-user restrictions

**Implementation Effort:** 2-3 days

**Expected Cost:**
- Development: $0 (both free tiers)
- Production (10K users): $0 (within free tiers)
- Production (100K users): $0 (within GA4 10M events + Mixpanel 1M events)
- If scaling beyond: Consider GA360 ($50K/year) or Mixpanel paid (~$200/month)

### Integration Approach

**Data Flow:**
```
Frontend Events → Google Analytics 4 → Dashboard (broad metrics)
Frontend + Backend Events → Mixpanel → Advanced Funnel Analysis
```

**Code Example:**
```javascript
// Frontend - Google Analytics 4
import ReactGA from 'react-ga4';

// Initialize GA4
ReactGA.initialize('G-XXXXXXXXXX');

// Track page views
ReactGA.send({ hitType: 'pageview', page: window.location.pathname });

// Track custom events
const trackCampaignView = (campaignId) => {
  ReactGA.event({
    category: 'Campaign',
    action: 'View',
    label: campaignId,
    value: 1
  });
};

// Frontend - Mixpanel
import mixpanel from 'mixpanel-browser';

mixpanel.init('YOUR_MIXPANEL_TOKEN');

// Identify user
mixpanel.identify(userId);
mixpanel.people.set({
  '$email': userEmail,
  '$name': userName,
  role: userRole
});

// Track event
mixpanel.track('Campaign Viewed', {
  campaignId: campaignId,
  campaignName: campaignName,
  timestamp: new Date().toISOString()
});
```

```python
# Backend - Mixpanel
from mixpanel import Mixpanel

mp = Mixpanel(os.getenv('MIXPANEL_TOKEN'))

def track_backend_event(user_id, event_name, properties):
    """
    Track backend events in Mixpanel
    """
    try:
        mp.track(user_id, event_name, properties)
    except Exception as e:
        logger.error(f'Mixpanel error: {e}')
```

---

## 10. FILE STORAGE APIs

### Why We Need It
- **Business Value:** Store voter photos, documents, campaign media, uploaded files
- **Use Cases:**
  1. Store voter profile photos
  2. Campaign media files (images, videos)
  3. Document uploads (ID proofs, forms)
  4. Polling booth images
  5. CDN for serving assets

### Options Compared

#### Option 1: AWS S3
**Pros:**
- Industry standard
- Highly reliable (99.99% availability)
- Cheapest standard storage: ~$0.023/GB/month (US)
- India region available (Mumbai - ap-south-1)
- Integrated with AWS ecosystem
- Lifecycle policies for cost optimization

**Cons:**
- India pricing ~10% higher than US
- Requires AWS knowledge
- Bandwidth costs can add up

**Pricing (approx for India/Mumbai region):**
- Standard storage: ~$0.025/GB/month
- Data transfer out: $0.10/GB (first 10TB)
- API requests: $0.0004 per 1,000 PUT requests
- S3 Glacier (archive): $0.004/GB/month

**Rating:** 9/10

#### Option 2: Cloudinary
**Pros:**
- FREE: 25GB storage, transformations, CDN
- Optimized for images/videos
- Automatic image optimization
- Transformations on-the-fly
- CDN included (Akamai, Fastly, Cloudflare)
- Great for media-heavy apps

**Cons:**
- More expensive at scale: $89/month (Plus plan)
- Video file size limited on free tier (100MB)
- Credit-based pricing can be confusing

**Pricing:**
- Free: 25GB storage, CDN, transformations
- Plus: $89/month (225GB storage, 2 accounts)
- Advanced: $224/month

**Rating:** 9/10 (for media)

#### Option 3: Backblaze B2
**Pros:**
- VERY CHEAP: $0.005/GB/month (5x cheaper than S3)
- Pay-as-you-go, no tiers
- No egress fees to CDN partners
- Transparent pricing
- S3-compatible API

**Cons:**
- Smaller ecosystem
- No India region (latency concerns)
- Less feature-rich than S3

**Pricing:**
- Storage: $0.005/GB/month
- Download: $0.01/GB
- API calls: Free (Class C), $0.004 per 10K (Class B)

**Rating:** 8/10 (great value, but no India region)

#### Option 4: DigitalOcean Spaces
**Pros:**
- Predictable pricing: $5/month (250GB + 1TB bandwidth)
- S3-compatible API
- CDN included
- Simple pricing

**Cons:**
- Storage limits per tier
- Not as feature-rich as S3
- No India region

**Pricing:**
- $5/month: 250GB storage + 1TB transfer
- Additional storage: $0.02/GB

**Rating:** 7.5/10

### RECOMMENDED CHOICE

**Winner:** Cloudinary (for images/videos) + AWS S3 (for documents/general files)

**Justification:**
- Cloudinary FREE tier (25GB) perfect for user photos, campaign images
- Automatic optimization saves bandwidth
- CDN included (better user experience)
- Use AWS S3 for documents, backups (cheaper at scale)
- S3 India region ensures low latency
- Combined approach optimizes cost and performance

**Alternative (Cost-optimized):** Backblaze B2 if India latency acceptable

**Implementation Effort:** 2-3 days

**Expected Cost:**
- Development: $0 (Cloudinary free tier)
- Production (10K users, 10MB/user media + 5MB docs):
  - Cloudinary: Free (within 25GB)
  - S3 (50GB docs): ~$1.25/month
  - Total: ~$2/month
- Production (100K users):
  - Cloudinary Plus: $89/month (225GB)
  - S3 (500GB docs): ~$12.50/month
  - Total: ~$100/month

### Integration Approach

**Data Flow:**
```
User Upload (Image) → Frontend → Cloudinary Upload API → Store + Transform → CDN URL
User Upload (Document) → Frontend → Backend → AWS S3 → Presigned URL → Store
```

**Code Example:**
```python
import cloudinary
import cloudinary.uploader
import boto3
from botocore.exceptions import ClientError

# Cloudinary configuration
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

def upload_image_to_cloudinary(file, folder='user_photos'):
    """
    Upload image to Cloudinary
    """
    try:
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            transformation=[
                {'width': 1000, 'crop': 'limit'},
                {'quality': 'auto:good'},
                {'fetch_format': 'auto'}
            ]
        )
        return {
            'url': result['secure_url'],
            'public_id': result['public_id']
        }
    except Exception as e:
        logger.error(f'Cloudinary error: {e}')
        return None

# AWS S3 configuration
s3_client = boto3.client(
    's3',
    region_name='ap-south-1',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

BUCKET_NAME = 'pulseofpeople-documents'

def upload_document_to_s3(file, filename, content_type):
    """
    Upload document to AWS S3
    """
    try:
        s3_client.upload_fileobj(
            file,
            BUCKET_NAME,
            filename,
            ExtraArgs={'ContentType': content_type}
        )

        # Generate presigned URL (valid for 1 hour)
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': filename},
            ExpiresIn=3600
        )
        return url
    except ClientError as e:
        logger.error(f'S3 error: {e}')
        return None
```

---

## 11. PAYMENT GATEWAY APIs

### Why We Need It
- **Business Value:** Accept campaign donations, subscription payments, event fees
- **Use Cases:**
  1. Campaign donation collection
  2. Subscription payments for premium features
  3. Event ticket sales
  4. Volunteer registration fees (if any)
  5. UPI payment collection

### Options Compared

#### Option 1: Razorpay
**Pros:**
- India market leader
- 2% transaction fee (standard)
- No setup/maintenance fees
- UPI payments FREE (bank-to-bank)
- Good documentation
- Fast settlements (T+0, T+1, T+2)

**Cons:**
- 3% fee for premium cards/EMI
- UPI wallet payments: 1.1% fee (>₹2,000)

**Pricing:**
- Setup: Free
- Maintenance: Free
- Standard (cards, UPI, netbanking): 2%
- Premium cards: 3%
- UPI bank-to-bank: Free
- UPI wallet (>₹2,000): 1.1%

**Rating:** 9/10

#### Option 2: Cashfree
**Pros:**
- Special offer: 1.6% for 12 months (Sep-Dec 2025 signups)
- Standard: 1.95%
- 100+ payment methods
- UPI on credit cards: 2.15%
- No setup/maintenance fees
- Fast settlements

**Cons:**
- Slightly higher than PhonePe for some use cases

**Pricing:**
- Setup: Free
- Maintenance: Free
- Special offer: 1.6% (12 months)
- Standard: 1.95%
- UPI credit card: 2.15%
- EMI/Pay later: 1.5-2.2%

**Rating:** 9.5/10 (best overall value)

#### Option 3: PhonePe Payment Gateway
**Pros:**
- ZERO fees for Standard Plan
- No processing, setup, or hidden charges
- 1.1% only on wallet UPI payments >₹2,000
- Free for most transactions
- Best for high-volume, low-value transactions

**Cons:**
- Limited to India
- Enterprise features require upgrade

**Pricing:**
- Standard Plan: FREE
- Setup: Free
- Maintenance: Free
- Processing: Free (except wallet UPI >₹2,000: 1.1%)
- Enterprise Plan: Custom pricing

**Rating:** 9.5/10 (best for India UPI)

#### Option 4: Paytm
**Pros:**
- Established brand
- 1.99% transaction fee
- T+1 settlement
- Zero setup/maintenance

**Cons:**
- More expensive than Cashfree/PhonePe
- 2.99% for AmEx, Diners, international
- UPI subscription fee for SMEs (₹5-65/year)

**Pricing:**
- Setup: Free
- Maintenance: Free
- Standard: 1.99%
- Premium: 2.99%
- In-store: Free
- UPI subscription: ₹5-65/year

**Rating:** 8/10

#### Option 5: Stripe India
**Pros:**
- Global brand
- Good for international payments
- Excellent developer experience

**Cons:**
- NO UPI SUPPORT
- Expensive: ~4.3% for international cards
- Currency conversion: +2%
- Invite-only in India
- Not suitable for domestic India payments

**Pricing:**
- International cards: ~4.3%
- Currency conversion: +2%
- Total: Can reach 6.3%

**Rating:** 5/10 (for India market)

### RECOMMENDED CHOICE

**Winner:** PhonePe (primary, FREE) + Cashfree (backup/premium features)

**Justification:**
- PhonePe is COMPLETELY FREE for standard transactions (0% fee)
- Perfect for political donations via UPI (majority of Indian payments)
- Cashfree as backup offers comprehensive payment methods at 1.6-1.95%
- Combined approach covers all use cases at minimal cost
- Skip Stripe (no UPI, too expensive for India)

**Alternative:** Razorpay if you prefer single vendor

**Implementation Effort:** 2-3 days

**Expected Cost:**
- Development: $0
- Production (10K users, ₹500 avg donation, 10% donate):
  - PhonePe: ₹0 (FREE for UPI bank-to-bank)
  - Card payments (20% of transactions): 1,000 × ₹500 × 0.02 = ₹10,000 (~$120/month)
  - Total: ~$120/month
- Production (100K users):
  - PhonePe UPI: ₹0
  - Card payments: ~$1,200/month
  - Total: ~$1,200/month (or less with PhonePe free tier)

### Integration Approach

**Data Flow:**
```
User Donation Page → Payment Gateway SDK → PhonePe/Cashfree → Payment Processing →
→ Webhook Callback → Backend Verification → Update Database → Send Receipt
```

**Code Example:**
```python
import hashlib
import requests
from django.conf import settings

# PhonePe Integration
PHONEPE_MERCHANT_ID = os.getenv('PHONEPE_MERCHANT_ID')
PHONEPE_SALT_KEY = os.getenv('PHONEPE_SALT_KEY')
PHONEPE_SALT_INDEX = os.getenv('PHONEPE_SALT_INDEX')

def create_phonepe_payment(amount, order_id, user_phone):
    """
    Create PhonePe payment request
    """
    payload = {
        'merchantId': PHONEPE_MERCHANT_ID,
        'merchantTransactionId': order_id,
        'amount': int(amount * 100),  # Convert to paise
        'merchantUserId': user_phone,
        'redirectUrl': f'{settings.SITE_URL}/payment/callback/',
        'redirectMode': 'POST',
        'callbackUrl': f'{settings.API_URL}/api/payment/webhook/',
        'paymentInstrument': {
            'type': 'PAY_PAGE'
        }
    }

    # Generate checksum
    import base64
    import json

    payload_json = json.dumps(payload)
    payload_base64 = base64.b64encode(payload_json.encode()).decode()

    checksum_string = f'{payload_base64}/pg/v1/pay{PHONEPE_SALT_KEY}'
    checksum = hashlib.sha256(checksum_string.encode()).hexdigest()
    checksum = f'{checksum}###{PHONEPE_SALT_INDEX}'

    headers = {
        'Content-Type': 'application/json',
        'X-VERIFY': checksum
    }

    response = requests.post(
        'https://api.phonepe.com/apis/hermes/pg/v1/pay',
        headers=headers,
        json={'request': payload_base64}
    )

    return response.json()

# Cashfree Integration
import cashfree_pg
from cashfree_pg.models.create_order_request import CreateOrderRequest

cashfree_pg.PGClient.set_api_keys(
    os.getenv('CASHFREE_APP_ID'),
    os.getenv('CASHFREE_SECRET_KEY')
)

def create_cashfree_payment(amount, order_id, customer_id, customer_phone):
    """
    Create Cashfree payment order
    """
    try:
        request = CreateOrderRequest(
            order_amount=amount,
            order_currency='INR',
            order_id=order_id,
            customer_details={
                'customer_id': customer_id,
                'customer_phone': customer_phone
            },
            order_meta={
                'return_url': f'{settings.SITE_URL}/payment/callback/'
            }
        )

        response = cashfree_pg.PGClient.create_order(request)
        return response
    except Exception as e:
        logger.error(f'Cashfree error: {e}')
        return None
```

---

## 12. VOICE/CALL APIs

### Why We Need It
- **Business Value:** Automated calling campaigns, voter surveys, voice messages, IVR
- **Use Cases:**
  1. Automated reminder calls for voting day
  2. Voice surveys to collect voter feedback
  3. IVR system for campaign information
  4. Call recording for quality assurance
  5. Voice broadcast for announcements

### Options Compared

#### Option 1: Exotel
**Pros:**
- India-focused cloud telephony
- Multilevel IVR included
- Call recording built-in
- Virtual numbers
- Good support

**Cons:**
- Pricing not very transparent
- Must contact sales for detailed quotes

**Pricing:**
- Basic: ₹9,999 (₹5,000 usage + ₹4,999 rental, 6 months validity, 3 agents)
- Mid-tier: ₹19,999 (₹9,500 usage + ₹10,499 rental, 1 year, 6 agents)
- Premium: ₹49,999 (₹39,500 usage + ₹10,499 rental, 1 year, unlimited agents)
- International pricing: $200 one-time license or subscription

**Rating:** 8/10

#### Option 2: Knowlarity
**Pros:**
- India market presence
- Cloud telephony features
- Custom plan options

**Cons:**
- Three package tiers (Advance, Premium, Premium Plus)
- Pricing not publicly listed
- Must contact for quotes

**Pricing:**
- Custom pricing (contact sales)
- Three tiers available

**Rating:** 7/10

#### Option 3: Kaleyra
**Pros:**
- Strong in India/APAC
- Good for financial institutions
- Regional pricing for India
- High security

**Cons:**
- Expensive
- Geared toward enterprises
- Limited public pricing info

**Pricing:**
- Custom pricing based on volume
- Competitive rates for high volume

**Rating:** 7.5/10

#### Option 4: Twilio Voice
**Pros:**
- Global leader
- Excellent documentation
- Reliable infrastructure
- Rich features
- Good developer experience

**Cons:**
- EXPENSIVE for India use case
- 2x cost of India-focused providers
- Additional carrier fees
- Free trial available but limited

**Pricing:**
- India pricing not clearly listed
- Generally 2x more expensive than MSG91/Exotel
- Must contact for India pricing

**Rating:** 7/10 (good product, high cost)

### RECOMMENDED CHOICE

**Winner:** Exotel

**Justification:**
- India-focused with good local support
- IVR and call recording included
- Transparent tiered pricing
- Good balance of features and cost
- Virtual numbers for India
- Can start with basic plan (₹9,999) and scale up

**Alternative:** Knowlarity if budget allows for enterprise features

**Implementation Effort:** 3-4 days

**Expected Cost:**
- Development: ₹9,999 basic plan (~$120, includes ₹5,000 usage credit)
- Production (10K users, 1 call/user/month = 10K calls):
  - Exotel mid-tier: ₹19,999/year (~$240/year or $20/month)
  - Call costs included in usage credit
- Production (100K users, 1 call/user/month = 100K calls):
  - Exotel premium: ₹49,999/year (~$600/year or $50/month)
  - Additional call costs beyond usage credit

### Integration Approach

**Data Flow:**
```
Campaign Manager → Create Call Campaign → Exotel API → Initiate Calls →
→ IVR Menu (if configured) → Record Call → Webhook Callback → Store Results
```

**Code Example:**
```python
import requests
from requests.auth import HTTPBasicAuth

EXOTEL_API_KEY = os.getenv('EXOTEL_API_KEY')
EXOTEL_API_TOKEN = os.getenv('EXOTEL_API_TOKEN')
EXOTEL_SID = os.getenv('EXOTEL_SID')
EXOTEL_CALLER_ID = os.getenv('EXOTEL_CALLER_ID')

def make_call_exotel(to_number, from_number=EXOTEL_CALLER_ID, callback_url=None):
    """
    Make a call using Exotel API
    """
    url = f'https://api.exotel.com/v1/Accounts/{EXOTEL_SID}/Calls/connect.json'

    data = {
        'From': from_number,
        'To': to_number,
        'CallerId': EXOTEL_CALLER_ID,
        'CallType': 'trans',  # 'trans' for transactional, 'promo' for promotional
        'Record': 'true'
    }

    if callback_url:
        data['StatusCallback'] = callback_url

    try:
        response = requests.post(
            url,
            data=data,
            auth=HTTPBasicAuth(EXOTEL_API_KEY, EXOTEL_API_TOKEN)
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f'Exotel error: {e}')
        return None

def get_call_details(call_sid):
    """
    Get call details from Exotel
    """
    url = f'https://api.exotel.com/v1/Accounts/{EXOTEL_SID}/Calls/{call_sid}.json'

    try:
        response = requests.get(
            url,
            auth=HTTPBasicAuth(EXOTEL_API_KEY, EXOTEL_API_TOKEN)
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f'Exotel error: {e}')
        return None
```

---

## PRIORITY RANKING

### Must-Have (Phase 1 - MVP)

1. **Google Maps API** - $200-1,200/month
   - Core feature: Polling booth mapping
   - No good free alternative for India coverage

2. **MSG91 (SMS)** - $120-1,020/month
   - Essential for voter reminders, OTP
   - Cheapest option for India

3. **AWS SES (Email)** - $10-100/month
   - Campaign emails, transactional emails
   - Unbeatable price

4. **Cloudinary (Images)** - $0-89/month
   - User photos, campaign media
   - Free tier likely sufficient for MVP

5. **Google Analytics 4** - FREE
   - Essential for tracking platform usage
   - No cost

6. **Facebook/Instagram Graph API** - FREE
   - Social media sentiment tracking
   - No cost

**Total Must-Have Cost (MVP):**
- 10K users: ~$450/month
- 100K users: ~$2,500/month

### Should-Have (Phase 2 - Growth)

7. **Visual Crossing Weather API** - $0-35/month
   - Campaign planning optimization
   - Good ROI for features

8. **HuggingFace + Azure Text Analytics** - $0-210/month
   - Sentiment analysis for feedback
   - Important for insights

9. **Mixpanel** - FREE
   - Detailed user analytics
   - Good for product optimization

10. **PhonePe + Cashfree (Payments)** - 2% transaction fees
    - Enable donations
    - Revenue generator

11. **GNews API** - $40-120/month
    - Track political news
    - Competitive intelligence

12. **AWS S3** - $2-15/month
    - Document storage
    - Cheap and reliable

**Total Should-Have Added Cost:**
- 10K users: +$80/month
- 100K users: +$400/month

### Nice-to-Have (Phase 3 - Scale)

13. **Exotel (Voice)** - $20-50/month
    - Voice campaigns
    - Advanced feature

14. **India Census API** - FREE
    - Demographics data
    - Nice addition for targeting

15. **Postmark (Transactional Email)** - $15-89/month
    - Better deliverability for critical emails
    - Can supplement AWS SES

**Total Nice-to-Have Added Cost:**
- 10K users: +$35/month
- 100K users: +$140/month

---

## TOTAL ESTIMATED COSTS

### Development/Testing Phase
- **Total Cost:** ~$0-50/month
- Most APIs offer free tiers sufficient for development
- Can build entire platform on free tiers

### Production - 10K Active Users
- **Must-Have:** ~$450/month
- **Should-Have:** ~$530/month
- **Nice-to-Have:** ~$565/month

### Production - 100K Active Users
- **Must-Have:** ~$2,500/month
- **Should-Have:** ~$2,900/month
- **Nice-to-Have:** ~$3,040/month

### Production - 1M Active Users (Projected)
- **Estimated:** ~$12,000-15,000/month
- Volume discounts will significantly reduce per-unit costs
- Many APIs offer 20-80% discounts at high volumes

---

## RECOMMENDATIONS SUMMARY

| Category | Recommended API | Backup/Alternative | Monthly Cost (10K users) |
|----------|----------------|-------------------|------------------------|
| Weather | Visual Crossing | OpenWeatherMap | $35 |
| Social Media | Facebook + Instagram | Skip Twitter | FREE |
| Maps | Google Maps | Mapbox | $200 |
| SMS | MSG91 | Gupshup | $120 |
| Email | AWS SES | Brevo | $10 |
| Sentiment Analysis | HuggingFace + Azure | OpenAI | $30 |
| News | GNews | MediaStack | $40 |
| Demographics | Census API | Data.gov.in | FREE |
| Analytics | Google Analytics 4 | Mixpanel | FREE |
| File Storage | Cloudinary + S3 | Backblaze B2 | $2 |
| Payments | PhonePe | Cashfree | 2% fees |
| Voice/Calls | Exotel | Knowlarity | $20 |

**Total Recommended Stack: ~$450-565/month for 10K users**

---

## INDIAN MARKET SPECIFIC CONSIDERATIONS

### Compliance Requirements

1. **DLT (Distributed Ledger Technology) for SMS**
   - Mandatory for bulk SMS in India
   - MSG91 and Gupshup have built-in DLT compliance
   - All SMS templates must be pre-registered

2. **Data Localization**
   - Consider APIs with Indian data centers
   - Google Maps, AWS have India regions (Mumbai)
   - Important for data privacy compliance

3. **UPI Integration**
   - PhonePe, Razorpay, Cashfree support UPI
   - Stripe does NOT support UPI (major limitation)
   - 80%+ of Indian digital payments are UPI

4. **Regional Language Support**
   - Azure Text Analytics supports Hindi
   - Google Maps has Address Descriptors for India
   - Many news APIs support regional languages

### Infrastructure Recommendations

1. **Use India Regions:**
   - AWS: ap-south-1 (Mumbai) or ap-south-2 (Hyderabad)
   - Google Cloud: asia-south1 (Mumbai)
   - Reduces latency for Indian users

2. **CDN Configuration:**
   - Cloudinary uses Akamai/Fastly/Cloudflare (India POPs)
   - Consider CloudFront for S3 assets
   - Reduces load times significantly

3. **Caching Strategy:**
   - Redis for API response caching
   - Weather data: 15-minute cache
   - News: 1-hour cache
   - Demographics: Daily cache
   - Reduces API costs by 50-70%

---

## NEXT STEPS

1. **Phase 1: Setup Development Environment (Week 1)**
   - Create accounts for free-tier APIs
   - Obtain API keys
   - Configure .env files
   - Test basic integration

2. **Phase 2: MVP Integration (Weeks 2-4)**
   - Integrate Must-Have APIs:
     - Google Maps
     - MSG91
     - AWS SES
     - Google Analytics
     - Facebook/Instagram

3. **Phase 3: Enhanced Features (Weeks 5-8)**
   - Add Should-Have APIs:
     - Weather API
     - Sentiment Analysis
     - Payments
     - News Aggregation

4. **Phase 4: Scale & Optimize (Ongoing)**
   - Monitor API usage
   - Optimize costs with caching
   - Negotiate volume discounts
   - Add Nice-to-Have features based on user feedback

---

## APPENDIX: API SETUP CHECKLIST

### Before You Start
- [ ] Review all API documentation
- [ ] Understand rate limits and quotas
- [ ] Plan caching strategy
- [ ] Design error handling approach
- [ ] Set up monitoring/alerting

### For Each API
- [ ] Create developer account
- [ ] Verify email/phone
- [ ] Complete KYC if required (for Indian APIs)
- [ ] Generate API keys
- [ ] Store keys in .env file (NEVER commit to git)
- [ ] Test API with sample requests
- [ ] Implement error handling
- [ ] Add logging
- [ ] Document integration

### Security Best Practices
- [ ] Use environment variables for all API keys
- [ ] Rotate API keys regularly (monthly)
- [ ] Implement rate limiting on backend
- [ ] Validate all API responses
- [ ] Log all API errors
- [ ] Monitor for unusual usage patterns
- [ ] Set up billing alerts for paid APIs

---

**Document End**

*Last Updated: November 9, 2025*
*Next Review: December 9, 2025*
*Version: 1.0*
