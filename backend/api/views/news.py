"""
News Article API Views
Provides endpoints for Tamil Nadu political news with sentiment analysis
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta

from api.models import NewsArticle
from api.serializers.news_serializers import (
    NewsArticleListSerializer,
    NewsArticleDetailSerializer,
    NewsSentimentStatsSerializer,
    NewsSourceStatsSerializer
)


class NewsArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for news articles (read-only)

    Endpoints:
    - GET /api/news/ - List all articles with filters
    - GET /api/news/{id}/ - Get single article detail
    - GET /api/news/sentiment-stats/ - Get aggregated sentiment statistics
    - GET /api/news/source-stats/ - Get statistics by news source
    - GET /api/news/trending-topics/ - Get trending topics from articles
    """
    permission_classes = [AllowAny]  # Allow public read-only access to news
    queryset = NewsArticle.objects.filter(ai_processed=True)
    serializer_class = NewsArticleListSerializer

    def get_queryset(self):
        """
        Filter queryset based on query parameters
        """
        queryset = super().get_queryset()

        # Filter by date range
        days = self.request.query_params.get('days', None)
        if days:
            try:
                days_int = int(days)
                start_date = timezone.now() - timedelta(days=days_int)
                queryset = queryset.filter(published_at__gte=start_date)
            except ValueError:
                pass

        # Filter by sentiment
        sentiment = self.request.query_params.get('sentiment', None)
        if sentiment in ['positive', 'negative', 'neutral']:
            queryset = queryset.filter(tvk_sentiment=sentiment)

        # Filter by source
        source = self.request.query_params.get('source', None)
        if source:
            queryset = queryset.filter(source__icontains=source)

        # Filter by language
        language = self.request.query_params.get('language', None)
        if language in ['en', 'ta']:
            queryset = queryset.filter(language=language)

        # Filter by relevance
        relevant_only = self.request.query_params.get('relevant_only', 'false')
        if relevant_only.lower() == 'true':
            queryset = queryset.filter(is_relevant=True)

        # Search in title
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(article_text__icontains=search)
            )

        return queryset.order_by('-published_at')

    def get_serializer_class(self):
        """Use detailed serializer for retrieve action"""
        if self.action == 'retrieve':
            return NewsArticleDetailSerializer
        return NewsArticleListSerializer

    @action(detail=False, methods=['get'])
    def sentiment_stats(self, request):
        """
        Get aggregated sentiment statistics
        GET /api/news/sentiment-stats/?days=7
        """
        # Get date range
        days = request.query_params.get('days', '30')
        try:
            days_int = int(days)
            start_date = timezone.now() - timedelta(days=days_int)
        except ValueError:
            days_int = 30
            start_date = timezone.now() - timedelta(days=30)

        # Query articles
        articles = NewsArticle.objects.filter(
            published_at__gte=start_date,
            ai_processed=True
        )

        # Calculate statistics
        total_articles = articles.count()

        sentiment_counts = articles.values('tvk_sentiment').annotate(
            count=Count('id')
        )

        positive_count = next((item['count'] for item in sentiment_counts if item['tvk_sentiment'] == 'positive'), 0)
        negative_count = next((item['count'] for item in sentiment_counts if item['tvk_sentiment'] == 'negative'), 0)
        neutral_count = next((item['count'] for item in sentiment_counts if item['tvk_sentiment'] == 'neutral'), 0)

        avg_sentiment = articles.aggregate(Avg('tvk_sentiment_score'))['tvk_sentiment_score__avg'] or 0.5

        # Mentions
        total_vijay = sum(articles.values_list('vijay_mentions', flat=True))
        total_tvk = sum(articles.values_list('tvk_mentions', flat=True))

        # Articles by source
        source_counts = articles.values('source').annotate(count=Count('id'))
        articles_by_source = {item['source']: item['count'] for item in source_counts}

        # Articles by language
        language_counts = articles.values('language').annotate(count=Count('id'))
        articles_by_language = {item['language']: item['count'] for item in language_counts}

        # Trending topics (flatten and count)
        all_topics = []
        for article in articles:
            if article.key_topics:
                all_topics.extend(article.key_topics)

        from collections import Counter
        topic_counts = Counter(all_topics)
        trending_topics = [{'topic': topic, 'count': count} for topic, count in topic_counts.most_common(10)]

        stats = {
            'total_articles': total_articles,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'avg_sentiment_score': round(avg_sentiment, 2),
            'total_vijay_mentions': total_vijay,
            'total_tvk_mentions': total_tvk,
            'articles_by_source': articles_by_source,
            'articles_by_language': articles_by_language,
            'trending_topics': trending_topics,
        }

        serializer = NewsSentimentStatsSerializer(stats)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def source_stats(self, request):
        """
        Get statistics grouped by news source
        GET /api/news/source-stats/?days=7
        """
        # Get date range
        days = request.query_params.get('days', '30')
        try:
            days_int = int(days)
            start_date = timezone.now() - timedelta(days=days_int)
        except ValueError:
            days_int = 30
            start_date = timezone.now() - timedelta(days=30)

        # Get all sources
        sources = NewsArticle.objects.filter(
            published_at__gte=start_date,
            ai_processed=True
        ).values('source').distinct()

        source_stats = []
        for source_item in sources:
            source_name = source_item['source']
            source_articles = NewsArticle.objects.filter(
                source=source_name,
                published_at__gte=start_date,
                ai_processed=True
            )

            total = source_articles.count()
            positive = source_articles.filter(tvk_sentiment='positive').count()
            negative = source_articles.filter(tvk_sentiment='negative').count()
            neutral = source_articles.filter(tvk_sentiment='neutral').count()
            avg_score = source_articles.aggregate(Avg('tvk_sentiment_score'))['tvk_sentiment_score__avg'] or 0.5

            source_stats.append({
                'source': source_name,
                'total_articles': total,
                'positive_count': positive,
                'negative_count': negative,
                'neutral_count': neutral,
                'avg_sentiment_score': round(avg_score, 2),
            })

        # Sort by total articles
        source_stats.sort(key=lambda x: x['total_articles'], reverse=True)

        serializer = NewsSourceStatsSerializer(source_stats, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def trending_topics(self, request):
        """
        Get trending topics from recent articles
        GET /api/news/trending-topics/?days=7&limit=20
        """
        # Get date range
        days = request.query_params.get('days', '7')
        limit = request.query_params.get('limit', '20')

        try:
            days_int = int(days)
            start_date = timezone.now() - timedelta(days=days_int)
        except ValueError:
            days_int = 7
            start_date = timezone.now() - timedelta(days=7)

        try:
            limit_int = int(limit)
        except ValueError:
            limit_int = 20

        # Get articles
        articles = NewsArticle.objects.filter(
            published_at__gte=start_date,
            ai_processed=True,
            is_relevant=True
        )

        # Flatten topics
        all_topics = []
        for article in articles:
            if article.key_topics:
                all_topics.extend(article.key_topics)

        # Count and rank
        from collections import Counter
        topic_counts = Counter(all_topics)
        trending = [
            {'topic': topic, 'count': count, 'percentage': round((count / len(all_topics)) * 100, 1)}
            for topic, count in topic_counts.most_common(limit_int)
        ]

        return Response({
            'period_days': days_int,
            'total_articles': articles.count(),
            'total_topics': len(all_topics),
            'unique_topics': len(topic_counts),
            'trending_topics': trending,
        })
