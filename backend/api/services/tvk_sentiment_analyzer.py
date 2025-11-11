"""
TVK/Vijay Sentiment Analyzer
Uses LLM (OpenAI GPT-4) to analyze news articles for sentiment toward Vijay and TVK party

Analyzes:
- Overall sentiment (positive/negative/neutral)
- Vijay mentions count
- TVK mentions count
- Opposition (DMK/BJP/etc.) mentions
- Key topics extraction
- Sentiment reasoning
"""

import logging
import json
from openai import OpenAI
from django.conf import settings
from api.models import NewsArticle

logger = logging.getLogger(__name__)


class TVKSentimentAnalyzer:
    """
    Analyzes news articles for TVK/Vijay political sentiment using LLM
    """

    def __init__(self):
        # Initialize OpenAI client
        api_key = getattr(settings, 'OPENAI_API_KEY', None)
        if not api_key:
            logger.warning("OPENAI_API_KEY not set, using fallback analysis")
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key)

        self.model = "gpt-4"  # or "gpt-3.5-turbo" for faster/cheaper

    def analyze_article(self, article_text, title="", language="en"):
        """
        Analyze a news article for TVK/Vijay sentiment

        Args:
            article_text (str): Full article text
            title (str): Article title
            language (str): Article language ('en' or 'ta')

        Returns:
            dict: Analysis results
        """
        if not self.client:
            return self._fallback_analysis(article_text)

        try:
            # Construct analysis prompt
            prompt = self._build_analysis_prompt(article_text, title, language)

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a political sentiment analyzer specializing in Tamil Nadu politics. Analyze news articles for sentiment toward Vijay (Thalapathy) and his TVK (Thamizhaga Vettri Kazhagam) party."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for consistent analysis
                response_format={"type": "json_object"}
            )

            # Parse response
            result_text = response.choices[0].message.content
            analysis = json.loads(result_text)

            # Validate and normalize response
            return self._normalize_analysis(analysis)

        except Exception as e:
            logger.error(f"LLM analysis failed: {str(e)}")
            return self._fallback_analysis(article_text)

    def _build_analysis_prompt(self, article_text, title, language):
        """
        Build the LLM analysis prompt
        """
        language_note = "This article is in Tamil." if language == 'ta' else ""

        prompt = f"""
Analyze this Tamil Nadu political news article for sentiment toward Vijay (Thalapathy) and his TVK party.

{language_note}

Title: {title}

Article:
{article_text[:4000]}

Provide analysis in JSON format with these exact fields:

{{
  "tvk_sentiment": "positive|negative|neutral",
  "tvk_sentiment_score": 0.0-1.0,
  "sentiment_reasoning": "Brief explanation of why this sentiment was assigned",

  "vijay_mentions": count of direct mentions of "Vijay" or "Thalapathy",
  "tvk_mentions": count of mentions of "TVK" or "Thamizhaga Vettri Kazhagam",
  "dmk_mentions": count of mentions of "DMK" or "Stalin",
  "opposition_mentions": count of other party mentions (BJP, AIADMK, Congress, etc.),

  "key_topics": ["topic1", "topic2", "topic3"],
  "entities_mentioned": ["person1", "party1", "place1"],

  "is_relevant": true|false,
  "category": "politics|election|policy|governance|social_issue|economy|other",

  "ai_summary": "2-3 sentence summary of the article"
}}

Sentiment Scoring Guide:
- 0.0-0.3 = Negative (critical, attacking, unfavorable coverage)
- 0.4-0.6 = Neutral (balanced reporting, no clear bias)
- 0.7-1.0 = Positive (favorable, supportive, praising coverage)

Examples:
- If article praises Vijay's stance on NEET → positive (0.8-0.9)
- If article criticizes TVK policies → negative (0.2-0.3)
- If article mentions Vijay neutrally → neutral (0.5)
- If article doesn't mention TVK/Vijay → neutral (0.5), is_relevant=false

Key Topics should be from: ["neet", "jobs", "employment", "education", "water_crisis", "fishermen", "farmers", "youth", "women", "corruption", "governance", "cauvery", "social_justice", "healthcare", "infrastructure", "economy", "environment", "human_rights", "language", "cultural_identity"]

Focus on:
1. How is Vijay/TVK portrayed?
2. Is the coverage favorable or unfavorable?
3. What is the overall tone?
4. Are there quotes from Vijay or TVK leaders?
5. How does this compare to coverage of other parties?
"""
        return prompt

    def _normalize_analysis(self, analysis):
        """
        Normalize and validate LLM analysis results
        """
        # Ensure required fields exist with defaults
        normalized = {
            'tvk_sentiment': analysis.get('tvk_sentiment', 'neutral'),
            'tvk_sentiment_score': float(analysis.get('tvk_sentiment_score', 0.5)),
            'sentiment_reasoning': analysis.get('sentiment_reasoning', ''),

            'vijay_mentions': int(analysis.get('vijay_mentions', 0)),
            'tvk_mentions': int(analysis.get('tvk_mentions', 0)),
            'dmk_mentions': int(analysis.get('dmk_mentions', 0)),
            'opposition_mentions': int(analysis.get('opposition_mentions', 0)),

            'key_topics': analysis.get('key_topics', []),
            'entities_mentioned': analysis.get('entities_mentioned', []),

            'is_relevant': analysis.get('is_relevant', True),
            'category': analysis.get('category', 'politics'),

            'ai_summary': analysis.get('ai_summary', ''),
        }

        # Validate sentiment
        if normalized['tvk_sentiment'] not in ['positive', 'negative', 'neutral']:
            normalized['tvk_sentiment'] = 'neutral'

        # Clamp sentiment score
        if normalized['tvk_sentiment_score'] < 0.0:
            normalized['tvk_sentiment_score'] = 0.0
        elif normalized['tvk_sentiment_score'] > 1.0:
            normalized['tvk_sentiment_score'] = 1.0

        return normalized

    def _fallback_analysis(self, article_text):
        """
        Simple keyword-based fallback when LLM is not available
        """
        text_lower = article_text.lower()

        # Count mentions
        vijay_mentions = (
            text_lower.count('vijay') +
            text_lower.count('thalapathy') +
            text_lower.count('தளபதி')
        )
        tvk_mentions = (
            text_lower.count('tvk') +
            text_lower.count('thamizhaga vettri kazhagam') +
            text_lower.count('tamizhaga vetri kazhagam')
        )
        dmk_mentions = text_lower.count('dmk') + text_lower.count('stalin')

        # Simple sentiment (keyword-based)
        positive_keywords = ['praise', 'support', 'welcome', 'appreciate', 'commend', 'endorse']
        negative_keywords = ['criticize', 'oppose', 'condemn', 'attack', 'reject', 'slam']

        positive_count = sum(1 for kw in positive_keywords if kw in text_lower)
        negative_count = sum(1 for kw in negative_keywords if kw in text_lower)

        if positive_count > negative_count:
            sentiment = 'positive'
            score = 0.7
        elif negative_count > positive_count:
            sentiment = 'negative'
            score = 0.3
        else:
            sentiment = 'neutral'
            score = 0.5

        is_relevant = (vijay_mentions + tvk_mentions) > 0

        return {
            'tvk_sentiment': sentiment,
            'tvk_sentiment_score': score,
            'sentiment_reasoning': 'Fallback keyword-based analysis',
            'vijay_mentions': vijay_mentions,
            'tvk_mentions': tvk_mentions,
            'dmk_mentions': dmk_mentions,
            'opposition_mentions': 0,
            'key_topics': [],
            'entities_mentioned': [],
            'is_relevant': is_relevant,
            'category': 'politics',
            'ai_summary': article_text[:200] + '...',
        }

    def process_article(self, article_id):
        """
        Process a NewsArticle from database

        Args:
            article_id: UUID of NewsArticle

        Returns:
            bool: Success status
        """
        try:
            article = NewsArticle.objects.get(id=article_id)

            # Skip if already processed
            if article.ai_processed:
                logger.info(f"Article {article_id} already processed")
                return True

            # Analyze
            logger.info(f"Analyzing article: {article.title[:50]}...")
            analysis = self.analyze_article(
                article_text=article.article_text,
                title=article.title,
                language=article.language
            )

            # Update article with analysis results
            article.tvk_sentiment = analysis['tvk_sentiment']
            article.tvk_sentiment_score = analysis['tvk_sentiment_score']
            article.sentiment_reasoning = analysis['sentiment_reasoning']

            article.vijay_mentions = analysis['vijay_mentions']
            article.tvk_mentions = analysis['tvk_mentions']
            article.dmk_mentions = analysis['dmk_mentions']
            article.opposition_mentions = analysis['opposition_mentions']

            article.key_topics = analysis['key_topics']
            article.entities_mentioned = analysis['entities_mentioned']

            article.is_relevant = analysis['is_relevant']
            article.category = analysis['category']

            article.ai_summary = analysis['ai_summary']
            article.ai_processed = True
            article.processing_attempts += 1

            article.save()

            logger.info(f"✅ Analysis complete: {analysis['tvk_sentiment']} ({analysis['tvk_sentiment_score']})")
            return True

        except NewsArticle.DoesNotExist:
            logger.error(f"Article {article_id} not found")
            return False
        except Exception as e:
            logger.error(f"Error processing article {article_id}: {str(e)}")

            # Update error status
            try:
                article = NewsArticle.objects.get(id=article_id)
                article.processing_error = str(e)
                article.processing_attempts += 1
                article.save()
            except:
                pass

            return False

    def process_unprocessed_articles(self, batch_size=10):
        """
        Process all unprocessed articles in batches

        Args:
            batch_size (int): Number of articles to process

        Returns:
            tuple: (success_count, error_count)
        """
        # Get unprocessed articles
        unprocessed = NewsArticle.objects.filter(
            ai_processed=False,
            processing_attempts__lt=3  # Max 3 attempts
        ).order_by('-scraped_at')[:batch_size]

        success_count = 0
        error_count = 0

        for article in unprocessed:
            if self.process_article(article.id):
                success_count += 1
            else:
                error_count += 1

        logger.info(f"📊 Batch processing complete: {success_count} success, {error_count} errors")
        return success_count, error_count


# =====================================================
# STANDALONE FUNCTIONS
# =====================================================

def analyze_article_sentiment(article_id):
    """
    Analyze a single article's sentiment
    """
    analyzer = TVKSentimentAnalyzer()
    return analyzer.process_article(article_id)


def analyze_all_unprocessed_articles():
    """
    Analyze all unprocessed articles
    """
    analyzer = TVKSentimentAnalyzer()
    return analyzer.process_unprocessed_articles(batch_size=50)
