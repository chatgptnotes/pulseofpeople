# TV & Broadcast Analysis - Data Strategy
## From Dummy Data to Real Data Integration

**Date:** 2025-11-09
**Status:** Ready for Implementation
**Priority:** High

---

## 🎯 Current Situation

**Problem:** The TV Broadcast Analysis page uses hardcoded dummy data in `TVBroadcastAnalysis.tsx`

**Files with Dummy Data:**
- `src/pages/TVBroadcastAnalysis.tsx` - Lines 91-400+ (hardcoded arrays)
- No database integration
- No real-time updates

---

## 📋 Recommended 3-Phase Approach

### **Phase 1: Database + Seed Data** (Week 1) ✅ READY
**Goal:** Replace dummy data with database-backed seed data

#### What We Built:
1. **Database Schema** (`20251109_tv_broadcast_schema.sql`)
   - 5 tables: channels, shows, segments, viewership, sentiment_trends
   - Full-text search on transcriptions
   - Auto-calculated durations
   - Trigger-based updates

2. **Realistic Seed Data** (`seed_tv_broadcast_data.sql`)
   - 14 Tamil Nadu + National TV channels
   - 9 popular Tamil news shows
   - 9 recent broadcast segments covering TVK, DMK, BJP
   - Sample BARC viewership ratings

#### Action Items:
1. **Run migrations in Supabase:**
   ```sql
   -- Step 1: Create schema
   -- Copy/paste: supabase/migrations/20251109_tv_broadcast_schema.sql

   -- Step 2: Insert seed data
   -- Copy/paste: supabase/seed_tv_broadcast_data.sql
   ```

2. **Update React component** to fetch from Supabase instead of hardcoded arrays

3. **Test** that all data appears correctly

#### Expected Outcome:
✅ Database populated with realistic Tamil Nadu TV data
✅ No more hardcoded arrays in React components
✅ Data can be edited via Supabase dashboard or API

---

### **Phase 2: Manual Data Entry UI** (Week 2-3)
**Goal:** Build admin interface for your team to add/edit TV segments

#### What to Build:
1. **Channel Management Page**
   - Add/edit/delete TV channels
   - Update viewership counts
   - Set prime time slots

2. **Broadcast Segment Entry Form**
   - Quick-add segment interface
   - Autocomplete for channel/show names
   - Sentiment tagging (positive/neutral/negative)
   - Mention tagging (Vijay, Stalin, etc.)
   - Priority flags

3. **Bulk Import Tool**
   - CSV upload for multiple segments
   - Template: `Channel, Show, Time, Topic, Sentiment, Mentions`

#### Tech Stack:
- React form with Tailwind CSS
- Supabase client for CRUD operations
- React Hook Form for validation

#### Example UI Flow:
```
Admin Dashboard → TV Broadcast → Add Segment
  ↓
Form Fields:
  - Channel: [Dropdown: Sun News, Thanthi TV, ...]
  - Show Name: [Autocomplete]
  - Date/Time: [DateTime Picker]
  - Topic: [Text Input]
  - Sentiment: [Positive/Neutral/Negative buttons]
  - Mentions: [Tag Input: Vijay, Stalin, ...]
  - Priority: [High/Medium/Low]
  - Notes: [Textarea]
  ↓
Save → Broadcasts to Supabase → Updates dashboard in real-time
```

#### Benefits:
✅ Your team can add data daily without coding
✅ Structured data format ensures consistency
✅ Faster than manually editing SQL

---

### **Phase 3: Real Data Integration** (Month 2-3)
**Goal:** Automate data collection from real sources

#### Option A: Media Monitoring Services (Recommended)
**Services that provide TV monitoring in India:**

1. **BARC India** (Broadcast Audience Research Council)
   - **What:** Official TV ratings provider
   - **Data:** Viewership numbers, TRP ratings
   - **Access:** Requires subscription ($$$)
   - **API:** Contact BARC for enterprise access
   - **Best For:** Accurate viewership metrics

