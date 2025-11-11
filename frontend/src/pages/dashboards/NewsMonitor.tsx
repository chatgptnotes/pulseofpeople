/**
 * News Monitor Dashboard
 *
 * Displays Tamil Nadu political news with AI-powered sentiment analysis
 * - Real-time sentiment tracking for TVK/Vijay coverage
 * - Source performance comparison
 * - Trending topics analysis
 * - Article search and filtering
 */

import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { newsApi, NewsArticle, NewsSentimentStats, NewsSourceStats, NewsFilters } from '../../services/newsApi';
import { Card } from '../../components/ui/Card';
import { PieChart } from '../../components/charts/PieChart';
import { BarChart } from '../../components/charts/BarChart';
import { LineChart } from '../../components/charts/LineChart';
import ArticleIcon from '@mui/icons-material/Article';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import NewspaperIcon from '@mui/icons-material/Newspaper';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import SearchIcon from '@mui/icons-material/Search';
import FilterListIcon from '@mui/icons-material/FilterList';
import RefreshIcon from '@mui/icons-material/Refresh';
import SentimentSatisfiedIcon from '@mui/icons-material/SentimentSatisfied';
import SentimentDissatisfiedIcon from '@mui/icons-material/SentimentDissatisfied';
import SentimentNeutralIcon from '@mui/icons-material/SentimentNeutral';

