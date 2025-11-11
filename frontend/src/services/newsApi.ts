/**
 * News Articles API Service
 * Handles all API calls to the Django backend for news scraping and sentiment analysis
 *
 * This service connects to Django for:
 * - Tamil Nadu political news articles
 * - LLM-powered sentiment analysis for TVK/Vijay coverage
 * - Aggregated sentiment statistics
 * - News source performance tracking
 * - Trending topics analysis
 */

import { supabase } from '../lib/supabase';

const DJANGO_API_URL = import.meta.env.VITE_DJANGO_API_URL || 'http://127.0.0.1:8000/api';

// =====================================================
// TYPE DEFINITIONS
// =====================================================

export interface NewsArticle {
  id: string;
  title: string;
  url: string;
  source: string;
  author: string | null;
  published_at: string;
  scraped_at: string;
  language: 'en' | 'ta';
  word_count: number;
  excerpt_preview?: string;

  // Sentiment fields
  tvk_sentiment: 'positive' | 'negative' | 'neutral';
  tvk_sentiment_score: number;
  vijay_mentions: number;
  tvk_mentions: number;
  dmk_mentions: number;
  opposition_mentions?: number;

  // Metadata
  is_relevant: boolean;
  category: string;
  ai_processed: boolean;
}

export interface NewsArticleDetail extends NewsArticle {
  article_text: string;
  excerpt: string | null;
  sentiment_reasoning: string | null;
  ai_summary: string | null;
  key_topics: string[];
  entities_mentioned: string[];
  processing_attempts: number;
  processing_error: string | null;
}

export interface NewsSentimentStats {
  total_articles: number;
  positive_count: number;
  negative_count: number;
  neutral_count: number;
  avg_sentiment_score: number;
  total_vijay_mentions: number;
  total_tvk_mentions: number;
  articles_by_source: Record<string, number>;
  articles_by_language: Record<string, number>;
  trending_topics: Array<{ topic: string; count: number }>;
}

export interface NewsSourceStats {
  source: string;
  total_articles: number;
  positive_count: number;
  negative_count: number;
  neutral_count: number;
  avg_sentiment_score: number;
}

export interface TrendingTopicsResponse {
  period_days: number;
  total_articles: number;
  total_topics: number;
  unique_topics: number;
  trending_topics: Array<{
    topic: string;
    count: number;
    percentage: number;
  }>;
}

export interface NewsFilters {
  days?: number;
  sentiment?: 'positive' | 'negative' | 'neutral';
  source?: string;
  language?: 'en' | 'ta';
  relevant_only?: boolean;
  search?: string;
  page?: number;
  page_size?: number;
}

// =====================================================
// AUTHENTICATION HELPERS
// =====================================================

const getAuthToken = async (): Promise<string | null> => {
  try {
    const { data: { session }, error } = await supabase.auth.getSession();

    if (error) {
      console.error('[NewsAPI] Error fetching session:', error.message);
      return null;
    }

    if (!session) {
      console.warn('[NewsAPI] No active session found');
      return null;
    }

    return session.access_token;
  } catch (error: any) {
    console.error('[NewsAPI] Unexpected error getting token:', error.message);
    return null;
  }
};

const buildHeaders = async (includeAuth = true): Promise<HeadersInit> => {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  if (includeAuth) {
    const token = await getAuthToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    } else {
      console.warn('[NewsAPI] No token available for authenticated request');
    }
  }

  return headers;
};

// =====================================================
// NEWS ARTICLES API
// =====================================================

