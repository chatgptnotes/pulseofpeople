#!/usr/bin/env python3
"""
Test script for social media post generation logic
Run this to verify content templates and distributions
"""

import random
from decimal import Decimal
from datetime import datetime, timedelta

# Test content generation
def test_content_templates():
    """Test all content templates"""
    districts = ['Chennai', 'Coimbatore', 'Madurai', 'Salem']

    templates = {
        'water_crisis': [
            f"Water shortage in {random.choice(districts)}! When will this crisis end? #TNWaterCrisis #SaveTamilNadu",
            f"Chennai residents struggle with depleted groundwater. We need action NOW! #ChennaiWater #WaterScarcity",
        ],
        'tvk_vijay': [
            f"Vijay's speech on jobs resonated with youth! #TVK #VijayForTN #TamilNaduFuture",
            f"Finally a leader who speaks for common people! @TVKOfficial #TVKVision2026",
        ],
        'neet_protest': [
            f"NEET destroyed dreams of rural students. When will TN get exemption? #NEETHurts #StopNEET",
        ],
        'cauvery_water': [
            f"Karnataka not releasing Cauvery water. Delta farmers suffering! #CauveryWater #SaveDeltaFarmers",
        ],
        'fishermen': [
            f"530 TN fishermen arrested by SL Navy this year. Enough is enough! #TNFishermen #SriLanka",
        ],
        'development': [
            f"New infrastructure projects announced for {random.choice(districts)} district #TNDevelopment",
        ],
    }

    print("=== Content Template Test ===\n")
    for content_type, template_list in templates.items():
        print(f"{content_type}:")
        for template in template_list:
            print(f"  - {template}")
        print()

def test_engagement_tiers():
    """Test engagement tier distribution"""
    tier_probabilities = {
        'viral': 0.05,
        'high': 0.15,
        'medium': 0.40,
        'low': 0.40,
    }

    print("=== Engagement Tier Test ===\n")

    # Simulate 10,000 posts
    samples = 10000
    tier_counts = {tier: 0 for tier in tier_probabilities}

    for _ in range(samples):
        tier = random.choices(
            list(tier_probabilities.keys()),
            weights=list(tier_probabilities.values())
        )[0]
        tier_counts[tier] += 1

    print(f"Simulated {samples:,} posts:\n")
    for tier, count in tier_counts.items():
        expected = tier_probabilities[tier] * 100
        actual = (count / samples) * 100
        print(f"  {tier.ljust(10)}: {count:5,} posts (Expected: {expected:4.1f}%, Actual: {actual:4.1f}%)")

def test_time_distribution():
    """Test time distribution"""
    print("\n=== Time Distribution Test ===\n")

    hour_weights = {
        range(7, 9): 0.20,    # 7-9am: 20%
        range(12, 14): 0.25,  # 12-2pm: 25%
        range(18, 21): 0.35,  # 6-9pm: 35%
        range(22, 24): 0.10,  # 10pm-12am: 10%
    }

    # Simulate 10,000 posts
    samples = 10000
    hour_counts = {hour: 0 for hour in range(24)}

    for _ in range(samples):
        hour_range = random.choices(
            list(hour_weights.keys()),
            weights=list(hour_weights.values())
        )[0]
        hour = random.choice(list(hour_range))
        hour_counts[hour] += 1

    print(f"Simulated {samples:,} posts by hour:\n")
    for hour, count in sorted(hour_counts.items()):
        if count > 0:
            percentage = (count / samples) * 100
            bar = '█' * int(percentage)
            print(f"  {hour:02d}:00 - {count:4,} posts ({percentage:5.2f}%) {bar}")

def test_platform_distribution():
    """Test platform distribution"""
    print("\n=== Platform Distribution Test ===\n")

    platform_distribution = {
        'twitter': 0.50,
        'facebook': 0.30,
        'instagram': 0.15,
        'youtube': 0.03,
        'whatsapp': 0.02,
    }

    total = 20000

    for platform, percentage in platform_distribution.items():
        count = int(total * percentage)
        print(f"  {platform.ljust(15)}: {count:6,} posts ({percentage * 100:5.1f}%)")

def test_sentiment_mapping():
    """Test sentiment scoring"""
    print("\n=== Sentiment Mapping Test ===\n")

    sentiment_mapping = {
        'water_crisis': (0.2, 0.4),
        'tvk_vijay': (0.7, 0.9),
        'neet_protest': (0.3, 0.5),
        'cauvery_water': (0.25, 0.45),
        'fishermen': (0.3, 0.5),
        'development': (0.65, 0.85),
    }

    for content_type, (min_score, max_score) in sentiment_mapping.items():
        avg_score = (min_score + max_score) / 2
        polarity = 'Positive' if avg_score >= 0.6 else 'Negative' if avg_score <= 0.4 else 'Neutral'
        print(f"  {content_type.ljust(20)}: {min_score:.2f}-{max_score:.2f} (Avg: {avg_score:.2f}) → {polarity}")

if __name__ == '__main__':
    test_content_templates()
    test_platform_distribution()
    test_engagement_tiers()
    test_time_distribution()
    test_sentiment_mapping()

    print("\n✓ All tests completed successfully!\n")