export default function NewsMonitor() {
  const { user } = useAuth();

  // State
  const [loading, setLoading] = useState(true);
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [sentimentStats, setSentimentStats] = useState<NewsSentimentStats | null>(null);
  const [sourceStats, setSourceStats] = useState<NewsSourceStats[]>([]);
  const [filters, setFilters] = useState<NewsFilters>({ days: 7, page_size: 20 });
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSentiment, setSelectedSentiment] = useState<'all' | 'positive' | 'negative' | 'neutral'>('all');

  useEffect(() => {
    loadDashboardData();
  }, [filters]);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      // Load all data in parallel
      const [articlesData, stats, sources] = await Promise.all([
        newsApi.getArticles(filters),
        newsApi.getSentimentStats(filters.days || 7),
        newsApi.getSourceStats(filters.days || 7),
      ]);

      setArticles(articlesData.results);
      setSentimentStats(stats);
      setSourceStats(sources);
    } catch (error) {
      console.error('Error loading news data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setFilters({ ...filters, search: searchQuery });
  };

  const handleSentimentFilter = (sentiment: typeof selectedSentiment) => {
    setSelectedSentiment(sentiment);
    setFilters({
      ...filters,
      sentiment: sentiment === 'all' ? undefined : sentiment,
    });
  };

  const handleRefresh = () => {
    loadDashboardData();
  };

  // Calculate sentiment colors
  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'text-green-600 bg-green-50';
      case 'negative': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return <SentimentSatisfiedIcon className="h-5 w-5" />;
      case 'negative': return <SentimentDissatisfiedIcon className="h-5 w-5" />;
      default: return <SentimentNeutralIcon className="h-5 w-5" />;
    }
  };

  // Prepare chart data
  const sentimentChartData = sentimentStats ? {
    labels: ['Positive', 'Neutral', 'Negative'],
    datasets: [{
      data: [sentimentStats.positive_count, sentimentStats.neutral_count, sentimentStats.negative_count],
      backgroundColor: ['#10b981', '#6b7280', '#ef4444'],
    }]
  } : null;

  const sourceChartData = sourceStats.length > 0 ? {
    labels: sourceStats.map(s => s.source),
    datasets: [{
      label: 'Total Articles',
      data: sourceStats.map(s => s.total_articles),
      backgroundColor: '#3b82f6',
    }]
  } : null;

  if (loading) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2 mb-8"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">News Monitor</h1>
            <p className="mt-2 text-gray-600">
              AI-powered sentiment analysis of Tamil Nadu political news
            </p>
          </div>
          <button
            onClick={handleRefresh}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <RefreshIcon className="h-5 w-5" />
            Refresh
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      {sentimentStats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Articles</p>
                <p className="text-2xl font-bold text-gray-900 mt-2">
                  {sentimentStats.total_articles}
                </p>
              </div>
              <div className="bg-blue-500 p-3 rounded-lg">
                <ArticleIcon className="h-6 w-6 text-white" />
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Avg Sentiment</p>
                <p className="text-2xl font-bold text-gray-900 mt-2">
                  {sentimentStats.avg_sentiment_score.toFixed(2)}
                </p>
              </div>
              <div className="bg-purple-500 p-3 rounded-lg">
                <AnalyticsIcon className="h-6 w-6 text-white" />
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Vijay Mentions</p>
                <p className="text-2xl font-bold text-gray-900 mt-2">
                  {sentimentStats.total_vijay_mentions}
                </p>
              </div>
              <div className="bg-green-500 p-3 rounded-lg">
                <TrendingUpIcon className="h-6 w-6 text-white" />
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">TVK Mentions</p>
                <p className="text-2xl font-bold text-gray-900 mt-2">
                  {sentimentStats.total_tvk_mentions}
                </p>
              </div>
              <div className="bg-indigo-500 p-3 rounded-lg">
                <NewspaperIcon className="h-6 w-6 text-white" />
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Filters and Search */}
      <Card className="p-6 mb-8">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 flex gap-2">
            <input
              type="text"
              placeholder="Search articles..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              onClick={handleSearch}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <SearchIcon className="h-5 w-5" />
            </button>
          </div>

          <div className="flex gap-2">
            <button
              onClick={() => handleSentimentFilter('all')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                selectedSentiment === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              All
            </button>
            <button
              onClick={() => handleSentimentFilter('positive')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                selectedSentiment === 'positive' ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Positive
            </button>
            <button
              onClick={() => handleSentimentFilter('neutral')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                selectedSentiment === 'neutral' ? 'bg-gray-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Neutral
            </button>
            <button
              onClick={() => handleSentimentFilter('negative')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                selectedSentiment === 'negative' ? 'bg-red-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Negative
            </button>
          </div>
        </div>
      </Card>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Sentiment Distribution */}
        {sentimentChartData && (
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Sentiment Distribution</h3>
            <div className="h-64">
              <PieChart data={sentimentChartData} />
            </div>
          </Card>
        )}

        {/* Source Performance */}
        {sourceChartData && (
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Articles by Source</h3>
            <div className="h-64">
              <BarChart data={sourceChartData} />
            </div>
          </Card>
        )}
      </div>

      {/* Recent Articles */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Articles</h3>

        {articles.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <ArticleIcon className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <p>No articles found matching your filters</p>
          </div>
        ) : (
          <div className="space-y-4">
            {articles.map((article) => (
              <div
                key={article.id}
                className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900 mb-2">
                      <a
                        href={article.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="hover:text-blue-600 transition-colors"
                      >
                        {article.title}
                      </a>
                    </h4>

                    <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                      {article.excerpt_preview}
                    </p>

                    <div className="flex flex-wrap items-center gap-3 text-sm">
                      <span className="text-gray-500">
                        <strong>{article.source}</strong>
                      </span>
                      <span className="text-gray-400">•</span>
                      <span className="text-gray-500">
                        {new Date(article.published_at).toLocaleDateString()}
                      </span>
                      {article.author && (
                        <>
                          <span className="text-gray-400">•</span>
                          <span className="text-gray-500">{article.author}</span>
                        </>
                      )}
                      <span className="text-gray-400">•</span>
                      <span className="text-gray-500">{article.language === 'ta' ? 'Tamil' : 'English'}</span>
                    </div>
                  </div>

                  <div className="flex flex-col items-end gap-2">
                    <div className={`flex items-center gap-1 px-3 py-1 rounded-full ${getSentimentColor(article.tvk_sentiment)}`}>
                      {getSentimentIcon(article.tvk_sentiment)}
                      <span className="text-sm font-medium capitalize">{article.tvk_sentiment}</span>
                    </div>
                    <div className="text-sm text-gray-500">
                      Score: {article.tvk_sentiment_score.toFixed(2)}
                    </div>
                    {(article.vijay_mentions > 0 || article.tvk_mentions > 0) && (
                      <div className="text-xs text-gray-500">
                        Vijay: {article.vijay_mentions} | TVK: {article.tvk_mentions}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
