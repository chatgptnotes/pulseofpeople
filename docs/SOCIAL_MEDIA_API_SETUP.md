# Social Media API Setup Guide
## TVK Pulse of People Platform

**Last Updated**: November 8, 2024
**Version**: 1.0
**Approach**: Hybrid (Real data for TVK accounts + Estimated aggregated data)

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Facebook & Instagram Setup](#facebook--instagram-setup)
4. [Twitter/X API Setup](#twitterx-api-setup)
5. [YouTube Data API Setup](#youtube-data-api-setup)
6. [Environment Configuration](#environment-configuration)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)
9. [Rate Limits & Costs](#rate-limits--costs)

---

## 🎯 Overview

The Social Media Monitoring Dashboard uses a **hybrid approach**:

### ✅ Real Data (via APIs)
- **TVK's Official Accounts**: Facebook, Instagram, Twitter/X, YouTube
- Direct API integration for authentic metrics
- Live posts, engagement, follower counts

###  Estimated Data (Aggregated)
- **Mentions & Trends**: WhatsApp, Telegram, LinkedIn, TikTok
- Algorithm-based estimates for platforms without API access
- Realistic projections based on platform behavior

---

## ⚙️ Prerequisites

Before starting, ensure you have:

- [ ] Admin access to TVK's social media accounts
- [ ] Basic understanding of API keys and tokens
- [ ] Access to a computer with internet connection
- [ ] Email address for developer account registration

**Time Required**: Approximately 2-3 hours for full setup

---

## 📘 Facebook & Instagram Setup

### Step 1: Create Meta Developer Account

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Click **"Get Started"** in the top right
3. Log in with your Facebook account (use TVK admin account)
4. Complete the registration form
5. Verify your email address

### Step 2: Create a Facebook App

1. From the [Meta Apps Dashboard](https://developers.facebook.com/apps/), click **"Create App"**
2. Select **"Business"** as the app type
3. Fill in app details:
   - **App Name**: `TVK Social Media Monitor`
   - **Contact Email**: your email
   - **Business Account**: Select TVK business account
4. Click **"Create App"**

### Step 3: Get Facebook Page Access Token

1. In your app dashboard, go to **Settings → Basic**
2. Note down your **App ID** and **App Secret** (keep secure!)
3. In the left sidebar, click **"Add Product"**
4. Find **"Facebook Login"** and click **"Set Up"**
5. Go to **Tools → Graph API Explorer**
6. In the Graph API Explorer:
   - Select your app from the dropdown
   - Click **"Generate Access Token"**
   - Grant permissions: `pages_read_engagement`, `pages_read_user_content`, `pages_show_list`
   - Copy the generated access token

### Step 4: Get Your Facebook Page ID

1. Go to your TVK Facebook Page
2. Click **"About"** in the left menu
3. Scroll down to find **"Page ID"** or **"Page Transparency"**
4. Copy the numeric ID (e.g., `123456789012345`)

**Alternative method:**
```bash
# Visit this URL (replace YOUR_PAGE_USERNAME):
https://findmyfbid.in/
```

### Step 5: Make Token Long-Lived

Short-lived tokens expire in 1 hour. Convert to long-lived (60 days):

```bash
https://graph.facebook.com/v18.0/oauth/access_token?
  grant_type=fb_exchange_token&
  client_id=YOUR_APP_ID&
  client_secret=YOUR_APP_SECRET&
  fb_exchange_token=YOUR_SHORT_LIVED_TOKEN
```

Copy the `access_token` from the response.

### Step 6: Instagram Business Account Setup

1. Ensure your Instagram account is a **Business Account**
2. Link it to your Facebook Page (Instagram → Settings → Account → Linked Accounts)
3. In Graph API Explorer:
   - Use the URL: `/{YOUR_FACEBOOK_PAGE_ID}?fields=instagram_business_account`
   - Run the query
   - Copy the `instagram_business_account.id`

### ✅ Facebook & Instagram Complete!

You should now have:
- ✅ Facebook Page ID
- ✅ Facebook Access Token (long-lived)
- ✅ Instagram Business Account ID
- ✅ Instagram Access Token (same as Facebook token)

---

## 🐦 Twitter/X API Setup

### Step 1: Create Twitter Developer Account

1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Click **"Sign up"** (or **"Sign in"** if you have an account)
3. Log in with TVK's Twitter account
4. Apply for **Developer Access**:
   - Select **"Hobbyist"** → **"Exploring the API"** (FREE tier)
   - Fill out the application form
   - Describe use case: *"Social media monitoring for political party official accounts"*
   - Agree to Terms of Service
5. Verify your email
6. Wait for approval (usually instant, max 48 hours)

### Step 2: Create a Project and App

1. In the Developer Portal, click **"Projects & Apps"**
2. Click **"+ Create Project"**
3. Fill in:
   - **Project Name**: `TVK Social Monitor`
   - **Use Case**: Select appropriate option
   - **Project Description**: Brief description
4. Click **"Create"**
5. Create an App within the project:
   - **App Name**: `tvk-pulse-monitor`
   - **Environment**: Select **"Development"** or **"Production"**

### Step 3: Get API Credentials

1. After creating the app, you'll see:
   - **API Key**
   - **API Key Secret**
   - **Bearer Token**
2. **IMPORTANT**: Copy the **Bearer Token** immediately (shown only once!)
3. Store securely in a password manager

### Step 4: Get Your Twitter Account ID

**Method 1: Using Twitter API**
```bash
curl -X GET "https://api.twitter.com/2/users/by/username/YOUR_TWITTER_HANDLE" \
  -H "Authorization: Bearer YOUR_BEARER_TOKEN"
```

**Method 2: Using Online Tool**
- Visit: https://tweeterid.com/
- Enter TVK's Twitter handle
- Copy the numeric ID

### Step 5: Set App Permissions

1. In your app settings, go to **"Settings"**
2. Under **"User authentication settings"**, click **"Set up"**
3. Enable **"OAuth 2.0"**
4. Set **"Type of App"**: **Read-only**
5. Add Callback URL: `http://localhost:5173/callback` (for development)
6. Save changes

### ✅ Twitter/X Complete!

You should now have:
- ✅ Twitter Account ID
- ✅ Bearer Token

---

## 🎥 YouTube Data API Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Click **"Select a project"** → **"NEW PROJECT"**
4. Fill in:
   - **Project Name**: `TVK Social Media Monitor`
   - **Organization**: Leave as default or select your org
5. Click **"CREATE"**

### Step 2: Enable YouTube Data API v3

1. In the Google Cloud Console, go to **"APIs & Services" → "Library"**
2. Search for **"YouTube Data API v3"**
3. Click on it
4. Click **"ENABLE"**
5. Wait for activation (10-30 seconds)

### Step 3: Create API Credentials

1. Go to **"APIs & Services" → "Credentials"**
2. Click **"+ CREATE CREDENTIALS"**
3. Select **"API key"**
4. Copy the generated API key immediately
5. Click **"RESTRICT KEY"** (recommended)
6. Under **"API restrictions"**:
   - Select **"Restrict key"**
   - Choose **"YouTube Data API v3"**
7. Under **"Application restrictions"** (optional):
   - Select **"HTTP referrers (web sites)"**
   - Add: `localhost:5173/*` and your production domain
8. Click **"SAVE"**

### Step 4: Get Your YouTube Channel ID

**Method 1: From YouTube Studio**
1. Go to [YouTube Studio](https://studio.youtube.com/)
2. Click your profile icon → **"Settings"**
3. Go to **"Channel" → "Advanced settings"**
4. Copy your **Channel ID** (starts with `UC...`)

**Method 2: From Channel URL**
- If your URL is `youtube.com/channel/UC1234...`, the part after `/channel/` is your Channel ID
- If your URL is `youtube.com/@YourHandle`, use Method 1 or 3

**Method 3: Using YouTube Data API**
```bash
curl "https://www.googleapis.com/youtube/v3/channels?part=id&forUsername=YOUR_CHANNEL_NAME&key=YOUR_API_KEY"
```

### Step 5: Test the API

Visit this URL in your browser (replace with your credentials):
```
https://www.googleapis.com/youtube/v3/channels?part=statistics&id=YOUR_CHANNEL_ID&key=YOUR_API_KEY
```

You should see JSON with subscriber count, view count, etc.

### ✅ YouTube Complete!

You should now have:
- ✅ YouTube Channel ID
- ✅ YouTube API Key

---

## 🔧 Environment Configuration

### Step 1: Create .env File

Navigate to your project's `frontend/` folder:

```bash
cd frontend
cp .env.example .env
```

### Step 2: Add Your Credentials

Open `.env` in a text editor and fill in:

```env
# Facebook
VITE_FACEBOOK_PAGE_ID=123456789012345
VITE_FACEBOOK_ACCESS_TOKEN=EAABsbCS1...your-long-token...ZD

# Instagram
VITE_INSTAGRAM_ACCOUNT_ID=987654321098765
VITE_INSTAGRAM_ACCESS_TOKEN=EAABsbCS1...same-as-facebook...ZD

# Twitter/X
VITE_TWITTER_ACCOUNT_ID=1234567890
VITE_TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAABear...erToken...AAAA

# YouTube
VITE_YOUTUBE_CHANNEL_ID=UC1234567890abcdefgh
VITE_YOUTUBE_API_KEY=AIzaSyABC...your-api-key...XYZ
```

### Step 3: Restart Development Server

```bash
# Stop the current server (Ctrl+C)
# Start it again
npm run dev
```

---

## 🧪 Testing

### Test Individual APIs

Open your browser's Developer Console and run:

```javascript
// Test Facebook
import socialMediaAPI from './src/services/socialMediaAPI';

// Check if configured
console.log('Facebook configured:', socialMediaAPI.isAPIConfigured('facebook'));

// Fetch data
const fbMetrics = await socialMediaAPI.fetchFacebookMetrics();
console.log('Facebook Metrics:', fbMetrics);

const fbPosts = await socialMediaAPI.fetchFacebookPosts(5);
console.log('Facebook Posts:', fbPosts);
```

### Expected Results

✅ **Success**: You see real data from your accounts
❌ **Error**: Check troubleshooting section below

---

## 🔥 Troubleshooting

### Common Issues

#### 1. "Invalid Access Token" (Facebook/Instagram)

**Cause**: Token expired or incorrect
**Fix**:
- Regenerate token following Step 3 of Facebook setup
- Ensure you're using a long-lived token
- Check for extra spaces when copying token

#### 2. "Rate Limit Exceeded" (Any API)

**Cause**: Too many requests
**Fix**:
- Wait 15 minutes before trying again
- Reduce polling frequency in code
- Consider caching data

#### 3. "Permission Denied" (Facebook/Instagram)

**Cause**: Missing required permissions
**Fix**:
- In Graph API Explorer, add permissions: `pages_read_engagement`, `pages_read_user_content`
- Regenerate access token

#### 4. "Channel Not Found" (YouTube)

**Cause**: Incorrect Channel ID
**Fix**:
- Double-check Channel ID format (should start with `UC`)
- Ensure you're using Channel ID, not User ID or Handle

#### 5. "CORS Error" (Any API)

**Cause**: Direct API calls from browser blocked
**Solution**: Already handled! Our service layer makes requests correctly.

### Debug Mode

Enable debug logging:

```typescript
// In src/services/socialMediaAPI.ts, add to each function:
console.log('Fetching data from:', platform);
console.log('Using credentials:', { configured: isAPIConfigured(platform) });
```

---

## 💰 Rate Limits & Costs

### Facebook & Instagram (Meta Graph API)

- **Free Tier**: 200 requests/hour per user
- **Cost**: FREE for basic usage
- **Limits**:
  - Page access: 200 calls/hour
  - Instagram: 200 calls/hour
- **Upgrade**: Contact Meta for higher limits

### Twitter/X API

| Tier | Cost | Limits |
|------|------|--------|
| Free | $0/month | 1,500 tweets/month, 500,000 tweets read/month |
| Basic | $100/month | 3,000 tweets/month, 10,000 tweets read/month |
| Pro | $5,000/month | Unlimited |

**Recommendation**: Start with FREE tier for testing

### YouTube Data API

- **Free Tier**: 10,000 units/day
- **Cost**: FREE up to quota
- **Typical Usage**:
  - Channel stats: 3 units
  - Video list: 100 units
  - Video details: 1 unit each
- **Overage**: $0.002 per unit above quota

**Daily Estimate**: 200-500 units (well within free limit)

### Total Monthly Cost

| Scenario | Facebook | Instagram | Twitter | YouTube | **Total** |
|----------|----------|-----------|---------|---------|-----------|
| Testing | FREE | FREE | FREE | FREE | **$0** |
| Light Use | FREE | FREE | FREE | FREE | **$0** |
| Heavy Use | FREE | FREE | $100 | FREE | **$100** |

---

## 📞 Support & Resources

### Official Documentation

- [Meta Graph API Docs](https://developers.facebook.com/docs/graph-api/)
- [Twitter API v2 Docs](https://developer.twitter.com/en/docs/twitter-api)
- [YouTube Data API Docs](https://developers.google.com/youtube/v3)

### Community Help

- Meta Developer Community: https://developers.facebook.com/community/
- Twitter Developer Forums: https://twittercommunity.com/
- Stack Overflow: Tag questions with `facebook-graph-api`, `twitter-api`, `youtube-api`

### TVK Platform Support

For platform-specific issues:
- Email: tech@tvk.org
- Internal Slack: #social-media-tech

---

## 🔒 Security Best Practices

1. **Never commit API keys to Git**
   - `.env` file is already in `.gitignore`
   - Use environment variables only

2. **Rotate credentials regularly**
   - Facebook: Every 60 days (token expiry)
   - Twitter: Every 90 days (recommended)
   - YouTube: Annually

3. **Use read-only permissions**
   - Only request permissions you need
   - Never use write permissions unless necessary

4. **Monitor usage**
   - Check API dashboards monthly
   - Set up alerts for unusual activity

5. **Restrict API keys**
   - Add domain restrictions
   - Use referrer restrictions where possible

---

## ✅ Setup Checklist

Before going live, verify:

- [ ] All API credentials added to `.env`
- [ ] `.env` file NOT committed to Git
- [ ] Each API tested successfully
- [ ] Rate limits understood
- [ ] Error handling implemented
- [ ] Data refresh frequency configured
- [ ] Security best practices followed
- [ ] Backup credentials stored securely
- [ ] Team trained on maintenance

---

**Congratulations!** 🎉

Your social media monitoring is now live with real data from TVK's official accounts!

For questions or issues, refer to the [Troubleshooting](#troubleshooting) section or contact the tech team.

---

**Document Version**: 1.0
**Last Reviewed**: November 8, 2024
**Next Review**: December 8, 2024