export const newsApi = {
  /**
   * Get list of news articles with optional filters
   * GET /api/news/?days=7&sentiment=positive&source=The Hindu
   */
  async getArticles(filters?: NewsFilters): Promise<{
    count: number;
    next: string | null;
    previous: string | null;
    results: NewsArticle[];
  }> {
    try {
      const params = new URLSearchParams();

      if (filters?.days) params.append('days', filters.days.toString());
      if (filters?.sentiment) params.append('sentiment', filters.sentiment);
      if (filters?.source) params.append('source', filters.source);
      if (filters?.language) params.append('language', filters.language);
      if (filters?.relevant_only) params.append('relevant_only', 'true');
      if (filters?.search) params.append('search', filters.search);
      if (filters?.page) params.append('page', filters.page.toString());
      if (filters?.page_size) params.append('page_size', filters.page_size.toString());

      const url = `${DJANGO_API_URL}/news/?${params.toString()}`;
      const response = await fetch(url, {
        method: 'GET',
        headers: await buildHeaders(),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Failed to fetch articles' }));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      return response.json();
    } catch (error: any) {
      console.error('[NewsAPI] Error fetching articles:', error.message);
      throw error;
    }
  },

  /**
   * Get single article detail
   * GET /api/news/{id}/
   */
  async getArticleDetail(articleId: string): Promise<NewsArticleDetail> {
    try {
      const response = await fetch(`${DJANGO_API_URL}/news/${articleId}/`, {
        method: 'GET',
        headers: await buildHeaders(),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Article not found' }));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      return response.json();
    } catch (error: any) {
      console.error('[NewsAPI] Error fetching article detail:', error.message);
      throw error;
    }
  },

  /**
   * Get aggregated sentiment statistics
   * GET /api/news/sentiment-stats/?days=7
   */
  async getSentimentStats(days = 30): Promise<NewsSentimentStats> {
    try {
      const response = await fetch(`${DJANGO_API_URL}/news/sentiment-stats/?days=${days}`, {
        method: 'GET',
        headers: await buildHeaders(),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Failed to fetch sentiment stats' }));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      return response.json();
    } catch (error: any) {
      console.error('[NewsAPI] Error fetching sentiment stats:', error.message);
      throw error;
    }
  },

  /**
   * Get statistics grouped by news source
   * GET /api/news/source-stats/?days=7
   */
  async getSourceStats(days = 30): Promise<NewsSourceStats[]> {
    try {
      const response = await fetch(`${DJANGO_API_URL}/news/source-stats/?days=${days}`, {
        method: 'GET',
        headers: await buildHeaders(),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Failed to fetch source stats' }));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      return response.json();
    } catch (error: any) {
      console.error('[NewsAPI] Error fetching source stats:', error.message);
      throw error;
    }
  },

  /**
   * Get trending topics from recent articles
   * GET /api/news/trending-topics/?days=7&limit=20
   */
  async getTrendingTopics(days = 7, limit = 20): Promise<TrendingTopicsResponse> {
    try {
      const response = await fetch(
        `${DJANGO_API_URL}/news/trending-topics/?days=${days}&limit=${limit}`,
        {
          method: 'GET',
          headers: await buildHeaders(),
        }
      );

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Failed to fetch trending topics' }));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      return response.json();
    } catch (error: any) {
      console.error('[NewsAPI] Error fetching trending topics:', error.message);
      throw error;
    }
  },

  /**
   * Get sentiment trend over time (helper function)
   * Fetches articles for different time periods to show trend
   */
  async getSentimentTrend(days = 30): Promise<Array<{
    date: string;
    positive: number;
    negative: number;
    neutral: number;
    avg_score: number;
  }>> {
    try {
      // This would need a dedicated backend endpoint for optimal performance
      // For now, we'll fetch all articles and group them client-side
      const articles = await this.getArticles({ days, page_size: 1000 });

      // Group by date
      const dateGroups: Record<string, NewsArticle[]> = {};

      articles.results.forEach(article => {
        const date = article.published_at.split('T')[0]; // Get YYYY-MM-DD
        if (!dateGroups[date]) {
          dateGroups[date] = [];
        }
        dateGroups[date].push(article);
      });

      // Calculate stats for each date
      const trend = Object.entries(dateGroups).map(([date, dayArticles]) => {
        const positive = dayArticles.filter(a => a.tvk_sentiment === 'positive').length;
        const negative = dayArticles.filter(a => a.tvk_sentiment === 'negative').length;
        const neutral = dayArticles.filter(a => a.tvk_sentiment === 'neutral').length;
        const avg_score = dayArticles.reduce((sum, a) => sum + a.tvk_sentiment_score, 0) / dayArticles.length;

        return {
          date,
          positive,
          negative,
          neutral,
          avg_score: parseFloat(avg_score.toFixed(2)),
        };
      });

      // Sort by date
      trend.sort((a, b) => a.date.localeCompare(b.date));

      return trend;
    } catch (error: any) {
      console.error('[NewsAPI] Error calculating sentiment trend:', error.message);
      throw error;
    }
  },
};
