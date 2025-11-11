# API Cost Estimates - Pulse of People Platform
**Date:** November 9, 2025
**Version:** 1.0
**Currency:** USD (with INR equivalents where applicable)

## Executive Summary

This document provides detailed cost estimates for all third-party APIs across different usage scenarios. Cost projections are provided for:
- **Development/Testing Phase:** 0-100 users
- **Small Production:** 1,000 active users/month
- **Medium Production:** 10,000 active users/month
- **Large Production:** 100,000 active users/month
- **Scale Production:** 1,000,000 active users/month

### Monthly Cost Summary

| User Tier | Must-Have APIs | Should-Have APIs | Nice-to-Have APIs | **Total Estimated** |
|-----------|----------------|------------------|-------------------|-------------------|
| Development (0-100) | $0 | $0 | $0 | **$0-50** |
| Small (1K users) | $50 | $65 | $75 | **$75-150** |
| Medium (10K users) | $450 | $530 | $565 | **$565-700** |
| Large (100K users) | $2,500 | $2,900 | $3,040 | **$3,040-3,500** |
| Scale (1M users) | $12,000 | $14,500 | $15,200 | **$15,200-18,000** |

---

## DETAILED COST BREAKDOWN

### 1. GOOGLE MAPS API

**Use Case:** Polling booth mapping, geocoding, directions

#### Pricing Model
- Free tier: 70,000 Geocoding requests/month (India pricing 2025)
- Free tier: 35,000 Places API calls/month
- Maps JavaScript API: Dynamic pricing (map loads)
- Directions API: Variable pricing with volume discounts

#### Usage Assumptions
| User Tier | Map Loads/Month | Geocoding Requests | Directions API Calls |
|-----------|-----------------|-------------------|----------------------|
| Development | 500 | 100 | 50 |
| Small (1K) | 10,000 | 1,000 | 500 |
| Medium (10K) | 100,000 | 5,000 | 2,000 |
| Large (100K) | 1,000,000 | 20,000 | 10,000 |
| Scale (1M) | 10,000,000 | 100,000 | 50,000 |

#### Cost Estimates
| Tier | Map Loads | Geocoding | Directions | **Monthly Total** |
|------|-----------|-----------|------------|-------------------|
| Development | Free | Free | Free | **$0** |
| Small | Free ($200 credit) | Free | Free | **$0** |
| Medium | ~$150 | Free | $10 | **$160** |
| Large | ~$1,000 | Free | $50 | **$1,050** |
| Scale | ~$6,000 (w/ discounts) | $30 | $250 | **$6,280** |

**Notes:**
- Free $200 monthly credit covers most small usage
- Automatic volume discounts at 5M+ requests (20-80% off)
- India-specific pricing 70% lower than global (2024 reduction continued)
- Caching can reduce costs by 50-70%

**Optimization Tips:**
- Cache geocoding results (90% hit rate possible)
- Use static maps where possible (cheaper)
- Implement marker clustering (reduce map loads)
- Request only needed fields to reduce costs

---

### 2. VISUAL CROSSING WEATHER API

**Use Case:** Campaign planning, event scheduling

#### Pricing Model
- Free: 1,000 requests/day (30,000/month)
- Unlimited: $35/month
- Pay-as-you-go: $0.0001 per record

#### Usage Assumptions
| User Tier | Requests/Month |
|-----------|----------------|
| Development | 1,000 |
| Small (1K) | 5,000 |
| Medium (10K) | 30,000 |
| Large (100K) | 100,000 |
| Scale (1M) | 500,000 |

#### Cost Estimates
| Tier | Requests | Pricing | **Monthly Total** |
|------|----------|---------|-------------------|
| Development | 1,000 | Free tier | **$0** |
| Small | 5,000 | Free tier | **$0** |
| Medium | 30,000 | Free tier (at limit) | **$0** or $35 unlimited |
| Large | 100,000 | Unlimited plan | **$35** |
| Scale | 500,000 | Unlimited plan | **$35** |

**Notes:**
- Unlimited plan ($35/month) is best value for production
- Free tier (30K/month) sufficient for small deployments
- Cache weather data for 15 minutes (reduce requests by 90%)
- Historical data included in all plans

