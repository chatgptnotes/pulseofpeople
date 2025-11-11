# API Quick Reference Guide - Pulse of People
**Version:** 1.0
**Date:** November 9, 2025

## Quick Start Checklist

Use this guide to quickly set up all recommended APIs for the Pulse of People platform.

---

## MUST-HAVE APIs (Week 1-4)

### 1. Google Maps API
**Why:** Polling booth mapping (core feature)
**Cost:** $160-1,050/month (depending on usage)
**Setup Time:** 1 hour

**Quick Setup:**
1. Go to: https://console.cloud.google.com/
2. Create new project: "PulseOfPeople"
3. Enable APIs:
   - Maps JavaScript API
   - Geocoding API
   - Places API
   - Directions API
4. Create API key → Restrict to your domains
5. Enable billing (required for production)
6. Add to `.env`: `GOOGLE_MAPS_API_KEY=your-key-here`

**Free Tier:** $200 credit/month (~40K map loads)

---

### 2. MSG91 SMS API
**Why:** Voter reminders, OTP verification
**Cost:** $12-1,000/month (₹0.17-0.20 per SMS)
**Setup Time:** 30 minutes

**Quick Setup:**
1. Go to: https://msg91.com/
2. Sign up with business details
3. Complete KYC verification
4. Register DLT templates (required for India)
   - Go to DLT portal: https://www.vilpower.in/
   - Register your company
   - Create SMS templates
5. Get AUTH_KEY from dashboard
6. Add to `.env`:
   ```
   MSG91_AUTH_KEY=your-auth-key
   MSG91_SENDER_ID=POPINDIA
   MSG91_DLT_ENTITY_ID=your-dlt-id
   MSG91_DLT_TEMPLATE_ID=your-template-id
   ```

**Free Tier:** 25,000 free credits (startup offer)

---

### 3. AWS SES (Email)
**Why:** Campaign emails, transactional emails
**Cost:** $10-100/month ($0.10 per 1,000 emails)
**Setup Time:** 1 hour

**Quick Setup:**
1. Go to: https://aws.amazon.com/ses/
2. Create AWS account (if needed)
3. Choose India region: ap-south-1 (Mumbai)
4. Verify domain or email address
5. Request production access (fills form, takes 24-48 hours)
6. Create IAM user with SES permissions
7. Generate access keys
8. Add to `.env`:
   ```
   AWS_ACCESS_KEY_ID=your-access-key
   AWS_SECRET_ACCESS_KEY=your-secret-key
   AWS_SES_REGION_NAME=ap-south-1
   ```

**Free Tier:** 3,000 emails/month (62,000 if hosted on EC2)

---

### 4. Cloudinary (Images)
**Why:** User photos, campaign media
**Cost:** $0-89/month (free tier: 25GB)
**Setup Time:** 15 minutes

**Quick Setup:**
1. Go to: https://cloudinary.com/
2. Sign up (free account)
3. Go to Dashboard
4. Copy: Cloud Name, API Key, API Secret
5. Add to `.env`:
   ```
   CLOUDINARY_CLOUD_NAME=your-cloud-name
   CLOUDINARY_API_KEY=your-api-key
   CLOUDINARY_API_SECRET=your-api-secret
   ```

**Free Tier:** 25GB storage, transformations, CDN included

---

### 5. Google Analytics 4
**Why:** Track user behavior, funnel analysis
**Cost:** FREE
**Setup Time:** 30 minutes

**Quick Setup:**
1. Go to: https://analytics.google.com/
2. Create account: "Pulse of People"
3. Create GA4 property
4. Copy Measurement ID (G-XXXXXXXXXX)
5. Add to `frontend/.env`:
   ```
   VITE_GA4_MEASUREMENT_ID=G-XXXXXXXXXX
   ```
6. Install `react-ga4` in frontend
7. Initialize in app

**Free Tier:** 10M events/month (sufficient for 100K users)

---

### 6. Facebook & Instagram Graph APIs
**Why:** Social media sentiment tracking
**Cost:** FREE
**Setup Time:** 1 hour

**Quick Setup:**
1. Go to: https://developers.facebook.com/
2. Create app → Select "Business"
3. Add Facebook Login product
4. Get App ID and App Secret
5. Create Facebook Business Page
6. Connect Instagram Business Account
7. Generate Page Access Token (Graph API Explorer)
8. Add to `.env`:
   ```
   FACEBOOK_APP_ID=your-app-id
   FACEBOOK_APP_SECRET=your-app-secret
   FACEBOOK_ACCESS_TOKEN=your-page-token
   INSTAGRAM_BUSINESS_ACCOUNT_ID=your-ig-id
   ```

**Free Tier:** Completely free (rate limits sufficient)

---

## SHOULD-HAVE APIs (Week 5-6)

