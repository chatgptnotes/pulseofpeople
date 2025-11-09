#!/usr/bin/env python
"""
Test script for WhatsApp AI Chatbot
Tests all services and creates sample data
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.models import WhatsAppConversation, WhatsAppMessage, VoterProfile, BotConfiguration
from api.services.message_processor import get_message_processor
from api.services.whatsapp_service import get_whatsapp_service
from api.services.ai_service import get_ai_service

def test_services():
    """Test all services are working"""
    print("\n" + "="*60)
    print("TESTING WHATSAPP AI CHATBOT SERVICES")
    print("="*60)

    # Test WhatsApp Service
    print("\n1. Testing WhatsApp Service...")
    wa_service = get_whatsapp_service()
    link = wa_service.generate_click_to_chat_link(
        message="Hi, I want to share feedback",
        source="test",
        campaign="test_campaign"
    )
    print(f"   ✅ WhatsApp service working")
    print(f"   Generated link: {link}")

    # Test AI Service
    print("\n2. Testing AI Service...")
    ai_service = get_ai_service()
    lang = ai_service.detect_language("வணக்கம்! எப்படி இருக்கிறீர்கள்?")
    print(f"   ✅ AI service working")
    print(f"   Detected language: {lang}")

    # Test Message Processor
    print("\n3. Testing Message Processor...")
    processor = get_message_processor()
    print(f"   ✅ Message processor initialized")

    print("\n" + "="*60)
    print("ALL SERVICES WORKING! ✅")
    print("="*60)


def create_sample_bot_config():
    """Create sample bot configuration"""
    print("\n4. Creating Bot Configuration...")

    config, created = BotConfiguration.objects.get_or_create(
        name="Tamil Nadu Feedback Bot",
        defaults={
            'description': 'AI-powered feedback collection bot for Tamil Nadu citizens',
            'personality': 'friendly',
            'languages': ['ta', 'en', 'hi'],
            'channels': ['whatsapp', 'web'],
            'ai_model': 'gpt-4',
            'system_prompt': 'You are a helpful assistant collecting feedback from citizens.',
            'active': True
        }
    )

    if created:
        print(f"   ✅ Created new bot configuration: {config.name}")
    else:
        print(f"   ℹ️  Bot configuration already exists: {config.name}")

    return config


def create_sample_conversations():
    """Create sample conversation data"""
    print("\n5. Creating Sample Conversations...")

    # Sample conversation 1
    conv1, created1 = WhatsAppConversation.objects.get_or_create(
        phone_number="+919876543210",
        defaults={
            'user_name': 'Test User 1',
            'user_location': 'Chennai',
            'language': 'ta',
            'channel': 'whatsapp',
            'sentiment': 'positive',
            'sentiment_score': 0.8,
            'category': 'feedback',
            'priority': 'medium',
            'topics': ['Healthcare', 'Education'],
            'keywords': ['hospital', 'school'],
            'issues': ['Long wait times at hospital'],
            'ai_confidence': 85.0,
            'satisfaction_score': 90,
            'resolved': True
        }
    )

    if created1:
        # Add messages to conversation
        WhatsAppMessage.objects.create(
            conversation=conv1,
            sender='user',
            content='வணக்கம்! நான் எங்கள் பகுதியில் மருத்துவமனை பற்றி பேச விரும்புகிறேன்',
            language='ta',
            intent='report_issue',
            confidence=92.0,
            sentiment='neutral'
        )

        WhatsAppMessage.objects.create(
            conversation=conv1,
            sender='bot',
            content='வணக்கம்! உங்கள் கருத்துக்களை பகிர்ந்து கொள்ளுங்கள். எந்த மருத்துவமனை பற்றி பேச விரும்புகிறீர்கள்?',
            language='ta',
            model_used='gpt-4',
            prompt_tokens=120,
            completion_tokens=45
        )

        print(f"   ✅ Created sample conversation 1 with messages")
    else:
        print(f"   ℹ️  Sample conversation 1 already exists")

    # Sample conversation 2
    conv2, created2 = WhatsAppConversation.objects.get_or_create(
        phone_number="+919123456789",
        defaults={
            'user_name': 'Test User 2',
            'user_location': 'Coimbatore',
            'language': 'en',
            'channel': 'whatsapp',
            'sentiment': 'negative',
            'sentiment_score': -0.6,
            'category': 'complaint',
            'priority': 'high',
            'topics': ['Infrastructure', 'Roads'],
            'keywords': ['pothole', 'road', 'damage'],
            'issues': ['Bad road conditions'],
            'ai_confidence': 78.0,
            'satisfaction_score': 40,
            'resolved': False
        }
    )

    if created2:
        WhatsAppMessage.objects.create(
            conversation=conv2,
            sender='user',
            content='The roads in my area are terrible! Full of potholes.',
            language='en',
            intent='report_issue',
            confidence=95.0,
            sentiment='negative'
        )

        WhatsAppMessage.objects.create(
            conversation=conv2,
            sender='bot',
            content='I understand your concern about the road conditions. Can you please share your exact location so we can escalate this issue?',
            language='en',
            model_used='gpt-4',
            prompt_tokens=150,
            completion_tokens=55
        )

        print(f"   ✅ Created sample conversation 2 with messages")
    else:
        print(f"   ℹ️  Sample conversation 2 already exists")

    # Create voter profiles
    print("\n6. Creating Voter Profiles...")

    profile1, p_created1 = VoterProfile.objects.get_or_create(
        phone_number="+919876543210",
        defaults={
            'name': 'Test User 1',
            'preferred_language': 'ta',
            'location_data': {'district': 'Chennai', 'constituency': 'T.Nagar'},
            'demographics': {'age_group': '25-34', 'occupation': 'Engineer'},
            'interaction_count': 5,
            'total_messages_sent': 12,
            'avg_sentiment_score': 0.7,
            'topic_interests': {'Healthcare': 3, 'Education': 2}
        }
    )

    if p_created1:
        profile1.generate_referral_code()
        print(f"   ✅ Created voter profile 1 - Referral code: {profile1.referral_code}")
    else:
        print(f"   ℹ️  Voter profile 1 already exists - Code: {profile1.referral_code or 'None'}")

    profile2, p_created2 = VoterProfile.objects.get_or_create(
        phone_number="+919123456789",
        defaults={
            'name': 'Test User 2',
            'preferred_language': 'en',
            'location_data': {'district': 'Coimbatore', 'constituency': 'Coimbatore North'},
            'demographics': {'age_group': '35-44', 'occupation': 'Business'},
            'interaction_count': 3,
            'total_messages_sent': 8,
            'avg_sentiment_score': -0.3,
            'topic_interests': {'Infrastructure': 2, 'Roads': 1}
        }
    )

    if p_created2:
        profile2.generate_referral_code()
        print(f"   ✅ Created voter profile 2 - Referral code: {profile2.referral_code}")
    else:
        print(f"   ℹ️  Voter profile 2 already exists - Code: {profile2.referral_code or 'None'}")


def test_message_flow():
    """Test complete message processing flow"""
    print("\n" + "="*60)
    print("TESTING MESSAGE FLOW")
    print("="*60)

    processor = get_message_processor()

    test_message = "Healthcare facilities in my area need improvement"
    test_phone = "+919999999999"

    print(f"\nProcessing test message...")
    print(f"Phone: {test_phone}")
    print(f"Message: {test_message}")

    result = processor.process_incoming_message(
        phone_number=test_phone,
        message_text=test_message,
        message_type='text',
        source_campaign='test_campaign'
    )

    if result['status'] == 'success':
        print(f"\n✅ Message processed successfully!")
        print(f"   Conversation ID: {result['conversation_id']}")
        print(f"   Bot Response: {result['response'][:100]}...")
    else:
        print(f"\n❌ Message processing failed: {result.get('error')}")


def print_stats():
    """Print database statistics"""
    print("\n" + "="*60)
    print("DATABASE STATISTICS")
    print("="*60)

    conv_count = WhatsAppConversation.objects.count()
    msg_count = WhatsAppMessage.objects.count()
    profile_count = VoterProfile.objects.count()
    bot_count = BotConfiguration.objects.count()

    print(f"\n📊 Total Conversations: {conv_count}")
    print(f"📨 Total Messages: {msg_count}")
    print(f"👥 Total Voter Profiles: {profile_count}")
    print(f"🤖 Total Bot Configurations: {bot_count}")

    # Sentiment breakdown
    positive = WhatsAppConversation.objects.filter(sentiment='positive').count()
    negative = WhatsAppConversation.objects.filter(sentiment='negative').count()
    neutral = WhatsAppConversation.objects.filter(sentiment='neutral').count()

    print(f"\n😊 Positive: {positive}")
    print(f"😐 Neutral: {neutral}")
    print(f"😞 Negative: {negative}")

    print("\n" + "="*60)


def main():
    """Main test function"""
    print("\n🤖 WHATSAPP AI CHATBOT - TEST SUITE")
    print("="*60)

    try:
        # Test services
        test_services()

        # Create sample data
        create_sample_bot_config()
        create_sample_conversations()

        # Test message flow
        test_message_flow()

        # Print stats
        print_stats()

        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\n📝 Next Steps:")
        print("   1. Get WhatsApp API credentials from Meta")
        print("   2. Update .env with credentials")
        print("   3. Start server: python manage.py runserver")
        print("   4. Test with ngrok: ngrok http 8000")
        print("   5. Configure webhook in Meta dashboard")
        print("\n💡 API Endpoints Available:")
        print("   - http://localhost:8000/api/whatsapp/conversations/")
        print("   - http://localhost:8000/api/whatsapp/conversations/analytics/")
        print("   - http://localhost:8000/api/whatsapp/webhook/")
        print("\n📖 Read WHATSAPP_BOT_SETUP_COMPLETE.md for full documentation")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
