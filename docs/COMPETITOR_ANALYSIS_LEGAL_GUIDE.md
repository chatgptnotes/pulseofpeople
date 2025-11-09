# Competitor Analysis - Legal Data Collection Guide

## ⚖️ Legal & Compliant Approach to Competitor Social Media Tracking

This document outlines the **LEGAL and RECOMMENDED** methods for tracking competitor social media activity in the Pulse of People platform.

---

## 🚫 What NOT to Do

### ❌ Prohibited Methods

**DO NOT use these methods** - they violate platform Terms of Service and may result in:
- Account termination/bans
- IP address blocking
- Legal action (CFAA violations)
- Platform blacklisting

#### Prohibited Activities:
1. **Web Scraping**: Using automated tools (Puppeteer, Selenium, BeautifulSoup) to extract data
2. **Bot Automation**: Creating bots to collect competitor data
3. **API Abuse**: Exceeding rate limits or using APIs in unauthorized ways
4. **Account Impersonation**: Creating fake accounts to access competitor data
5. **Circumventing Authentication**: Bypassing login walls or access controls

### Platform-Specific Prohibitions:

- **Facebook/Instagram**: "You may not access or collect data from our Products using automated means"
- **Twitter/X**: "You will not... scrape the Twitter Services"
- **YouTube**: "You agree not to... access Content through any technology or means other than... the Service itself"
- **LinkedIn**: "You agree that you will not... use any robot, spider, scraper or other automated means"

---

## ✅ Legal & Recommended Methods

### Method 1: Official Platform APIs (Recommended)

**For TVK's Own Accounts:**
- Facebook Graph API
- Instagram Graph API
- Twitter API v2
- YouTube Data API v3

**What You Can Track:**
- Your own posts, engagement, followers
- Public mentions of your accounts
- Hashtag performance
- Demographic insights

**Cost**: FREE (within generous limits)
**Legal**: ✅ Fully authorized
**Setup**: See `docs/SOCIAL_MEDIA_API_SETUP.md`

---

### Method 2: Third-Party Social Listening Services (Best for Competitor Tracking)

These companies have **official agreements** with social platforms:

#### Recommended Services:

| Service | Monthly Cost | Features | Best For |
|---------|--------------|----------|----------|
| **Brand24** | $49-249 | Brand monitoring, sentiment | Budget-conscious campaigns |
| **Mention** | $99-500 | Multi-platform listening, alerts | Medium campaigns |
| **Hootsuite Insights** | $200-1,000 | Complete social analytics | Large campaigns |
| **Brandwatch** | $800-2,000 | Enterprise-grade intelligence | National campaigns |
| **Sprout Social** | $249-499 | Management + listening | All-in-one solution |

**Why Use These?**
- ✅ Legal access to platform data (authorized by platforms)
- ✅ Track competitors without violating ToS
- ✅ Monitor mentions, sentiment, trends
- ✅ Historical data included
- ✅ No technical maintenance
- ✅ Advanced analytics (AI-powered insights)

**Setup**: See integration guides for each service below

---

### Method 3: Manual Data Entry (Fallback)

For budget-constrained campaigns or initial testing:

**Process:**
1. Visit competitor social media pages manually
2. Record public metrics (followers, post engagement)
3. Enter data into Competitor Registry
4. Update weekly/monthly

**Tools:**
- Pulse of People Competitor Registry (built-in)
- Spreadsheet templates (provided)
- Browser bookmarks for quick access

**Cost**: $0 (time investment only)
**Legal**: ✅ Fully compliant
**Accuracy**: Adequate for trend analysis

---

### Method 4: Public Data Sources

**Freely Available Data:**
- RSS Feeds (where available)
- Public APIs (Reddit, some news sites)
- Official platform embeds
- Press releases
- Public statements

---

## 🔧 Implementation in Pulse of People

### Architecture Overview

```
Competitor Data Collection
├── Primary: Official APIs (TVK's own accounts)
├── Secondary: Third-Party Services (competitor monitoring)
└── Fallback: Manual Data Entry (budget option)
```