### 7. Visual Crossing Weather API
**Why:** Campaign planning, event scheduling
**Cost:** $0-35/month (unlimited)
**Setup Time:** 15 minutes

**Quick Setup:**
1. Go to: https://www.visualcrossing.com/
2. Sign up for free account
3. Get API key from account page
4. Add to `.env`:
   ```
   VISUAL_CROSSING_API_KEY=your-api-key
   ```

**Free Tier:** 1,000 requests/day (30K/month)

---

### 8. HuggingFace + Azure Text Analytics
**Why:** Sentiment analysis (English + Hindi)
**Cost:** $10-110/month
**Setup Time:** 1 hour

**HuggingFace Setup:**
1. Go to: https://huggingface.co/
2. Sign up
3. Settings → Access Tokens → Create token
4. Add to `.env`:
   ```
   HUGGINGFACE_API_TOKEN=your-token
   ```

**Azure Setup (for Hindi):**
1. Go to: https://portal.azure.com/
2. Create "Text Analytics" resource
3. Choose region: Southeast Asia
4. Get endpoint and key
5. Add to `.env`:
   ```
   AZURE_TEXT_ANALYTICS_ENDPOINT=your-endpoint
   AZURE_TEXT_ANALYTICS_KEY=your-key
   ```

**Free Tier:** HuggingFace generous, Azure 5K records/month

---

### 9. GNews API
**Why:** Political news aggregation
**Cost:** $30-80/month
**Setup Time:** 15 minutes

**Quick Setup:**
1. Go to: https://gnews.io/
2. Sign up
3. Get API key
4. Add to `.env`:
   ```
   GNEWS_API_KEY=your-api-key
   ```

**Free Tier:** Development tier available

---

### 10. PhonePe + Cashfree (Payments)
**Why:** Campaign donations
**Cost:** 0-2% transaction fees
**Setup Time:** 2 hours (includes KYC)

**PhonePe Setup:**
1. Go to: https://www.phonepe.com/business/
2. Sign up as merchant
3. Complete KYC (business documents required)
4. Get Merchant ID and Salt Key
5. Add to `.env`:
   ```
   PHONEPE_MERCHANT_ID=your-merchant-id
   PHONEPE_SALT_KEY=your-salt-key
   PHONEPE_ENV=sandbox
   ```

**Cashfree Setup:**
1. Go to: https://www.cashfree.com/
2. Sign up
3. Complete KYC
4. Get App ID and Secret Key
5. Add to `.env`:
   ```
   CASHFREE_APP_ID=your-app-id
   CASHFREE_SECRET_KEY=your-secret-key
   ```

**Free Tier:** PhonePe is FREE for UPI transactions

---

### 11. Mixpanel
**Why:** Advanced user analytics
**Cost:** FREE
**Setup Time:** 30 minutes

**Quick Setup:**
1. Go to: https://mixpanel.com/
2. Sign up
3. Create project
4. Get Project Token
5. Add to `.env`:
   ```
   MIXPANEL_TOKEN=your-project-token
   ```
6. Install `mixpanel-browser` in frontend

**Free Tier:** 1M events/month

---

### 12. AWS S3 (Documents)
**Why:** Document storage
**Cost:** $2-62/month
**Setup Time:** 30 minutes

**Quick Setup:**
1. AWS Console → S3
2. Create bucket: "pulseofpeople-documents"
3. Region: ap-south-1 (Mumbai)
4. Block public access: ON
5. Enable versioning
6. Create IAM policy for bucket access
7. Add to `.env`:
   ```
   AWS_S3_BUCKET_NAME=pulseofpeople-documents
   AWS_S3_REGION=ap-south-1
   ```

**Free Tier:** First 5GB free for 12 months

---

## NICE-TO-HAVE APIs (Week 7-8)

### 13. Exotel Voice API
**Why:** Voice campaigns, IVR
**Cost:** $20-50/month
**Setup Time:** 1 hour

**Quick Setup:**
1. Go to: https://exotel.com/
2. Sign up
3. Complete business verification
4. Choose plan (Basic: ₹9,999 for 6 months)
5. Get API Key, Token, SID
6. Add to `.env`:
   ```
   EXOTEL_API_KEY=your-api-key
   EXOTEL_API_TOKEN=your-api-token
   EXOTEL_SID=your-sid
   ```

**Included:** IVR, call recording, virtual numbers

---

### 14. India Census API
**Why:** Demographics data
**Cost:** FREE
**Setup Time:** 30 minutes

**Quick Setup:**
1. Go to: https://censusindia.gov.in/census.website/data/api/documentation
2. Review API documentation
3. No API key required (public data)
4. Add to `.env`:
   ```
   CENSUS_API_BASE_URL=https://censusindia.gov.in/census.website/data/api
   ```

