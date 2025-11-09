"""
Django Management Command: Generate Realistic Social Media Posts
==================================================================
Generate 20,000 realistic social media posts for Pulse of People platform
with Tamil Nadu political context and realistic engagement patterns.

Usage:
    python manage.py generate_social_posts
    python manage.py generate_social_posts --count 10000
    python manage.py generate_social_posts --platform twitter --count 5000
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from api.models import (
    SocialMediaPost, Campaign, IssueCategory, District, State, Constituency
)
from datetime import datetime, timedelta
import random
import uuid
from decimal import Decimal


class Command(BaseCommand):
    help = 'Generate 20,000 realistic social media posts with Tamil Nadu political context'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20000,
            help='Number of posts to generate (default: 20000)'
        )
        parser.add_argument(
            '--platform',
            type=str,
            default='all',
            help='Specific platform: twitter, facebook, instagram, youtube, news, all (default: all)'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=500,
            help='Batch size for bulk creation (default: 500)'
        )
        parser.add_argument(
            '--generate-sql',
            action='store_true',
            help='Also generate Supabase SQL seed file'
        )

    def handle(self, *args, **options):
        count = options['count']
        platform_filter = options['platform']
        batch_size = options['batch_size']
        generate_sql = options['generate_sql']

        self.stdout.write(self.style.SUCCESS(f'\n=== Generating {count:,} Social Media Posts ===\n'))

        # Initialize data
        self._initialize_data()

        # Generate posts
        posts = self._generate_posts(count, platform_filter)

        # Save to database
        self._save_posts_bulk(posts, batch_size)

        # Generate SQL if requested
        if generate_sql:
            self._generate_supabase_sql(posts)

        # Print statistics
        self._print_statistics(posts)

        self.stdout.write(self.style.SUCCESS(f'\n✓ Successfully generated {len(posts):,} social media posts!\n'))

    def _initialize_data(self):
        """Initialize reference data"""
        self.stdout.write('Loading reference data...')

        # Get Tamil Nadu state and districts
        self.tamil_nadu = State.objects.filter(code='TN').first()
        self.districts = list(District.objects.filter(state=self.tamil_nadu)) if self.tamil_nadu else []

        # Get campaigns (especially TVK)
        self.campaigns = list(Campaign.objects.all())
        self.tvk_campaigns = [c for c in self.campaigns if 'TVK' in c.campaign_name or 'Vijay' in c.campaign_name]

        # Get issue categories
        self.issues = list(IssueCategory.objects.all())

        self.stdout.write(self.style.SUCCESS(f'  - {len(self.districts)} districts loaded'))
        self.stdout.write(self.style.SUCCESS(f'  - {len(self.campaigns)} campaigns loaded'))
        self.stdout.write(self.style.SUCCESS(f'  - {len(self.issues)} issue categories loaded\n'))

    def _generate_posts(self, count, platform_filter):
        """Generate realistic social media posts"""
        posts = []

        # Platform distribution
        platform_distribution = {
            'twitter': 0.50,      # 50% - 10,000 posts
            'facebook': 0.30,     # 30% - 6,000 posts
            'instagram': 0.15,    # 15% - 3,000 posts
            'youtube': 0.03,      # 3% - 600 posts
            'whatsapp': 0.02,     # 2% - 400 posts (using as 'news' equivalent)
        }

        # Calculate counts per platform
        if platform_filter == 'all':
            platform_counts = {
                platform: int(count * percentage)
                for platform, percentage in platform_distribution.items()
            }
        else:
            platform_counts = {platform_filter: count}

        self.stdout.write(f'Generating posts by platform:')
        for platform, platform_count in platform_counts.items():
            self.stdout.write(f'  - {platform}: {platform_count:,} posts')

        # Generate posts for each platform
        for platform, platform_count in platform_counts.items():
            self.stdout.write(f'\nGenerating {platform_count:,} {platform} posts...')
            for i in range(platform_count):
                post = self._generate_single_post(platform)
                posts.append(post)

                if (i + 1) % 1000 == 0:
                    self.stdout.write(f'  Progress: {i + 1:,}/{platform_count:,} ({((i + 1) / platform_count * 100):.1f}%)')

        return posts

    def _generate_single_post(self, platform):
        """Generate a single realistic post"""
        # Time distribution (last 7 days: Nov 23-30, 2024)
        end_date = datetime(2024, 11, 30, 23, 59, 59)
        start_date = end_date - timedelta(days=7)

        # Peak hours distribution
        hour_weights = {
            range(7, 9): 0.20,    # 7-9am: 20%
            range(12, 14): 0.25,  # 12-2pm: 25%
            range(18, 21): 0.35,  # 6-9pm: 35%
            range(22, 24): 0.10,  # 10pm-12am: 10%
            range(0, 7): 0.05,    # 12-7am: 5%
            range(9, 12): 0.025,  # 9am-12pm: 2.5%
            range(14, 18): 0.025, # 2-6pm: 2.5%
        }

        # Pick random day
        days_diff = random.randint(0, 6)
        post_date = end_date - timedelta(days=days_diff)

        # Weekday has 30% more volume
        is_weekday = post_date.weekday() < 5
        if is_weekday and random.random() < 0.3:
            # Boost weekday content
            pass

        # Pick hour based on weights
        hour_range = random.choices(
            list(hour_weights.keys()),
            weights=list(hour_weights.values())
        )[0]
        hour = random.choice(list(hour_range))
        minute = random.randint(0, 59)
        second = random.randint(0, 59)

        posted_at = post_date.replace(hour=hour, minute=minute, second=second)

        # Content type weights
        content_types = {
            'water_crisis': 0.25,
            'tvk_vijay': 0.25,
            'neet_protest': 0.15,
            'cauvery_water': 0.15,
            'fishermen': 0.10,
            'development': 0.10,
        }

        content_type = random.choices(
            list(content_types.keys()),
            weights=list(content_types.values())
        )[0]

        # Generate content and metadata
        content_data = self._generate_content(content_type, platform)

        # Engagement tier
        engagement_tier = self._determine_engagement_tier()
        engagement_data = self._generate_engagement(engagement_tier, platform)

        # Author type
        author_type = self._determine_author_type()
        author_data = self._generate_author(author_type)

        # Create post object
        post = SocialMediaPost(
            platform=platform,
            post_content=content_data['text'],
            post_url=self._generate_post_url(platform, content_data['post_id']),
            post_id=content_data['post_id'],
            posted_at=posted_at,
            reach=engagement_data['reach'],
            impressions=engagement_data['impressions'],
            engagement_count=engagement_data['engagement_count'],
            likes=engagement_data['likes'],
            shares=engagement_data['shares'],
            comments_count=engagement_data['comments'],
            sentiment_score=content_data['sentiment_score'],
            campaign=content_data.get('campaign'),
            posted_by=None,  # Anonymous/scraped posts
            is_published=True,
            is_promoted=engagement_tier == 'viral',
            hashtags=content_data['hashtags'],
            mentions=content_data.get('mentions', []),
        )

        return post

    def _generate_content(self, content_type, platform):
        """Generate post content based on type"""
        # District for geographic tagging (70% tagged)
        district = random.choice(self.districts) if self.districts and random.random() < 0.7 else None

        # Get district name distribution
        district_weights = {
            'Chennai': 0.25,
            'Coimbatore': 0.15,
            'Madurai': 0.10,
            'Salem': 0.08,
            'Tiruchirappalli': 0.07,
            'Tirunelveli': 0.06,
            'Erode': 0.05,
            'Vellore': 0.05,
        }

        if district:
            district_name = district.name
        elif random.random() < 0.5:
            # Use weighted district
            district_name = random.choices(
                list(district_weights.keys()),
                weights=list(district_weights.values())
            )[0]
        else:
            district_name = random.choice([
                'Chennai', 'Coimbatore', 'Madurai', 'Salem', 'Tiruchirappalli',
                'Tirunelveli', 'Erode', 'Vellore', 'Thanjavur', 'Kanyakumari'
            ])

        # Content templates by type
        templates = {
            'water_crisis': [
                f"Water shortage in {district_name}! When will this crisis end? #TNWaterCrisis #SaveTamilNadu",
                f"Chennai residents struggle with depleted groundwater. We need action NOW! #ChennaiWater #WaterScarcity",
                f"{district_name} water levels dropped 10 meters. Government sleeping? #WaterCrisis #TamilNadu",
                f"No water supply for 3 days in {district_name}. Families suffering! #TNWater #EmergencyNow",
                f"Water crisis worsening in {district_name}. Politicians busy with elections, people dying of thirst! #WaterRights",
                f"Ground water depleted in {district_name}. Industries shut down. Where is the solution? #IndustrialCrisis #Water",
            ],
            'tvk_vijay': [
                f"Vijay's speech on jobs resonated with youth! #TVK #VijayForTN #TamilNaduFuture",
                f"Finally a leader who speaks for common people! @TVKOfficial #TVKVision2026",
                f"Vijay addresses NEET issue head-on. This is the leadership we need! #StopNEET #TVK",
                f"TVK manifesto promises corruption-free governance. Fresh air for TN politics! #CleanPolitics #TVK",
                f"Attended TVK rally in {district_name}. Crowd was massive! Youth power! #TVKRally #VijayForTN",
                f"Vijay's vision for employment generation gives hope to graduates. #JobsForTN #TVK",
                f"TVK's focus on fishermen, farmers, and youth is exactly what TN needs! #TVKPolicies",
                f"Unlike traditional parties, TVK actually listens to people! #NewPolitics #TVK",
            ],
            'neet_protest': [
                f"NEET destroyed dreams of rural students. When will TN get exemption? #NEETHurts #StopNEET",
                f"Another student lost to NEET pressure. How many more? #StopNEET #TNStudents",
                f"Medical seats going to coaching class rich kids. Where is social justice? #NEETInjustice",
                f"TN students scoring 100% denied admission due to NEET. This is wrong! #AbolishNEET",
                f"Suicide rate among NEET aspirants rising. Government must act! #NEETKills #SaveStudents",
                f"TVK promises to fight NEET. Finally someone takes this seriously! #TVK #StopNEET",
            ],
            'cauvery_water': [
                f"Karnataka not releasing Cauvery water. Delta farmers suffering! #CauveryWater #SaveDeltaFarmers",
                f"Thanjavur farmers protest for water rights. Where is justice? #CauveryDispute #FarmersFirst",
                f"Crops dying in delta region. Cauvery water not released. Farmers will starve! #CauveryWater",
                f"Supreme Court order on Cauvery ignored. TN farmers paying the price! #WaterRights #Cauvery",
                f"Delta region facing worst drought. Need Cauvery water immediately! #FarmersCrisis",
            ],
            'fishermen': [
                f"530 TN fishermen arrested by SL Navy this year. Enough is enough! #TNFishermen #SriLanka",
                f"Ramanathapuram fishermen families starving. No boats, no livelihood #FishermenRights",
                f"Indian government silent on fishermen arrests. Who will protect our people? #TNFishermen",
                f"Fishermen demand protection from SL Navy. Diplomatic failure! #FishermenSafety",
                f"TVK promises dedicated ministry for fishermen welfare. Finally someone cares! #TVK #Fishermen",
            ],
            'development': [
                f"New infrastructure projects announced for {district_name} district #TNDevelopment",
                f"Healthcare expansion in rural areas. Good move! #TNHealthcare #RuralDevelopment",
                f"TVK's vision for corruption-free governance inspiring! #CleanPolitics #TVK",
                f"Education reforms needed in TN. Glad TVK is focusing on this! #EducationFirst #TVK",
                f"Industrial growth in {district_name}. Creating jobs for locals! #TNEconomy #Development",
                f"Smart city projects transforming {district_name}. Progress! #SmartCity #TN",
            ],
        }

        # Pick template
        text = random.choice(templates[content_type])

        # Generate hashtags based on content
        hashtag_sets = {
            'water_crisis': ['#TNWaterCrisis', '#SaveTamilNadu', '#WaterScarcity', '#ChennaiWater', '#WaterRights'],
            'tvk_vijay': ['#TVK', '#VijayForTN', '#TVKVision2026', '#TamilNaduFirst', '#CleanPolitics', '#NewPolitics'],
            'neet_protest': ['#StopNEET', '#NEETHurts', '#TNStudents', '#AbolishNEET', '#NEETKills'],
            'cauvery_water': ['#CauveryWater', '#CauveryDispute', '#SaveDeltaFarmers', '#FarmersFirst', '#WaterRights'],
            'fishermen': ['#TNFishermen', '#FishermenRights', '#FishermenSafety', '#SriLanka'],
            'development': ['#TNDevelopment', '#TamilNadu', '#Progress', '#SmartCity', '#RuralDevelopment'],
        }

        # Extract hashtags from text and add more
        hashtags_in_text = [word for word in text.split() if word.startswith('#')]
        additional_hashtags = [tag for tag in hashtag_sets[content_type] if tag not in hashtags_in_text]
        all_hashtags = hashtags_in_text + random.sample(additional_hashtags, min(2, len(additional_hashtags)))

        # Sentiment scoring
        sentiment_mapping = {
            'water_crisis': (0.2, 0.4),    # Negative
            'tvk_vijay': (0.7, 0.9),       # Positive
            'neet_protest': (0.3, 0.5),    # Negative
            'cauvery_water': (0.25, 0.45), # Negative
            'fishermen': (0.3, 0.5),       # Negative
            'development': (0.65, 0.85),   # Positive
        }

        sentiment_range = sentiment_mapping[content_type]
        sentiment_score = Decimal(str(random.uniform(*sentiment_range))).quantize(Decimal('0.01'))

        # Link to TVK campaign if relevant
        campaign = None
        if content_type == 'tvk_vijay' and self.tvk_campaigns:
            campaign = random.choice(self.tvk_campaigns)
        elif random.random() < 0.1 and self.campaigns:  # 10% linked to other campaigns
            campaign = random.choice(self.campaigns)

        # Generate platform-specific post ID
        post_id = self._generate_platform_post_id(platform)

        return {
            'text': text,
            'hashtags': all_hashtags,
            'sentiment_score': sentiment_score,
            'campaign': campaign,
            'post_id': post_id,
            'mentions': self._generate_mentions(content_type),
        }

    def _generate_platform_post_id(self, platform):
        """Generate realistic platform-specific post IDs"""
        if platform == 'twitter':
            # Twitter uses numeric IDs
            return str(random.randint(1000000000000000000, 9999999999999999999))
        elif platform == 'facebook':
            # Facebook uses numeric IDs
            return str(random.randint(100000000000000, 999999999999999))
        elif platform == 'instagram':
            # Instagram uses alphanumeric codes
            chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
            return ''.join(random.choices(chars, k=11))
        elif platform == 'youtube':
            # YouTube video IDs
            chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
            return ''.join(random.choices(chars, k=11))
        else:  # whatsapp/news
            return str(uuid.uuid4())

    def _generate_post_url(self, platform, post_id):
        """Generate platform-specific URLs"""
        url_templates = {
            'twitter': f'https://twitter.com/user/status/{post_id}',
            'facebook': f'https://facebook.com/post/{post_id}',
            'instagram': f'https://instagram.com/p/{post_id}/',
            'youtube': f'https://youtube.com/watch?v={post_id}',
            'whatsapp': '',  # WhatsApp doesn't have public URLs
        }
        return url_templates.get(platform, '')

    def _generate_mentions(self, content_type):
        """Generate mentions for posts"""
        mentions_sets = {
            'tvk_vijay': ['@TVKOfficial', '@ActorVijay', '@TVKMedia'],
            'water_crisis': ['@TNGovt', '@ChennaiMetroWater', '@CMOTamilNadu'],
            'neet_protest': ['@TNGovt', '@CMOTamilNadu', '@EducationMinTN'],
            'cauvery_water': ['@TNGovt', '@KarnatakaGovt', '@CauveryAuthority'],
            'fishermen': ['@TNGovt', '@CoastGuardIndia', '@MEAIndia'],
            'development': ['@TNGovt', '@CMOTamilNadu'],
        }

        mentions = mentions_sets.get(content_type, [])
        # Return 0-2 mentions
        return random.sample(mentions, k=min(random.randint(0, 2), len(mentions)))

    def _determine_engagement_tier(self):
        """Determine engagement tier based on probability"""
        tier_probabilities = {
            'viral': 0.05,        # 5% - Viral posts
            'high': 0.15,         # 15% - High engagement
            'medium': 0.40,       # 40% - Medium engagement
            'low': 0.40,          # 40% - Low engagement
        }

        return random.choices(
            list(tier_probabilities.keys()),
            weights=list(tier_probabilities.values())
        )[0]

    def _generate_engagement(self, tier, platform):
        """Generate engagement metrics based on tier and platform"""
        # Platform multipliers
        platform_multipliers = {
            'twitter': 1.0,
            'facebook': 0.8,
            'instagram': 0.9,
            'youtube': 1.2,
            'whatsapp': 0.3,
        }

        multiplier = platform_multipliers.get(platform, 1.0)

        # Base ranges by tier
        engagement_ranges = {
            'viral': {
                'likes': (5000, 50000),
                'shares': (1000, 10000),
                'comments': (500, 5000),
                'reach': (50000, 500000),
                'impressions': (100000, 1000000),
            },
            'high': {
                'likes': (500, 5000),
                'shares': (100, 1000),
                'comments': (50, 500),
                'reach': (5000, 50000),
                'impressions': (10000, 100000),
            },
            'medium': {
                'likes': (50, 500),
                'shares': (10, 100),
                'comments': (5, 50),
                'reach': (500, 5000),
                'impressions': (1000, 10000),
            },
            'low': {
                'likes': (5, 50),
                'shares': (0, 10),
                'comments': (0, 5),
                'reach': (50, 500),
                'impressions': (100, 1000),
            },
        }

        ranges = engagement_ranges[tier]

        # Apply platform multiplier
        likes = int(random.randint(*ranges['likes']) * multiplier)
        shares = int(random.randint(*ranges['shares']) * multiplier)
        comments = int(random.randint(*ranges['comments']) * multiplier)
        reach = int(random.randint(*ranges['reach']) * multiplier)
        impressions = int(random.randint(*ranges['impressions']) * multiplier)

        # Engagement count = likes + shares + comments
        engagement_count = likes + shares + comments

        return {
            'likes': likes,
            'shares': shares,
            'comments': comments,
            'reach': reach,
            'impressions': impressions,
            'engagement_count': engagement_count,
        }

    def _determine_author_type(self):
        """Determine author type"""
        author_types = {
            'citizen': 0.60,      # 60% - Regular citizens
            'political': 0.20,    # 20% - Political accounts
            'media': 0.10,        # 10% - Media handles
            'influencer': 0.05,   # 5% - Influencers
            'anonymous': 0.05,    # 5% - Anonymous
        }

        return random.choices(
            list(author_types.keys()),
            weights=list(author_types.values())
        )[0]

    def _generate_author(self, author_type):
        """Generate author data (for metadata)"""
        # Indian names pool
        first_names = [
            'Rajesh', 'Priya', 'Karthik', 'Divya', 'Arun', 'Lakshmi', 'Vijay',
            'Anjali', 'Kumar', 'Meera', 'Ravi', 'Sowmya', 'Suresh', 'Kavitha',
            'Ganesh', 'Deepa', 'Mahesh', 'Sangeetha', 'Prakash', 'Nithya'
        ]
        last_names = [
            'Kumar', 'Raj', 'Krishnan', 'Iyer', 'Naidu', 'Reddy', 'Pillai',
            'Nair', 'Menon', 'Sharma', 'Gupta', 'Singh', 'Patel'
        ]

        if author_type == 'citizen':
            return f"{random.choice(first_names)} {random.choice(last_names)}"
        elif author_type == 'political':
            parties = ['TVK', 'DMK', 'AIADMK', 'BJP', 'Congress']
            return f"{random.choice(parties)} {random.choice(['Official', 'TN', 'Youth', 'Media'])}"
        elif author_type == 'media':
            return random.choice(['TNNews24', 'ChennaiTimes', 'TamilNaduToday', 'TNExpress', 'DailyThanthi'])
        elif author_type == 'influencer':
            return f"{random.choice(first_names)}_{random.choice(['TN', 'Chennai', 'Writes', 'Speaks'])}"
        else:  # anonymous
            return f"Anonymous_{random.randint(1000, 9999)}"

    def _save_posts_bulk(self, posts, batch_size):
        """Save posts to database in batches"""
        self.stdout.write(f'\nSaving {len(posts):,} posts to database...')

        total_saved = 0
        for i in range(0, len(posts), batch_size):
            batch = posts[i:i + batch_size]

            with transaction.atomic():
                SocialMediaPost.objects.bulk_create(batch, batch_size=batch_size)

            total_saved += len(batch)
            self.stdout.write(f'  Saved batch {i // batch_size + 1}: {total_saved:,}/{len(posts):,} posts')

        self.stdout.write(self.style.SUCCESS(f'✓ All posts saved to database\n'))

    def _generate_supabase_sql(self, posts):
        """Generate Supabase SQL seed file"""
        sql_file_path = '/Users/murali/Applications/pulseofpeople/frontend/supabase/seeds/social_posts_seed.sql'

        self.stdout.write(f'\nGenerating Supabase SQL seed file...')

        sql_lines = [
            '-- Social Media Posts Seed Data',
            '-- Generated: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            '-- Total posts: ' + str(len(posts)),
            '',
            '-- Drop existing data (optional)',
            '-- TRUNCATE TABLE social_posts CASCADE;',
            '',
            '-- Insert social media posts',
            'INSERT INTO social_posts (',
            '    id, platform, post_content, post_url, post_id, posted_at,',
            '    reach, impressions, engagement_count, likes, shares, comments_count,',
            '    sentiment_score, campaign_id, is_published, is_promoted, hashtags, mentions,',
            '    created_at, updated_at',
            ') VALUES',
        ]

        # Generate INSERT statements
        for idx, post in enumerate(posts):
            # Escape single quotes in content
            content = post.post_content.replace("'", "''")

            # Format hashtags and mentions as PostgreSQL arrays
            hashtags_str = '{' + ','.join(f'"{tag}"' for tag in post.hashtags) + '}'
            mentions_str = '{' + ','.join(f'"{m}"' for m in post.mentions) + '}'

            # Generate UUID for id
            post_uuid = str(uuid.uuid4())

            # Campaign ID (null if none)
            campaign_id = f"'{post.campaign.id}'" if post.campaign else 'NULL'

            # Format timestamp
            posted_at_str = post.posted_at.strftime('%Y-%m-%d %H:%M:%S')
            created_at_str = timezone.now().strftime('%Y-%m-%d %H:%M:%S')

            # Build INSERT row
            sql_row = f"""(
    '{post_uuid}', '{post.platform}', '{content}', '{post.post_url}', '{post.post_id}', '{posted_at_str}',
    {post.reach}, {post.impressions}, {post.engagement_count}, {post.likes}, {post.shares}, {post.comments_count},
    {post.sentiment_score}, {campaign_id}, {post.is_published}, {post.is_promoted}, ARRAY{hashtags_str}, ARRAY{mentions_str},
    '{created_at_str}', '{created_at_str}'
)"""

            if idx < len(posts) - 1:
                sql_row += ','
            else:
                sql_row += ';'

            sql_lines.append(sql_row)

        # Add indexes
        sql_lines.extend([
            '',
            '-- Create indexes for performance',
            'CREATE INDEX IF NOT EXISTS idx_social_posts_platform ON social_posts(platform);',
            'CREATE INDEX IF NOT EXISTS idx_social_posts_posted_at ON social_posts(posted_at DESC);',
            'CREATE INDEX IF NOT EXISTS idx_social_posts_campaign ON social_posts(campaign_id);',
            'CREATE INDEX IF NOT EXISTS idx_social_posts_sentiment ON social_posts(sentiment_score);',
            'CREATE INDEX IF NOT EXISTS idx_social_posts_engagement ON social_posts(engagement_count DESC);',
            '',
            '-- Analyze table for query optimization',
            'ANALYZE social_posts;',
            '',
            f'-- Total posts inserted: {len(posts)}',
        ])

        # Write to file
        with open(sql_file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sql_lines))

        self.stdout.write(self.style.SUCCESS(f'✓ Supabase SQL seed file generated: {sql_file_path}\n'))

    def _print_statistics(self, posts):
        """Print detailed statistics"""
        self.stdout.write(self.style.SUCCESS('\n=== STATISTICS ===\n'))

        # Platform breakdown
        platform_counts = {}
        for post in posts:
            platform_counts[post.platform] = platform_counts.get(post.platform, 0) + 1

        self.stdout.write('Platform Distribution:')
        for platform, count in sorted(platform_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(posts)) * 100
            self.stdout.write(f'  {platform.ljust(15)}: {count:6,} posts ({percentage:5.1f}%)')

        # Engagement tiers
        viral_count = sum(1 for p in posts if p.likes >= 5000)
        high_count = sum(1 for p in posts if 500 <= p.likes < 5000)
        medium_count = sum(1 for p in posts if 50 <= p.likes < 500)
        low_count = sum(1 for p in posts if p.likes < 50)

        self.stdout.write('\nEngagement Tiers:')
        self.stdout.write(f'  Viral (5K+ likes)  : {viral_count:6,} posts ({(viral_count / len(posts) * 100):5.1f}%)')
        self.stdout.write(f'  High (500-5K)      : {high_count:6,} posts ({(high_count / len(posts) * 100):5.1f}%)')
        self.stdout.write(f'  Medium (50-500)    : {medium_count:6,} posts ({(medium_count / len(posts) * 100):5.1f}%)')
        self.stdout.write(f'  Low (<50)          : {low_count:6,} posts ({(low_count / len(posts) * 100):5.1f}%)')

        # Sentiment distribution
        positive_count = sum(1 for p in posts if p.sentiment_score >= Decimal('0.6'))
        negative_count = sum(1 for p in posts if p.sentiment_score <= Decimal('0.4'))
        neutral_count = len(posts) - positive_count - negative_count

        self.stdout.write('\nSentiment Distribution:')
        self.stdout.write(f'  Positive (≥0.6)    : {positive_count:6,} posts ({(positive_count / len(posts) * 100):5.1f}%)')
        self.stdout.write(f'  Neutral (0.4-0.6)  : {neutral_count:6,} posts ({(neutral_count / len(posts) * 100):5.1f}%)')
        self.stdout.write(f'  Negative (≤0.4)    : {negative_count:6,} posts ({(negative_count / len(posts) * 100):5.1f}%)')

        # Engagement metrics
        total_likes = sum(p.likes for p in posts)
        total_shares = sum(p.shares for p in posts)
        total_comments = sum(p.comments_count for p in posts)
        total_reach = sum(p.reach for p in posts)

        self.stdout.write('\nTotal Engagement:')
        self.stdout.write(f'  Total Likes        : {total_likes:,}')
        self.stdout.write(f'  Total Shares       : {total_shares:,}')
        self.stdout.write(f'  Total Comments     : {total_comments:,}')
        self.stdout.write(f'  Total Reach        : {total_reach:,}')
        self.stdout.write(f'  Avg Engagement Rate: {((total_likes + total_shares + total_comments) / total_reach * 100):.2f}%')

        # Date range
        if posts:
            earliest = min(p.posted_at for p in posts)
            latest = max(p.posted_at for p in posts)
            self.stdout.write(f'\nDate Range: {earliest.strftime("%Y-%m-%d")} to {latest.strftime("%Y-%m-%d")}')