**Optimization Tips:**
- Cache aggressively (weather doesn't change every minute)
- Batch requests for multiple locations
- Use 15-minute cache TTL minimum

---

### 3. MSG91 SMS API

**Use Case:** Voter reminders, OTP, campaign notifications

#### Pricing Model (India)
- Standard: ₹0.20-0.25 per SMS ($0.0024-0.003 USD)
- Bulk discount: ₹0.17 per SMS ($0.002 USD) for high volume
- Startup offer: 25,000 free credits (one-time)

#### Usage Assumptions
| User Tier | SMS/Month | OTP (50% of SMS) | Campaign (50% of SMS) |
|-----------|-----------|------------------|----------------------|
| Development | 100 | 50 | 50 |
| Small (1K) | 5,000 | 2,500 | 2,500 |
| Medium (10K) | 50,000 | 25,000 | 25,000 |
| Large (100K) | 500,000 | 250,000 | 250,000 |
| Scale (1M) | 5,000,000 | 2,500,000 | 2,500,000 |

#### Cost Estimates (USD)
| Tier | SMS Count | Rate per SMS | **Monthly Total** |
|------|-----------|--------------|-------------------|
| Development | 100 | Free (startup credits) | **$0** |
| Small | 5,000 | $0.0024 | **$12** |
| Medium | 50,000 | $0.0024 | **$120** |
| Large | 500,000 | $0.002 (bulk rate) | **$1,000** |
| Scale | 5,000,000 | $0.002 (bulk rate) | **$10,000** |

**Notes:**
- Prices in INR: ₹0.17-0.25 per SMS
- DLT compliance required for India (built-in)
- Startup policy: 25,000 free SMS (one-time offer)
- Undelivered SMS not charged

**Optimization Tips:**
- Use OTP only when necessary (2-factor auth)
- Batch campaign SMS during off-peak hours (may get better rates)
- Track delivery rates and optimize templates
- Consider SMS vs push notification for non-critical alerts

---

### 4. AWS SES (Email Service)

**Use Case:** Campaign emails, transactional emails, newsletters

#### Pricing Model
- Free: 3,000 emails/month
- EC2 hosted: 62,000 free emails/month
- Paid: $0.10 per 1,000 emails

#### Usage Assumptions
| User Tier | Emails/Month | Transactional | Campaign |
|-----------|--------------|---------------|----------|
| Development | 500 | 300 | 200 |
| Small (1K) | 10,000 | 2,000 | 8,000 |
| Medium (10K) | 100,000 | 10,000 | 90,000 |
| Large (100K) | 1,000,000 | 50,000 | 950,000 |
| Scale (1M) | 10,000,000 | 200,000 | 9,800,000 |

#### Cost Estimates
| Tier | Email Count | Pricing | **Monthly Total** |
|------|-------------|---------|-------------------|
| Development | 500 | Free tier | **$0** |
| Small | 10,000 | $0.10/1K (7K paid) | **$0.70** |
| Medium | 100,000 | $0.10/1K | **$10** |
| Large | 1,000,000 | $0.10/1K | **$100** |
| Scale | 10,000,000 | $0.10/1K | **$1,000** |

**Notes:**
- Cheapest email service on market
- No minimum fees or monthly charges
- Dedicated IP: +$24.95/month (recommended for large volume)
- Good deliverability (not best, but good for price)

**Optimization Tips:**
- Send transactional emails only when needed
- Segment campaign emails to engaged users
- Clean email lists regularly (remove bounces)
- Consider Postmark for critical transactional emails

---

### 5. CLOUDINARY (Image Storage & CDN)

**Use Case:** User photos, campaign media, polling booth images

#### Pricing Model
- Free: 25GB storage, transformations, CDN
- Plus: $89/month (225GB storage)
- Advanced: $224/month

#### Usage Assumptions
| User Tier | Storage (GB) | Transformations | Bandwidth (GB) |
|-----------|--------------|-----------------|----------------|
| Development | 1 | 1,000 | 5 |
| Small (1K) | 10 | 10,000 | 50 |
| Medium (10K) | 100 | 100,000 | 500 |
| Large (100K) | 500 | 1,000,000 | 2,000 |
| Scale (1M) | 2,000 | 5,000,000 | 10,000 |

#### Cost Estimates
| Tier | Storage | Plan | **Monthly Total** |
|------|---------|------|-------------------|
| Development | 1GB | Free | **$0** |
| Small | 10GB | Free | **$0** |
| Medium | 100GB | Free | **$0** (at 25GB limit, upgrade to Plus) |
| Large | 500GB | Plus ($89) | **$89** |
| Scale | 2TB | Advanced ($224+) | **$300** (estimated) |

**Notes:**
- Free tier very generous (25GB)
- Automatic image optimization included
- CDN included (Akamai, Fastly, Cloudflare)
- Video transcoding available

**Optimization Tips:**
- Use automatic format conversion (WebP for modern browsers)
- Implement lazy loading for images
- Use responsive images (srcset)
- Cache transformed images aggressively

---

### 6. AWS S3 (Document Storage)

**Use Case:** Document uploads, backups, general file storage

#### Pricing Model (India - Mumbai region)
- Storage: ~$0.025/GB/month
- Data transfer out: $0.10/GB (first 10TB)
- PUT requests: $0.005 per 1,000
- GET requests: $0.0004 per 1,000

#### Usage Assumptions
| User Tier | Storage (GB) | GET Requests/Month | PUT Requests/Month |
|-----------|--------------|-------------------|-------------------|
| Development | 1 | 1,000 | 100 |
| Small (1K) | 50 | 10,000 | 1,000 |
| Medium (10K) | 500 | 100,000 | 10,000 |
| Large (100K) | 2,000 | 500,000 | 50,000 |
| Scale (1M) | 10,000 | 2,000,000 | 200,000 |

#### Cost Estimates
| Tier | Storage | Requests | Bandwidth | **Monthly Total** |
|------|---------|----------|-----------|-------------------|
| Development | $0.03 | $0 | $0 | **$0** |
| Small | $1.25 | $0.04 | $0.50 | **$2** |
| Medium | $12.50 | $0.40 | $2 | **$15** |
| Large | $50 | $2 | $10 | **$62** |
| Scale | $250 | $8 | $30 | **$288** |

**Notes:**
- Extremely cheap for storage
- India region pricing ~10% higher than US
- Lifecycle policies can reduce costs (move to Glacier)
- Presigned URLs for secure access

**Optimization Tips:**
- Use S3 lifecycle policies (move old files to Glacier)
- Implement CloudFront CDN for frequent access
- Compress files before uploading
- Use S3 Intelligent-Tiering for automatic cost optimization

---

### 7. FACEBOOK & INSTAGRAM GRAPH APIs

**Use Case:** Social media sentiment analysis, page analytics

#### Pricing Model
- **FREE** for basic access
- Rate limits: 200 requests/hour (Instagram)
- No direct costs

#### Usage Assumptions
| User Tier | API Calls/Month |
|-----------|-----------------|
| Development | 1,000 |
| Small (1K) | 5,000 |
| Medium (10K) | 20,000 |
| Large (100K) | 50,000 |
| Scale (1M) | 100,000 |

#### Cost Estimates
| Tier | **Monthly Total** |
|------|-------------------|
| All Tiers | **$0** (FREE) |

**Notes:**
- Completely free (requires Business/Creator account)
- Rate limits sufficient for most use cases
- Premium features available (contact Meta for pricing)

**Optimization Tips:**
- Cache social media data (1-hour TTL)
- Batch requests where possible
- Monitor rate limits closely

---

### 8. HUGGINGFACE + AZURE TEXT ANALYTICS

**Use Case:** Sentiment analysis (English + Hindi)

#### HuggingFace Pricing Model
- Free: Generous free tier
- Pro: $9/month (individuals)
- Inference: Pay per compute time (very cheap)
- Custom models: ~$0.001 per query

#### Azure Text Analytics Pricing
- Free: 5,000 text records/month
- Paid: Tiered pricing (contact sales for 10M+)
- 1,000 characters = 1 text record

#### Usage Assumptions
| User Tier | Sentiment Analyses/Month | English (HF) | Hindi (Azure) |
|-----------|-------------------------|--------------|---------------|
| Development | 100 | 80 | 20 |
| Small (1K) | 5,000 | 4,000 | 1,000 |
| Medium (10K) | 50,000 | 40,000 | 10,000 |
| Large (100K) | 500,000 | 400,000 | 100,000 |
| Scale (1M) | 5,000,000 | 4,000,000 | 1,000,000 |

#### Cost Estimates
| Tier | HuggingFace | Azure | **Monthly Total** |
|------|-------------|-------|-------------------|
| Development | Free | Free | **$0** |
| Small | Free | Free | **$0** |
| Medium | Free | $5 (5K free) | **$10** |
| Large | $9 (Pro) | $100 | **$110** |
| Scale | $50 (Enterprise) | $500 | **$550** |

**Notes:**
- HuggingFace much cheaper than OpenAI ($0.001 vs $0.03 per query)
- Azure specifically for Hindi sentiment
- Combined approach saves 90% vs using only OpenAI

**Optimization Tips:**
- Batch sentiment analysis (process multiple texts together)
- Cache sentiment results for 24 hours
- Use HuggingFace for English, Azure only for Hindi
- Consider fine-tuning own model for Indian political context

---

### 9. GNEWS API

**Use Case:** Political news aggregation, candidate mentions

#### Pricing Model
- Free: Development tier
- Startup: Affordable pricing (not publicly listed)
- Estimated: $30-50/month for 10K requests

#### Usage Assumptions
| User Tier | News Fetches/Day | Requests/Month |
|-----------|------------------|----------------|
| Development | 10 | 300 |
| Small (1K) | 50 | 1,500 |
| Medium (10K) | 100 | 3,000 |
| Large (100K) | 300 | 9,000 |
| Scale (1M) | 1,000 | 30,000 |

#### Cost Estimates
| Tier | Requests | **Monthly Total** |
|------|----------|-------------------|
| Development | 300 | **$0** (free tier) |
| Small | 1,500 | **$10** (estimated) |
| Medium | 3,000 | **$30** |
| Large | 9,000 | **$80** |
| Scale | 30,000 | **$200** |

**Notes:**
- Pricing not publicly listed (estimates based on competitors)
- Can use MediaStack free tier (500 calls/month) as backup
- Cache news for 1 hour to reduce API calls by 90%

**Optimization Tips:**
- Fetch news on schedule (hourly cron job)
- Cache aggressively (news doesn't change every minute)
- Use MediaStack free tier (500/month) as supplement

---

### 10. GOOGLE ANALYTICS 4

**Use Case:** User behavior tracking, funnel analysis

#### Pricing Model
- **FREE** for up to 10M events/month
- GA360 (Premium): $50,000/year (not needed for most)

#### Usage Assumptions
| User Tier | Events/Month |
|-----------|--------------|
| Development | 5,000 |
| Small (1K) | 100,000 |
| Medium (10K) | 1,000,000 |
| Large (100K) | 8,000,000 |
| Scale (1M) | 50,000,000 (need GA360) |

#### Cost Estimates
| Tier | Events | **Monthly Total** |
|------|--------|-------------------|
| Development | 5K | **$0** |
| Small | 100K | **$0** |
| Medium | 1M | **$0** |
| Large | 8M | **$0** |
| Scale | 50M | **$4,167/month** (GA360) |

**Notes:**
- FREE tier covers 100K users easily (10M events/month)
- Only need GA360 at massive scale (1M+ users)
- No hidden costs

---

### 11. MIXPANEL

**Use Case:** Advanced user analytics, funnels

#### Pricing Model
- Free: 1M events/month (Growth plan)
- Plus: From $49/month (1,000 MTUs)
- Growth: From $200/year
- Enterprise: ~$3,000/year

#### Usage Assumptions
| User Tier | Events/Month | MTUs |
|-----------|--------------|------|
| Development | 10,000 | 100 |
| Small (1K) | 100,000 | 1,000 |
| Medium (10K) | 800,000 | 8,000 |
| Large (100K) | 5,000,000 | 50,000 |
| Scale (1M) | 20,000,000 | 200,000 |

#### Cost Estimates
| Tier | **Monthly Total** |
|------|-------------------|
| Development | **$0** (free tier) |
| Small | **$0** (free tier) |
| Medium | **$0** (just under free tier limit) |
| Large | **$200/year** (~$17/month) |
| Scale | **$500/month** (estimated) |

**Notes:**
- Very generous free tier (1M events/month)
- Much cheaper than Amplitude for small scale
- Can be supplement to GA4 (not replacement)

---

### 12. PHONEPE + CASHFREE PAYMENT GATEWAYS

**Use Case:** Campaign donations, payments

#### PhonePe Pricing Model
- Standard Plan: **FREE** (0% processing fee for UPI bank-to-bank)
- Wallet UPI (>₹2,000): 1.1% interchange fee
- Enterprise Plan: Custom pricing

#### Cashfree Pricing Model
- Special offer: 1.6% for 12 months (Sep-Dec 2025 signups)
- Standard: 1.95%
- UPI credit cards: 2.15%
- No setup/maintenance fees

#### Usage Assumptions
| User Tier | Donations/Month | Avg Donation | Total Amount | Payment Mix |
|-----------|-----------------|--------------|--------------|-------------|
| Small (1K) | 50 | ₹500 ($6) | ₹25,000 ($300) | 80% UPI, 20% cards |
| Medium (10K) | 500 | ₹500 | ₹250,000 ($3,000) | 80% UPI, 20% cards |
| Large (100K) | 5,000 | ₹500 | ₹2,500,000 ($30,000) | 80% UPI, 20% cards |
| Scale (1M) | 50,000 | ₹500 | ₹25,000,000 ($300,000) | 80% UPI, 20% cards |

#### Cost Estimates
| Tier | UPI (Free) | Cards (2% fee) | **Monthly Total** |
|------|------------|----------------|-------------------|
| Small | ₹20,000 ($240) free | ₹5,000 × 2% = ₹100 ($1.20) | **$1.20** |
| Medium | ₹200,000 ($2,400) free | ₹50,000 × 2% = ₹1,000 ($12) | **$12** |
| Large | ₹2,000,000 ($24,000) free | ₹500,000 × 2% = ₹10,000 ($120) | **$120** |
| Scale | ₹20,000,000 ($240,000) free | ₹5,000,000 × 2% = ₹100,000 ($1,200) | **$1,200** |

**Notes:**
- PhonePe is FREE for UPI bank-to-bank (majority of Indian payments)
- Only pay fees on card payments (~20% of volume)
- Much cheaper than international gateways (Stripe: 4.3%+)
- Transaction fees are typically passed to donor (optional)

**Optimization Tips:**
- Promote UPI payments (0% fee vs 2% for cards)
- Set minimum donation amounts to reduce fixed costs
- Consider passing fees to donors (transparent pricing)

---

### 13. EXOTEL VOICE API

**Use Case:** Voice campaigns, automated calls, IVR

#### Pricing Model (India)
- Basic: ₹9,999 (₹5,000 usage + ₹4,999 rental, 6 months, 3 agents)
- Mid-tier: ₹19,999/year (₹9,500 usage + ₹10,499 rental, 6 agents)
- Premium: ₹49,999/year (₹39,500 usage + ₹10,499 rental, unlimited agents)

#### Usage Assumptions
| User Tier | Calls/Month | Minutes/Call | Total Minutes |
|-----------|-------------|--------------|---------------|
| Small (1K) | 500 | 2 | 1,000 |
| Medium (10K) | 5,000 | 2 | 10,000 |
| Large (100K) | 50,000 | 2 | 100,000 |
| Scale (1M) | 500,000 | 2 | 1,000,000 |

#### Cost Estimates
| Tier | Plan | **Monthly Total** |
|------|------|-------------------|
| Development | Basic (₹9,999/6mo) | **$20** (~₹1,666/month) |
| Small | Basic | **$20/month** |
| Medium | Mid-tier (₹19,999/year) | **$20/month** |
| Large | Premium (₹49,999/year) | **$50/month** |
| Scale | Custom pricing | **$500/month** (estimated) |

**Notes:**
- Rental fees included in plans
- IVR and call recording included
- Virtual numbers included
- Usage credit renews annually

**Optimization Tips:**
- Use IVR to reduce live agent time
- Schedule calls during off-peak hours (may get better rates)
- Record calls for training (included)

---

### 14. INDIA CENSUS API & DATA.GOV.IN

**Use Case:** Demographics data, constituency profiles

#### Pricing Model
- **COMPLETELY FREE**
- Open Government Data initiative
- No rate limits (reasonable use)

#### Cost Estimates
| All Tiers | **Monthly Total** |
|-----------|-------------------|
| **FREE** | **$0** |

**Notes:**
- 100% free government data
- One-time data import (no ongoing API costs)
- Digital Census 2025 will provide updated data

**Optimization Tips:**
- Import data once, store locally
- Update quarterly or when new census data released

---

## CONSOLIDATED COST SUMMARY

### Development Phase (0-100 users)
| API Category | Monthly Cost |
|--------------|--------------|
| Google Maps | $0 (free tier) |
| Weather (Visual Crossing) | $0 (free tier) |
| SMS (MSG91) | $0 (startup credits) |
| Email (AWS SES) | $0 (free tier) |
| Images (Cloudinary) | $0 (free tier) |
| Storage (S3) | $0 |
| Social Media | $0 (free) |
| Sentiment Analysis | $0 (free tiers) |
| News (GNews) | $0 (free tier) |
| Analytics (GA4 + Mixpanel) | $0 (free) |
| Payments | $0 (no volume) |
| Voice | $0 (no usage) |
| Demographics | $0 (free) |
| **TOTAL** | **$0-50** |

---

### Small Production (1,000 users)
| API Category | Monthly Cost | Priority |
|--------------|--------------|----------|
| Google Maps | $0 (within free tier) | Must-Have |
| Weather | $0 | Should-Have |
| SMS (MSG91) | $12 | Must-Have |
| Email (AWS SES) | $1 | Must-Have |
| Images (Cloudinary) | $0 | Must-Have |
| Storage (S3) | $2 | Must-Have |
| Social Media | $0 | Must-Have |
| Sentiment Analysis | $0 | Should-Have |
| News | $10 | Should-Have |
| Analytics | $0 | Must-Have |
| Payments | $1 (transaction fees) | Should-Have |
| Voice | $20 | Nice-to-Have |
| Demographics | $0 | Nice-to-Have |
| **TOTAL** | **$50-75** | |

---

### Medium Production (10,000 users)
| API Category | Monthly Cost | Priority |
|--------------|--------------|----------|
| Google Maps | $160 | Must-Have |
| Weather | $35 | Should-Have |
| SMS (MSG91) | $120 | Must-Have |
| Email (AWS SES) | $10 | Must-Have |
| Images (Cloudinary) | $0 (near limit, may need Plus @ $89) | Must-Have |
| Storage (S3) | $15 | Must-Have |
| Social Media | $0 | Must-Have |
| Sentiment Analysis | $10 | Should-Have |
| News | $30 | Should-Have |
| Analytics | $0 | Must-Have |
| Payments | $12 (transaction fees) | Should-Have |
| Voice | $20 | Nice-to-Have |
| Demographics | $0 | Nice-to-Have |
| **TOTAL** | **$410-565** | |

**Breakdown:**
- Must-Have: ~$305
- Should-Have: +$87 = ~$392
- Nice-to-Have: +$20 = ~$412
- With optimizations and caching: **$350-450/month**

---

### Large Production (100,000 users)
| API Category | Monthly Cost | Priority |
|--------------|--------------|----------|
| Google Maps | $1,050 | Must-Have |
| Weather | $35 | Should-Have |
| SMS (MSG91) | $1,000 | Must-Have |
| Email (AWS SES) | $100 | Must-Have |
| Images (Cloudinary) | $89 (Plus plan) | Must-Have |
| Storage (S3) | $62 | Must-Have |
| Social Media | $0 | Must-Have |
| Sentiment Analysis | $110 | Should-Have |
| News | $80 | Should-Have |
| Analytics (GA4) | $0 | Must-Have |
| Mixpanel | $17 | Should-Have |
| Payments | $120 (transaction fees) | Should-Have |
| Voice | $50 | Nice-to-Have |
| Demographics | $0 | Nice-to-Have |
| **TOTAL** | **$2,713-3,040** | |

**Breakdown:**
- Must-Have: ~$2,301
- Should-Have: +$357 = ~$2,658
- Nice-to-Have: +$50 = ~$2,708
- With volume discounts: **$2,200-2,500/month**

---

### Scale Production (1,000,000 users)
| API Category | Monthly Cost | Notes |
|--------------|--------------|-------|
| Google Maps | $6,280 | Volume discounts applied |
| Weather | $35 | Unlimited plan |
| SMS (MSG91) | $10,000 | Bulk rate |
| Email (AWS SES) | $1,000 | Still cheapest |
| Images (Cloudinary) | $300 | Advanced plan+ |
| Storage (S3) | $288 | With lifecycle policies |
| Social Media | $0 | Still free |
| Sentiment Analysis | $550 | Enterprise tier |
| News | $200 | Higher volume |
| Analytics (GA4) | $4,167 | GA360 required |
| Mixpanel | $500 | Enterprise |
| Payments | $1,200 | Transaction fees |
| Voice | $500 | Custom pricing |
| Demographics | $0 | Free |
| **TOTAL** | **$25,020** | |

**With Optimizations:**
- Aggressive caching: -30% = **$17,514**
- Volume negotiations: -20% = **$14,011**
- **Realistic: $12,000-15,000/month**

---

## COST OPTIMIZATION STRATEGIES

### 1. Caching Strategy
**Potential Savings: 50-70%**

| API | Cache Duration | Expected Savings |
|-----|----------------|------------------|
| Google Maps (Geocoding) | 30 days | 90% reduction |
| Weather | 15 minutes | 95% reduction |
| News | 1 hour | 90% reduction |
| Social Media | 1 hour | 80% reduction |
| Demographics | 90 days | 99% reduction |

**Implementation:**
- Use Redis for caching
- Set appropriate TTLs
- Implement cache warming for popular queries

### 2. Request Batching
**Potential Savings: 20-40%**

- Batch sentiment analysis (process multiple texts in one request)
- Batch geocoding (process multiple addresses together)
- Combine API calls where possible

### 3. Volume Discounts
**Potential Savings: 20-80%**

| API | Volume Threshold | Discount |
|-----|------------------|----------|
| Google Maps | 5M+ requests | 20-80% |
| MSG91 | 1M+ SMS | 15-20% |
| Custom negotiation | All APIs | 10-30% |

**Strategy:**
- Reach out to API providers at 50% of volume threshold
- Negotiate annual contracts for better rates
- Commit to volume for discounts

### 4. Hybrid Approaches
**Potential Savings: 30-60%**

- Use free APIs where possible (Facebook, Instagram, Census)
- Use cheapest API for each use case (AWS SES vs Postmark)
- Mix free tiers with paid tiers strategically

### 5. Smart Feature Flags
**Potential Savings: 20-40%**

- Disable expensive features for free tier users
- Enable premium features only for paying customers
- A/B test expensive features to justify ROI

### 6. Efficient Data Fetching
**Potential Savings: 30-50%**

- Request only needed fields (Google Maps: partial responses)
- Implement pagination (don't fetch all data at once)
- Use webhooks instead of polling

---

## BILLING ALERTS & MONITORING

### Set Up Billing Alerts

**Google Cloud Platform:**
- Set budget alerts at 50%, 75%, 90%, 100%
- Alert email: team@pulseofpeople.com
- Recommended budget: 120% of expected usage

**AWS:**
- CloudWatch billing alerts
- Set alerts at: $50, $100, $250, $500
- Enable Cost Explorer

**Other APIs:**
- Monitor usage dashboards daily
- Set up email alerts for approaching limits
- Review costs weekly during development, monthly in production

### Cost Tracking Dashboard

**Create Google Sheet or Airtable:**
- Columns: API Name, Expected Cost, Actual Cost, Date, Notes
- Update weekly
- Flag anything >10% over budget
- Review monthly in team meeting

---

## PAYMENT METHODS & BILLING

### Recommended Setup

**Credit Card for API Payments:**
- Use business credit card with high limit
- Separate from personal expenses
- Enable email alerts for all charges
- Review statement weekly

**Prepaid vs Postpaid:**
- Use postpaid for AWS, Google Cloud (better for scaling)
- Use prepaid for Indian SMS providers if available (budget control)

### Tax Considerations

**Indian GST:**
- 18% GST on most Indian API services
- Factor into budget (costs shown may not include GST)
- Keep invoices for tax purposes

**International Payments:**
- Some providers charge in USD (AWS, Google)
- Currency conversion fees may apply
- Use Wise or similar for better rates

---

## ROI CALCULATIONS

### Cost Per User

| User Tier | Monthly API Cost | Active Users | Cost Per User |
|-----------|------------------|--------------|---------------|
| Small | $75 | 1,000 | **$0.075** (7.5 cents) |
| Medium | $450 | 10,000 | **$0.045** (4.5 cents) |
| Large | $2,500 | 100,000 | **$0.025** (2.5 cents) |
| Scale | $12,000 | 1,000,000 | **$0.012** (1.2 cents) |

**Key Insight:** Cost per user DECREASES as you scale (economies of scale)

### Break-Even Analysis

**If charging $5/month per user:**
| Tier | Users | Revenue | API Costs | Profit Margin |
|------|-------|---------|-----------|---------------|
| Small | 1,000 | $5,000 | $75 | 98.5% |
| Medium | 10,000 | $50,000 | $450 | 99.1% |
| Large | 100,000 | $500,000 | $2,500 | 99.5% |

**Key Insight:** API costs are a TINY fraction of revenue (even at $5/user/month)

---

## BUDGET RECOMMENDATIONS

### Year 1 Budget (Conservative)

| Quarter | Expected Users | API Budget | Buffer (20%) | **Total** |
|---------|----------------|------------|--------------|-----------|
| Q1 | 1,000 | $900 | $180 | **$1,080** |
| Q2 | 5,000 | $2,400 | $480 | **$2,880** |
| Q3 | 15,000 | $6,000 | $1,200 | **$7,200** |
| Q4 | 30,000 | $9,000 | $1,800 | **$10,800** |
| **Year 1 Total** | | **$18,300** | **$3,660** | **$21,960** |

**Monthly Average:** $1,830 + buffer

### Year 2 Budget (Growth Scenario)

| Quarter | Expected Users | API Budget | Buffer (15%) | **Total** |
|---------|----------------|------------|--------------|-----------|
| Q1 | 50,000 | $15,000 | $2,250 | **$17,250** |
| Q2 | 100,000 | $30,000 | $4,500 | **$34,500** |
| Q3 | 200,000 | $50,000 | $7,500 | **$57,500** |
| Q4 | 350,000 | $70,000 | $10,500 | **$80,500** |
| **Year 2 Total** | | **$165,000** | **$24,750** | **$189,750** |

**Monthly Average:** $15,813

---

## APPENDIX: Cost Calculator

### DIY Cost Estimator

**Input Your Expected Usage:**

```
Number of active users: _________
Average map loads per user: _______ (default: 10)
Average SMS per user: _______ (default: 5)
Average emails per user: _______ (default: 10)
Average storage per user (MB): _______ (default: 10)

Estimated Monthly Cost:
- Google Maps: (users × map_loads × $0.001) = $_______
- SMS: (users × sms × $0.0024) = $_______
- Email: (users × emails × $0.0001) = $_______
- Storage: (users × storage_mb / 1000 × $0.025) = $_______

TOTAL: $_______
```

**Online Calculator:** (Can build a simple web tool for this)

---

**Document End**

*Last Updated: November 9, 2025*
*Next Review: Monthly during Year 1*
*Version: 1.0*

**Note:** All costs are estimates based on 2025 pricing and may change. Always verify current pricing on official provider websites. Currency conversion rates: 1 USD ≈ ₹83 INR (Nov 2025).
