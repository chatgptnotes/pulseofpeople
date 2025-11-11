# Press & Media Monitoring Setup Guide

## ✅ What's Been Done

Your Press & Media Monitoring page is now **connected to the real backend API** that scrapes Tamil Nadu political news about TVK/Vijay using BeautifulSoup!

### Frontend Updates (PressMediaMonitoring.tsx)
- ✅ Replaced mock data with real API calls
- ✅ Added loading states and error handling
- ✅ Added refresh button
- ✅ Added sentiment filter buttons (All, Positive, Neutral, Negative)
- ✅ Wired up filters to API parameters
- ✅ Real-time data fetching from backend

### Data Sources
The backend scrapes news from:
- **Tamil**: Dinamalar, Dinakaran
- **English**: The Hindu TN, Times of India Chennai, Indian Express TN

### Features
- Sentiment analysis powered by OpenAI GPT-4
- Automatic scraping every 6 hours
- Filtering by sentiment, language, timeframe
- Search functionality
- Trending topics
- Source statistics

## 🚀 How to Test

### Step 1: Run Database Migrations

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

This creates the `NewsArticle` table in your database.

### Step 2: Set OpenAI API Key

Add to `backend/.env`:
```env
OPENAI_API_KEY=your-openai-api-key-here
```

### Step 3: Start Django Backend

```bash
cd backend
python manage.py runserver
```

Backend runs at: `http://127.0.0.1:8000`

### Step 4: Manually Scrape First Batch of News

Open Django shell:
```bash
python manage.py shell
```

Run this command:
```python
from api.tasks import scrape_and_analyze_news_pipeline
result = scrape_and_analyze_news_pipeline()
print(result)
```

This will:
1. Scrape Tamil Nadu political news from 5 sources
2. Save articles to database
3. Analyze sentiment with GPT-4
4. Print results

Expected output:
```
✅ News scraping complete: 15 articles scraped, 12 articles saved
✅ Sentiment analysis complete: 12 analyzed, 0 errors
```

### Step 5: Start Frontend

```bash
cd frontend
npm run dev
```

Frontend runs at: `http://localhost:5173`

### Step 6: View Press & Media Monitoring Page

Navigate to:
```
http://localhost:5173/press-media-monitoring
```

You should see:
- Real articles from Tamil Nadu news sources
- Sentiment analysis (positive/negative/neutral)
- Vijay/TVK mention counts
- Trending topics
- Source statistics

## 🔄 Enable Automatic Scraping (Optional)

To scrape news automatically every 6 hours:

### Start Celery Worker

```bash
cd backend
celery -A config worker -l info
```

### Start Celery Beat (Scheduler)

```bash
celery -A config beat -l info
```

Now news will be scraped automatically at:
- 12:00 AM
- 6:00 AM
- 12:00 PM
- 6:00 PM

## 🎯 How to Use the Page

### Overview Tab
- See total articles count
- View sentiment distribution (positive/negative/neutral)
- See breaking news alerts
- View trending topics

### Sources Tab
- See all news sources (Dinamalar, Dinakaran, The Hindu, etc.)
- View credibility scores
- See article counts per source

### Articles Tab
- Search articles by keyword
- Filter by sentiment (All/Positive/Neutral/Negative)
- Filter by language (Tamil/English)
- Filter by timeframe (1h/6h/24h/7d)
- Click article title to open original source

### Trends Tab
- View trending topics
- See mention counts
- View sentiment for each topic

### Analytics Tab
- View source performance
- Language distribution
- Detailed metrics

## 🐛 Troubleshooting

### "Failed to load news data"
**Problem**: Backend API not running or no data in database

**Solution**:
1. Make sure Django backend is running: `python manage.py runserver`
2. Run manual scraping in Django shell (see Step 4)
3. Check console for errors

### "Loading Tamil Nadu political news..." (stuck)
**Problem**: Backend not reachable

**Solution**:
1. Check backend is running at `http://127.0.0.1:8000`
2. Check `VITE_DJANGO_API_URL` in `frontend/.env`
3. Try accessing `http://127.0.0.1:8000/api/news/` in browser

### No articles showing
**Problem**: Database is empty

**Solution**:
1. Run manual scraping (see Step 4)
2. Wait a few minutes for articles to process
3. Refresh the page

### Sentiment analysis not working
**Problem**: OpenAI API key not set or invalid

**Solution**:
1. Add `OPENAI_API_KEY` to `backend/.env`
2. Restart Django server
3. Re-run scraping task

## 📊 Example API Endpoints

You can test these directly in browser:

- **All articles**: http://127.0.0.1:8000/api/news/
- **Positive sentiment**: http://127.0.0.1:8000/api/news/?sentiment=positive
- **Last 7 days**: http://127.0.0.1:8000/api/news/?days=7
- **Tamil articles**: http://127.0.0.1:8000/api/news/?language=ta
- **Search**: http://127.0.0.1:8000/api/news/?search=vijay
- **Sentiment stats**: http://127.0.0.1:8000/api/news/sentiment-stats/
- **Source stats**: http://127.0.0.1:8000/api/news/source-stats/
- **Trending topics**: http://127.0.0.1:8000/api/news/trending-topics/

## ✨ What You Get

1. **Real Tamil Nadu Political News** about TVK/Vijay
2. **AI-Powered Sentiment Analysis** (positive/negative/neutral scores)
3. **Mention Tracking** (Vijay, TVK, DMK counts)
4. **Trending Topics** extracted by LLM
5. **Multi-language Support** (Tamil and English)
6. **Automatic Scraping** every 6 hours
7. **Beautiful Dashboard** with filters and search

## 🎉 You're Done!

Your Press & Media Monitoring page is now live with real data from Tamil Nadu news sources!

Questions? Check the console for errors or review the API endpoints above.
