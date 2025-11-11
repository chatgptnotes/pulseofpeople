"""
Tamil Nadu Political News Scraper
Scrapes Tamil and English news articles every 6 hours for TVK/Vijay political coverage

Supported Sources:
- Tamil: Dinamalar, Dinakaran, Maalaimalar, Polimer News
- English: The Hindu (TN), Times of India (Chennai), Indian Express (TN)
"""

import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import feedparser
from django.utils import timezone
from api.models import NewsArticle

logger = logging.getLogger(__name__)


class TamilNaduNewsScraper:
    """
    Main scraper class for Tamil Nadu political news
    """

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.timeout = 15
        self.max_articles_per_source = 20

    # =====================================================
    # TAMIL NEWS SOURCES
    # =====================================================

    def scrape_dinamalar(self):
        """
        Scrape Dinamalar Tamil News (Chennai/TN Politics)
        """
        articles = []
        try:
            # Dinamalar Chennai/TN News URL
            url = "https://www.dinamalar.com/chennai_news.asp"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find news articles (adjust selectors based on actual site structure)
            news_items = soup.find_all('div', class_='NewsList', limit=self.max_articles_per_source)

            for item in news_items:
                try:
                    title_tag = item.find('a')
                    if not title_tag:
                        continue

                    title = title_tag.get_text(strip=True)
                    relative_url = title_tag.get('href', '')
                    article_url = urljoin(url, relative_url)

                    # Filter for political keywords
                    if not self._is_political_article(title):
                        continue

                    # Fetch full article
                    article_data = self._extract_article_from_url(
                        article_url,
                        source='Dinamalar',
                        language='ta'
                    )

                    if article_data:
                        articles.append(article_data)

                except Exception as e:
                    logger.error(f"Error parsing Dinamalar article: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Error scraping Dinamalar: {str(e)}")

        return articles

    def scrape_dinakaran(self):
        """
        Scrape Dinakaran Tamil News (Tamil Nadu section)
        """
        articles = []
        try:
            url = "https://www.dinakaran.com/tamilnadu"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find news articles
            news_items = soup.find_all('div', class_='news-item', limit=self.max_articles_per_source)

            for item in news_items:
                try:
                    title_tag = item.find('h2') or item.find('h3')
                    link_tag = item.find('a')

                    if not title_tag or not link_tag:
                        continue

                    title = title_tag.get_text(strip=True)
                    article_url = urljoin(url, link_tag.get('href', ''))

                    if not self._is_political_article(title):
                        continue

                    article_data = self._extract_article_from_url(
                        article_url,
                        source='Dinakaran',
                        language='ta'
                    )

                    if article_data:
                        articles.append(article_data)

                except Exception as e:
                    logger.error(f"Error parsing Dinakaran article: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Error scraping Dinakaran: {str(e)}")

        return articles

    # =====================================================
    # ENGLISH NEWS SOURCES
    # =====================================================

    def scrape_the_hindu_tn(self):
        """
        Scrape The Hindu Tamil Nadu Section
        """
        articles = []
        try:
            # The Hindu TN News RSS feed
            rss_url = "https://www.thehindu.com/news/national/tamil-nadu/feeder/default.rss"
            feed = feedparser.parse(rss_url)

            for entry in feed.entries[:self.max_articles_per_source]:
                try:
                    title = entry.title
                    article_url = entry.link
                    published = entry.get('published_parsed', None)

                    if not self._is_political_article(title):
                        continue

                    article_data = self._extract_article_from_url(
                        article_url,
                        source='The Hindu',
                        language='en',
                        published_date=published
                    )

                    if article_data:
                        articles.append(article_data)

                except Exception as e:
                    logger.error(f"Error parsing The Hindu article: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Error scraping The Hindu: {str(e)}")

        return articles

    def scrape_times_of_india_chennai(self):
        """
        Scrape Times of India Chennai Section
        """
        articles = []
        try:
            url = "https://timesofindia.indiatimes.com/city/chennai"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find news articles
            news_items = soup.find_all('div', class_='uwU81', limit=self.max_articles_per_source)

            for item in news_items:
                try:
                    link_tag = item.find('a')
                    if not link_tag:
                        continue

                    title = link_tag.get_text(strip=True)
                    article_url = urljoin(url, link_tag.get('href', ''))

                    if not self._is_political_article(title):
                        continue

                    article_data = self._extract_article_from_url(
                        article_url,
                        source='Times of India',
                        language='en'
                    )

                    if article_data:
                        articles.append(article_data)

                except Exception as e:
                    logger.error(f"Error parsing TOI article: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Error scraping Times of India: {str(e)}")

        return articles

    def scrape_indian_express_tn(self):
        """
        Scrape Indian Express Tamil Nadu Section
        """
        articles = []
        try:
            url = "https://indianexpress.com/section/cities/chennai/"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find news articles
            news_items = soup.find_all('div', class_='articles', limit=self.max_articles_per_source)

            for item in news_items:
                try:
                    link_tag = item.find('h2').find('a') if item.find('h2') else None
                    if not link_tag:
                        continue

                    title = link_tag.get_text(strip=True)
                    article_url = link_tag.get('href', '')

                    if not self._is_political_article(title):
                        continue

                    article_data = self._extract_article_from_url(
                        article_url,
                        source='Indian Express',
                        language='en'
                    )

                    if article_data:
                        articles.append(article_data)

                except Exception as e:
                    logger.error(f"Error parsing Indian Express article: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Error scraping Indian Express: {str(e)}")

        return articles

    # =====================================================
    # HELPER METHODS
    # =====================================================

    def _extract_article_from_url(self, url, source, language, published_date=None):
        """
        Extract full article content from URL
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title
            title_tag = soup.find('h1')
            title = title_tag.get_text(strip=True) if title_tag else "No Title"

            # Extract article text (combine all paragraph tags)
            paragraphs = soup.find_all('p')
            article_text = ' '.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])

            # Extract author (common patterns)
            author = None
            author_tag = soup.find('span', class_='author') or soup.find('div', class_='author')
            if author_tag:
                author = author_tag.get_text(strip=True)

            # Published date
            if not published_date:
                published_date = timezone.now()
            elif isinstance(published_date, tuple):
                # Convert time.struct_time to datetime
                import time
                published_date = datetime.fromtimestamp(time.mktime(published_date))
                published_date = timezone.make_aware(published_date)

            # Validate article length
            if len(article_text) < 100:
                logger.warning(f"Article too short, skipping: {url}")
                return None

            return {
                'title': title,
                'url': url,
                'source': source,
                'author': author,
                'article_text': article_text,
                'language': language,
                'published_at': published_date,
            }

        except Exception as e:
            logger.error(f"Error extracting article from {url}: {str(e)}")
            return None

    def _is_political_article(self, title):
        """
        Check if article title contains political keywords
        """
        political_keywords = [
            # Parties
            'tvk', 'vijay', 'thalapathy', 'dmk', 'stalin', 'aiadmk', 'bjp', 'congress',
            'nda', 'upa', 'admk',

            # Political Terms (English)
            'election', 'politics', 'government', 'minister', 'mla', 'mp', 'assembly',
            'parliament', 'campaign', 'rally', 'party', 'coalition', 'manifesto',
            'policy', 'governor', 'chief minister', 'cm', 'pm',

            # Political Terms (Tamil - romanized)
            'thalaivar', 'kalaignar', 'puratchi', 'amma', 'neta', 'arasiyal',

            # Social Issues (TN-specific)
            'neet', 'cauvery', 'kaveri', 'water', 'fishermen', 'farmer',
            'protest', 'strike', 'bandh',

            # Tamil Nadu
            'tamil nadu', 'chennai', 'madurai', 'coimbatore', 'trichy',
        ]

        title_lower = title.lower()
        return any(keyword in title_lower for keyword in political_keywords)

    # =====================================================
    # MAIN SCRAPING METHODS
    # =====================================================

    def scrape_all_tamil_sources(self):
        """
        Scrape all Tamil news sources
        """
        logger.info("Starting Tamil news scraping...")
        all_articles = []

        sources = [
            ('Dinamalar', self.scrape_dinamalar),
            ('Dinakaran', self.scrape_dinakaran),
        ]

        for source_name, scraper_func in sources:
            try:
                logger.info(f"Scraping {source_name}...")
                articles = scraper_func()
                all_articles.extend(articles)
                logger.info(f"✅ {source_name}: {len(articles)} articles")
            except Exception as e:
                logger.error(f"❌ {source_name} failed: {str(e)}")

        return all_articles

    def scrape_all_english_sources(self):
        """
        Scrape all English news sources
        """
        logger.info("Starting English news scraping...")
        all_articles = []

        sources = [
            ('The Hindu TN', self.scrape_the_hindu_tn),
            ('Times of India Chennai', self.scrape_times_of_india_chennai),
            ('Indian Express TN', self.scrape_indian_express_tn),
        ]

        for source_name, scraper_func in sources:
            try:
                logger.info(f"Scraping {source_name}...")
                articles = scraper_func()
                all_articles.extend(articles)
                logger.info(f"✅ {source_name}: {len(articles)} articles")
            except Exception as e:
                logger.error(f"❌ {source_name} failed: {str(e)}")

        return all_articles

    def scrape_all_sources(self):
        """
        Scrape all Tamil and English news sources
        """
        logger.info("🚀 Starting full news scraping cycle...")

        tamil_articles = self.scrape_all_tamil_sources()
        english_articles = self.scrape_all_english_sources()

        all_articles = tamil_articles + english_articles

        logger.info(f"📊 Total articles scraped: {len(all_articles)}")
        logger.info(f"   Tamil: {len(tamil_articles)}")
        logger.info(f"   English: {len(english_articles)}")

        return all_articles


# =====================================================
# STANDALONE FUNCTIONS
# =====================================================

def scrape_tamil_nadu_news():
    """
    Main function to scrape Tamil Nadu news
    Returns list of article data dictionaries
    """
    scraper = TamilNaduNewsScraper()
    return scraper.scrape_all_sources()


def save_articles_to_database(articles):
    """
    Save scraped articles to database
    """
    saved_count = 0
    duplicate_count = 0
    error_count = 0

    for article_data in articles:
        try:
            # Check if article already exists
            existing = NewsArticle.objects.filter(url=article_data['url']).first()
            if existing:
                duplicate_count += 1
                continue

            # Create new article (without AI processing yet)
            article = NewsArticle.objects.create(
                title=article_data['title'],
                url=article_data['url'],
                source=article_data['source'],
                author=article_data.get('author'),
                article_text=article_data['article_text'],
                language=article_data['language'],
                published_at=article_data['published_at'],
                ai_processed=False,  # Will be processed by sentiment analyzer
            )

            saved_count += 1
            logger.info(f"✅ Saved: {article.title[:50]}...")

        except Exception as e:
            error_count += 1
            logger.error(f"❌ Error saving article: {str(e)}")

    logger.info(f"📊 Save Summary:")
    logger.info(f"   Saved: {saved_count}")
    logger.info(f"   Duplicates: {duplicate_count}")
    logger.info(f"   Errors: {error_count}")

    return saved_count