### Data Sources by Method:

#### 1. Official APIs (Implemented)
- **File**: `frontend/src/lib/socialMediaAPI.ts`
- **Platforms**: Facebook, Instagram, Twitter, YouTube
- **Usage**: TVK's own account analytics
- **Status**: ✅ Production-ready

#### 2. Third-Party Integrations (Available)
- **Files**:
  - `frontend/src/lib/integrations/mention.ts`
  - `frontend/src/lib/integrations/brand24.ts`
  - `frontend/src/lib/integrations/hootsuite.ts`
- **Platforms**: All major social media
- **Usage**: Competitor tracking, mentions, sentiment
- **Status**: ⚠️ Requires paid subscription

#### 3. Manual Entry (Implemented)
- **Page**: `/competitors/registry`
- **Usage**: Add competitors, update metrics manually
- **Status**: ✅ Available

---

## 📊 What Data You Can Legally Collect

### About Your Own Accounts (Via Official APIs):
✅ Follower counts and growth
✅ Post engagement (likes, comments, shares)
✅ Reach and impressions
✅ Audience demographics
✅ Best posting times
✅ Content performance
✅ Hashtag analytics

### About Competitors (Via Third-Party Services):
✅ Public follower counts
✅ Public post counts
✅ Estimated engagement rates
✅ Public mentions
✅ Sentiment analysis
✅ Topic trends
✅ Share of voice

### What You CANNOT Collect:
❌ Private/protected posts
❌ Private messages/DMs
❌ Account login credentials
❌ Non-public engagement metrics
❌ User personal data without consent

---

## 🚀 Getting Started (Step-by-Step)

### Week 1: Set Up Your Own Account Tracking
1. Follow `docs/SOCIAL_MEDIA_API_SETUP.md`
2. Configure API credentials in `.env`
3. Verify data in Social Media Channels page
4. **Cost**: $0

### Week 2-3: Add Manual Competitor Tracking
1. Create competitor profiles in Competitor Registry
2. Add social media handles
3. Manually update metrics weekly
4. **Cost**: $0 (time only)

### Month 2+: Upgrade to Third-Party Service (Optional)
1. Evaluate budget ($49-249/month recommended)
2. Subscribe to Brand24 or Mention
3. Configure API integration
4. Enable automated competitor tracking
5. **Cost**: $49-249/month

---

## 🛡️ Best Practices

### Do's:
✅ Use official APIs for your own accounts
✅ Subscribe to authorized third-party services
✅ Respect platform rate limits
✅ Store only public data
✅ Update Terms of Service compliance regularly
✅ Document data sources

### Don'ts:
❌ Never scrape social media sites
❌ Never exceed API rate limits
❌ Never store private/protected data
❌ Never use unauthorized bots
❌ Never circumvent authentication
❌ Never impersonate users

---

## 📞 Support & Questions

### Need Help?
- **API Setup**: See `docs/SOCIAL_MEDIA_API_SETUP.md`
- **Third-Party Integration**: See service-specific guides
- **Legal Questions**: Consult with legal counsel
- **Technical Issues**: Contact platform support teams

### Resources:
- Facebook API Docs: https://developers.facebook.com/docs
- Twitter API Docs: https://developer.twitter.com/en/docs
- YouTube API Docs: https://developers.google.com/youtube
- Instagram API Docs: https://developers.facebook.com/docs/instagram-api

---

## 📋 Compliance Checklist

Before collecting competitor data, verify:

- [ ] Method is explicitly allowed in platform ToS
- [ ] Using official APIs or authorized services
- [ ] Not exceeding rate limits
- [ ] Only collecting public data
- [ ] Data storage complies with DPDP Act
- [ ] Users have proper permissions
- [ ] Documentation is up to date

---

## ⚠️ Legal Disclaimer

This guide provides general recommendations. Always:
- Review current platform Terms of Service
- Consult legal counsel for specific situations
- Comply with local data protection laws (DPDP Act in India)
- Respect intellectual property rights
- Follow ethical data collection practices

**Last Updated**: November 2025
**Version**: 1.0
