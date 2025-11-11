"""
News Article Serializers
Handles serialization for Tamil Nadu political news articles with sentiment analysis
"""

from rest_framework import serializers
from api.models import NewsArticle


class NewsArticleListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for news article lists
    """
    excerpt_preview = serializers.SerializerMethodField()

    class Meta:
        model = NewsArticle
        fields = [
            'id',
            'title',
            'url',
            'source',
            'author',
            'published_at',
            'scraped_at',
            'language',
            'word_count',
            'excerpt_preview',

            # Sentiment fields
            'tvk_sentiment',
            'tvk_sentiment_score',
            'vijay_mentions',
            'tvk_mentions',
            'dmk_mentions',

            # Metadata
            'is_relevant',
            'category',
            'ai_processed',
        ]
        read_only_fields = fields

    def get_excerpt_preview(self, obj):
        """Return first 150 characters of article as preview"""
        if obj.excerpt:
            return obj.excerpt[:150] + '...' if len(obj.excerpt) > 150 else obj.excerpt
        return obj.article_text[:150] + '...' if len(obj.article_text) > 150 else obj.article_text


class NewsArticleDetailSerializer(serializers.ModelSerializer):
    """
    Complete serializer with full article content and analysis
    """

    class Meta:
        model = NewsArticle
        fields = [
            'id',
            'title',
            'url',
            'source',
            'author',
            'published_at',
            'scraped_at',

            # Content
            'article_text',
            'excerpt',
            'language',
            'word_count',

            # Sentiment Analysis
            'tvk_sentiment',
            'tvk_sentiment_score',
            'sentiment_reasoning',
            'vijay_mentions',
            'tvk_mentions',
            'dmk_mentions',
            'opposition_mentions',

            # AI Analysis
            'ai_summary',
            'key_topics',
            'entities_mentioned',

            # Metadata
            'is_relevant',
            'category',
            'ai_processed',
            'processing_attempts',
            'processing_error',
        ]
        read_only_fields = fields


class NewsSentimentStatsSerializer(serializers.Serializer):
    """
    Aggregated sentiment statistics
    """
    total_articles = serializers.IntegerField()
    positive_count = serializers.IntegerField()
    negative_count = serializers.IntegerField()
    neutral_count = serializers.IntegerField()
    avg_sentiment_score = serializers.FloatField()
    total_vijay_mentions = serializers.IntegerField()
    total_tvk_mentions = serializers.IntegerField()
    articles_by_source = serializers.DictField()
    articles_by_language = serializers.DictField()
    trending_topics = serializers.ListField()


class NewsSourceStatsSerializer(serializers.Serializer):
    """
    Statistics by news source
    """
    source = serializers.CharField()
    total_articles = serializers.IntegerField()
    positive_count = serializers.IntegerField()
    negative_count = serializers.IntegerField()
    neutral_count = serializers.IntegerField()
    avg_sentiment_score = serializers.FloatField()