2. **Prime Focus Technologies** (Media Monitoring)
   - **What:** Media intelligence platform
   - **Data:** TV transcriptions, sentiment analysis
   - **Access:** Enterprise subscription
   - **Integration:** API available
   - **Best For:** Automated transcriptions

3. **TVEyes India**
   - **What:** TV/radio monitoring service
   - **Data:** Real-time transcriptions, clips
   - **Access:** Subscription-based
   - **Integration:** API + web dashboard
   - **Best For:** Real-time alerts

4. **Meltwater** (Global Media Intelligence)
   - **What:** Media monitoring (includes TV)
   - **Data:** Transcriptions, sentiment, mentions
   - **Access:** Enterprise SaaS
   - **Integration:** REST API
   - **Best For:** Multi-channel monitoring

#### Option B: DIY Integration (Lower Cost)

1. **RSS Feeds**
   - Most TV news channels publish RSS feeds
   - Example: Thanthi TV news RSS
   - **Pros:** Free, easy to parse
   - **Cons:** Limited to text headlines, no video/sentiment

2. **YouTube API**
   - Many channels upload full shows to YouTube
   - **Endpoint:** `youtube.data.list()`
   - **Data:** Video titles, descriptions, view counts
   - **Quota:** 10,000 units/day (free tier)
   - **Example:**
     ```javascript
     // Get latest videos from Sun News
     GET https://www.googleapis.com/youtube/v3/search
       ?channelId=UCNEhRGbdWM
       &part=snippet
       &maxResults=50
       &order=date
       &key=YOUR_API_KEY
     ```

3. **News Aggregators**
   - News API, Google News RSS
   - Filter by channel/source
   - **Limitation:** Text-only, no video segments

4. **Speech-to-Text (For Video Transcription)**
   - **Google Cloud Speech-to-Text API**
   - **AWS Transcribe**
   - Upload video clips → Get transcriptions
   - Then run sentiment analysis on text

#### Option C: Hybrid Approach (Best Value)
Combine manual entry (Phase 2) with partial automation:

1. **Your team watches TV** (manual)
2. **Logs segments via form** (Phase 2 UI)
3. **Automated enrichment:**
   - Fetch viewership from BARC API (weekly sync)
   - Get social media mentions from Twitter API
   - Auto-tag politicians/parties using NLP

---

## 💰 Cost Analysis

| Solution | Setup Cost | Monthly Cost | Effort | Data Quality |
|----------|-----------|--------------|--------|--------------|
| **Manual Entry (Phase 2)** | ₹0 | ₹0 | High | High |
| **BARC Subscription** | ₹50,000 | ₹10,000 | Low | Very High |
| **Media Monitoring Service** | ₹1,00,000 | ₹25,000 | Low | High |
| **DIY (YouTube + RSS)** | ₹0 | ₹0 | Medium | Medium |
| **Hybrid (Manual + APIs)** | ₹5,000 | ₹2,000 | Medium | High |

---

## 🚀 Recommended Implementation Plan

### **NOW (This Week)**
✅ **Phase 1:** Run database migrations
✅ Update `TVBroadcastAnalysis.tsx` to use Supabase
✅ Test with seed data

### **Next 2 Weeks**
🔨 **Phase 2:** Build manual data entry UI
📊 Create Channel Management page
📝 Create Broadcast Segment form
📤 CSV import tool

### **Month 2**
🔌 **Phase 3 (Starter):**
- Integrate YouTube API for video metadata
- Add RSS feed ingestion for headlines
- Set up cron job for daily syncs

### **Month 3+**
🤖 **Phase 3 (Advanced):**
- Evaluate BARC subscription
- Trial media monitoring service (Meltwater/TVEyes)
- Implement speech-to-text for transcriptions
- Build automated sentiment analysis pipeline

---

## 📊 Sample API Integration Code