**Free Tier:** Completely free government data

---

## Environment Variables Summary

### Backend (.env)
Copy from `/backend/.env.example` and fill in your actual API keys.

**Required for MVP:**
- `GOOGLE_MAPS_API_KEY`
- `MSG91_AUTH_KEY`
- `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`
- `CLOUDINARY_CLOUD_NAME` + `CLOUDINARY_API_KEY` + `CLOUDINARY_API_SECRET`

**Optional but recommended:**
- `VISUAL_CROSSING_API_KEY`
- `HUGGINGFACE_API_TOKEN`
- `PHONEPE_MERCHANT_ID` + `PHONEPE_SALT_KEY`
- `MIXPANEL_TOKEN`

### Frontend (.env)
Located at: `/frontend/.env`

**Required:**
```
VITE_API_URL=http://127.0.0.1:8000
VITE_GOOGLE_MAPS_API_KEY=your-google-maps-key
VITE_GA4_MEASUREMENT_ID=G-XXXXXXXXXX
VITE_CLOUDINARY_CLOUD_NAME=your-cloudinary-cloud-name
```

---

## Testing APIs

### Quick Test Scripts

**Test SMS:**
```bash
curl -X POST https://api.msg91.com/api/v5/flow/ \
  -H "authkey: YOUR_AUTH_KEY" \
  -H "content-type: application/json" \
  -d '{
    "sender": "POPINDIA",
    "mobiles": "919XXXXXXXXX",
    "message": "Test message from Pulse of People"
  }'
```

**Test Email (AWS SES):**
```python
import boto3

ses = boto3.client('ses', region_name='ap-south-1')
response = ses.send_email(
    Source='noreply@pulseofpeople.com',
    Destination={'ToAddresses': ['test@example.com']},
    Message={
        'Subject': {'Data': 'Test Email'},
        'Body': {'Text': {'Data': 'This is a test email.'}}
    }
)
print(response)
```

**Test Google Maps Geocoding:**
```bash
curl "https://maps.googleapis.com/maps/api/geocode/json?address=Connaught+Place+New+Delhi&key=YOUR_API_KEY"
```

---

## Cost Monitoring

### Set Billing Alerts

**Google Cloud Platform:**
1. Billing → Budgets & alerts
2. Create budget: $200/month
3. Set alerts: 50%, 75%, 90%, 100%

**AWS:**
1. Billing Dashboard → Budgets
2. Create budget: $100/month
3. Set alerts: $50, $75, $90, $100

**Other APIs:**
- Check usage dashboards daily (first week)
- Review costs weekly (first month)
- Set up email alerts for approaching limits

---

## Common Issues & Solutions

### Issue 1: Google Maps API not working
**Solution:**
- Check API key restrictions (HTTP referrers for frontend, IP for backend)
- Verify billing is enabled
- Check API is enabled in Google Cloud Console

### Issue 2: MSG91 SMS delivery failure
**Solution:**
- Verify DLT registration is complete
- Check phone number format (must include country code: +91)
- Ensure sender ID is approved
- Check template matches DLT template exactly

### Issue 3: AWS SES emails going to spam
**Solution:**
- Verify domain with SPF, DKIM records
- Request production access (sandbox mode limited)
- Use verified "From" address
- Implement email authentication (DMARC)

### Issue 4: Payment gateway webhook not receiving
**Solution:**
- Verify webhook URL is publicly accessible
- Check HTTPS is enabled (required)
- Verify webhook signature validation
- Check firewall/security group settings

---

## Next Steps After Setup

1. **Week 1:** Set up all MUST-HAVE APIs (6 APIs)
2. **Week 2-4:** Integrate MUST-HAVE APIs into application
3. **Week 5-6:** Add SHOULD-HAVE APIs (6 APIs)
4. **Week 7-8:** Add NICE-TO-HAVE APIs and optimize

**Total Setup Time (All APIs):** ~15-20 hours
**Total Integration Time:** ~320 hours (as per Integration Plan)

---

## Support Resources

### Official Documentation
- Google Maps: https://developers.google.com/maps
- AWS SES: https://docs.aws.amazon.com/ses/
- MSG91: https://docs.msg91.com/
- Cloudinary: https://cloudinary.com/documentation
- PhonePe: https://developer.phonepe.com/docs
- HuggingFace: https://huggingface.co/docs
- Facebook Graph: https://developers.facebook.com/docs/graph-api

### Community Support
- Stack Overflow: Search "[API name] + your issue"
- GitHub Discussions: Check API official repos
- Discord/Slack: Join developer communities

### Paid Support
- Google Cloud Support: $100-2,500/month
- AWS Support: $100-15,000/month
- Most other APIs: Email support included

---

**Document End**

*Last Updated: November 9, 2025*
*Version: 1.0*
