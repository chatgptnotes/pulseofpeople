"""
AI Service
Handles all AI/LLM interactions for conversation bot
Uses OpenAI GPT-4 for conversations and local LLMs for classification/summarization
"""
import os
import logging
import json
from typing import Optional, Dict, Any, List
from openai import OpenAI
from langdetect import detect, LangDetectException
import re

logger = logging.getLogger(__name__)


class AIService:
    """
    Service class for AI-powered conversation handling
    """

    def __init__(self):
        """Initialize OpenAI client"""
        self.api_key = os.getenv('OPENAI_API_KEY')

        if not self.api_key:
            logger.warning("OpenAI API key not configured")
            self.client = None
        else:
            try:
                self.client = OpenAI(api_key=self.api_key)
                logger.info("AI Service initialized with OpenAI")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {str(e)}")
                self.client = None

    def detect_language(self, text: str) -> str:
        """
        Detect language of text

        Args:
            text: Input text

        Returns:
            Language code (ta, en, hi, te)
        """
        try:
            lang = detect(text)

            # Map to our supported languages
            lang_map = {
                'ta': 'ta',  # Tamil
                'en': 'en',  # English
                'hi': 'hi',  # Hindi
                'te': 'te',  # Telugu
            }

            return lang_map.get(lang, 'en')
        except LangDetectException:
            # Default to English if detection fails
            return 'en'

    def generate_conversation_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        language: str = 'en',
        bot_personality: str = 'friendly'
    ) -> Dict[str, Any]:
        """
        Generate AI response for user message

        Args:
            user_message: User's message
            conversation_history: List of previous messages [{"role": "user", "content": "..."}, ...]
            language: Conversation language
            bot_personality: Bot personality (friendly, formal, professional, casual)

        Returns:
            Dictionary with response text, tokens, and model
        """
        if not self.client:
            return {
                "response": "I'm currently in test mode. Please configure OpenAI API key.",
                "tokens": {"prompt": 0, "completion": 0},
                "model": "test_mode"
            }

        try:
            # Build system prompt based on language and personality
            system_prompt = self._build_system_prompt(language, bot_personality)

            # Prepare messages for API
            messages = [{"role": "system", "content": system_prompt}]

            # Add conversation history (limit to last 10 exchanges)
            messages.extend(conversation_history[-20:])

            # Add current user message
            messages.append({"role": "user", "content": user_message})

            # Call GPT-4
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=500,
                top_p=0.9,
                frequency_penalty=0.0,
                presence_penalty=0.6
            )

            assistant_message = response.choices[0].message.content

            return {
                "response": assistant_message,
                "tokens": {
                    "prompt": response.usage.prompt_tokens,
                    "completion": response.usage.completion_tokens
                },
                "model": response.model
            }

        except Exception as e:
            logger.error(f"Failed to generate response: {str(e)}")
            return {
                "response": "I'm having trouble responding right now. Please try again.",
                "tokens": {"prompt": 0, "completion": 0},
                "model": "error"
            }

    def _build_system_prompt(self, language: str, personality: str) -> str:
        """Build system prompt based on language and personality"""

        personality_traits = {
            'friendly': 'warm, helpful, and approachable',
            'formal': 'respectful, professional, and courteous',
            'professional': 'efficient, clear, and knowledgeable',
            'casual': 'relaxed, conversational, and easy-going'
        }

        trait = personality_traits.get(personality, 'friendly')

        language_names = {
            'ta': 'Tamil',
            'en': 'English',
            'hi': 'Hindi',
            'te': 'Telugu'
        }

        lang_name = language_names.get(language, 'English')

        # Base prompt for Tamil Nadu political feedback bot
        prompt = f"""You are a {trait} AI assistant for the Tamil Nadu government feedback system.

Your role:
- Collect feedback, suggestions, and concerns from citizens
- Ask clarifying questions to understand issues better
- Be empathetic and acknowledge concerns
- Gather location, demographics, and topic information naturally
- Maintain conversation context
- Respond in {lang_name}

Guidelines:
- Keep responses concise (2-3 sentences max)
- Ask one follow-up question at a time
- Focus on: Healthcare, Education, Jobs, Infrastructure, Public Services
- Be non-partisan and objective
- If user reports urgent issue, acknowledge and say it will be escalated
- Thank users for their feedback

Important:
- DO NOT make promises or commitments
- DO NOT discuss other political parties
- DO NOT share personal opinions
- If asked about policies, provide factual information only

Respond in {lang_name} unless the user switches languages."""

        return prompt

    def classify_intent(self, text: str) -> Dict[str, Any]:
        """
        Classify user intent using GPT-4

        Args:
            text: User message

        Returns:
            Dictionary with intent and confidence
        """
        if not self.client:
            return {
                "intent": "general_inquiry",
                "confidence": 0.5,
                "category": "inquiry"
            }

        try:
            prompt = f"""Classify the intent of this message into ONE of these categories:

1. feedback_positive - User sharing positive feedback
2. feedback_negative - User sharing negative feedback/complaint
3. report_issue - User reporting a specific problem
4. ask_question - User asking a question
5. make_suggestion - User providing suggestions
6. political_opinion - User sharing political views
7. general_inquiry - General conversation
8. off_topic - Not relevant to governance

Message: "{text}"

Respond in JSON format:
{{"intent": "category_name", "confidence": 0.0-1.0, "category": "feedback|complaint|suggestion|inquiry|political"}}"""

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=100
            )

            result = response.choices[0].message.content
            return json.loads(result)

        except Exception as e:
            logger.error(f"Intent classification failed: {str(e)}")
            return {
                "intent": "general_inquiry",
                "confidence": 0.5,
                "category": "inquiry"
            }

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text

        Args:
            text: Input text

        Returns:
            Dictionary with sentiment and score
        """
        if not self.client:
            return {
                "sentiment": "neutral",
                "score": 0.0,
                "confidence": 0.5
            }

        try:
            prompt = f"""Analyze the sentiment of this message:

Message: "{text}"

Respond in JSON format:
{{"sentiment": "positive|negative|neutral", "score": -1.0 to 1.0, "confidence": 0.0-1.0}}

Where score: -1.0 (very negative) to 1.0 (very positive), 0.0 (neutral)"""

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=100
            )

            result = response.choices[0].message.content
            return json.loads(result)

        except Exception as e:
            logger.error(f"Sentiment analysis failed: {str(e)}")
            return {
                "sentiment": "neutral",
                "score": 0.0,
                "confidence": 0.5
            }

    def extract_topics_and_keywords(self, text: str) -> Dict[str, Any]:
        """
        Extract topics, keywords, and issues from text

        Args:
            text: Input text

        Returns:
            Dictionary with topics, keywords, and issues
        """
        if not self.client:
            return {
                "topics": [],
                "keywords": [],
                "issues": []
            }

        try:
            prompt = f"""Extract structured information from this message:

Message: "{text}"

Identify:
1. Topics: Main subjects (Healthcare, Education, Jobs, Infrastructure, Transport, etc.)
2. Keywords: Important words (hospital, school, road, bus, etc.)
3. Issues: Specific problems mentioned

Respond in JSON format:
{{
    "topics": ["topic1", "topic2"],
    "keywords": ["keyword1", "keyword2"],
    "issues": ["issue1", "issue2"]
}}"""

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )

            result = response.choices[0].message.content
            return json.loads(result)

        except Exception as e:
            logger.error(f"Topic extraction failed: {str(e)}")
            return {
                "topics": [],
                "keywords": [],
                "issues": []
            }

    def extract_demographics(self, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Infer user demographics from conversation

        Args:
            conversation_history: Full conversation history

        Returns:
            Dictionary with demographic information
        """
        if not self.client or not conversation_history:
            return {}

        try:
            # Combine all user messages
            user_messages = [
                msg['content'] for msg in conversation_history
                if msg['role'] == 'user'
            ]
            combined_text = " ".join(user_messages)

            prompt = f"""Based on this conversation, infer user demographics (only if clearly evident):

Conversation: "{combined_text}"

Infer (only if mentioned or very obvious):
1. Age group: 18-24, 25-34, 35-44, 45-54, 55-64, 65+
2. Gender: male, female, other, unknown
3. Occupation: student, teacher, engineer, business, farmer, homemaker, unemployed, etc.
4. Education: school, graduate, postgraduate, unknown

Respond in JSON format:
{{"age_group": "...", "gender": "...", "occupation": "...", "education": "..."}}

Use "unknown" if not evident. Do not guess."""

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=150
            )

            result = response.choices[0].message.content
            demographics = json.loads(result)

            # Remove unknown values
            return {k: v for k, v in demographics.items() if v != "unknown"}

        except Exception as e:
            logger.error(f"Demographics extraction failed: {str(e)}")
            return {}

    def summarize_conversation(self, conversation_history: List[Dict[str, str]]) -> str:
        """
        Generate summary of conversation

        Args:
            conversation_history: Full conversation

        Returns:
            Summary text
        """
        if not self.client or not conversation_history:
            return ""

        try:
            # Combine all messages
            conversation_text = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in conversation_history
            ])

            prompt = f"""Summarize this conversation in 2-3 sentences. Focus on:
- Main topics discussed
- Issues raised
- User sentiment

Conversation:
{conversation_text}

Summary:"""

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=150
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Summarization failed: {str(e)}")
            return ""


# Singleton instance
_ai_service = None

def get_ai_service() -> AIService:
    """Get or create AI service instance"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