### **YouTube API Integration** (Get Latest Videos)
```typescript
// src/lib/youtube-integration.ts
import { supabase } from './supabase';

const YOUTUBE_API_KEY = import.meta.env.VITE_YOUTUBE_API_KEY;

interface YouTubeVideo {
  id: string;
  title: string;
  publishedAt: string;
  channelTitle: string;
}

export async function fetchLatestTVSegments(channelId: string) {
  try {
    const response = await fetch(
      `https://www.googleapis.com/youtube/v3/search?` +
      `channelId=${channelId}&` +
      `part=snippet&` +
      `maxResults=20&` +
      `order=date&` +
      `type=video&` +
      `key=${YOUTUBE_API_KEY}`
    );

    const data = await response.json();

    // Transform to your schema
    const segments = data.items.map((item: any) => ({
      channel_code: 'sun-news', // Map from channelId
      show_name: 'YouTube Upload',
      segment_title: item.snippet.title,
      broadcast_date: new Date(item.snippet.publishedAt).toISOString().split('T')[0],
      start_time: new Date(item.snippet.publishedAt),
      topic: item.snippet.description,
      clip_url: `https://youtube.com/watch?v=${item.id.videoId}`,
      data_source: 'youtube_api',
      processing_status: 'completed'
    }));

    // Insert into Supabase
    const { error } = await supabase
      .from('broadcast_segments')
      .upsert(segments);

    if (error) throw error;

    return segments;
  } catch (error) {
    console.error('YouTube API error:', error);
    throw error;
  }
}

// Channel IDs for Tamil TV channels
export const TV_CHANNEL_IDS = {
  'sun-news': 'UCNEhRGbdWM...',
  'puthiya-thalaimurai': 'UC-dsDKFz...',
  'thanthi-tv': 'UCKahSL...'
};
```

### **RSS Feed Integration** (News Headlines)
```typescript
// src/lib/rss-integration.ts
import Parser from 'rss-parser';
import { supabase } from './supabase';

const parser = new Parser();

const RSS_FEEDS = {
  'sun-news': 'https://www.sunnews.com/rss/latest',
  'thanthi-tv': 'https://www.thanthitv.com/rss/news'
};

export async function syncRSSFeeds() {
  for (const [channelCode, feedUrl] of Object.entries(RSS_FEEDS)) {
    try {
      const feed = await parser.parseURL(feedUrl);

      const segments = feed.items.map(item => ({
        channel_code: channelCode,
        show_name: 'Breaking News',
        segment_title: item.title,
        broadcast_date: new Date(item.pubDate).toISOString().split('T')[0],
        start_time: new Date(item.pubDate),
        topic: item.contentSnippet,
        description: item.content,
        data_source: 'rss_feed',
        processing_status: 'completed'
      }));

      await supabase
        .from('broadcast_segments')
        .upsert(segments);

    } catch (error) {
      console.error(`RSS sync failed for ${channelCode}:`, error);
    }
  }
}

// Run daily at 6 AM
// Setup in Vercel Cron Jobs or Supabase Edge Functions
```

---

## 🔧 Migration Checklist

### Pre-Migration
- [ ] Backup current `TVBroadcastAnalysis.tsx`
- [ ] Review seed data for accuracy
- [ ] Confirm Supabase connection

### Migration Steps
- [ ] Run schema migration
- [ ] Run seed data script
- [ ] Verify data in Supabase dashboard
- [ ] Update React component
- [ ] Test all features
- [ ] Remove hardcoded dummy data

### Post-Migration
- [ ] Monitor performance
- [ ] Train team on manual entry (if Phase 2)
- [ ] Set up API integrations (if Phase 3)
- [ ] Document data update procedures

---

## 📞 Next Steps

1. **Review this document** with your team
2. **Choose your approach:**
   - Start with Phase 1 (this week)
   - Plan Phase 2 timeline
   - Budget for Phase 3 services

3. **Run the migrations** I created
4. **Test with seed data**
5. **Decide:** Manual entry vs API integration vs Hybrid

---

## 📚 Additional Resources

- **BARC India:** https://barcindia.co.in
- **YouTube Data API:** https://developers.google.com/youtube/v3
- **Google Cloud Speech-to-Text:** https://cloud.google.com/speech-to-text
- **Meltwater Media Intelligence:** https://www.meltwater.com
- **TVEyes:** https://www.tveyes.com

---

**Questions?** Update this document as decisions are made.
