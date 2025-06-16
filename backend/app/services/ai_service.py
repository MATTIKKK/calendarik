from typing import Dict, Any
from openai import AsyncOpenAI, OpenAIError
from app.core.config import settings
from app.services.calendar_service import CalendarService
from datetime import datetime, timedelta
import json
import re


class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    def _create_system_prompt(self, personality: str, user_gender: str, language: str, calendar_context: str = "") -> str:
        base_prompts = {
            'assistant': (
                "You are a professional AI assistant. Your tone is formal and efficient. "
                "Help the user manage their schedule with precision and clarity."
            ),
            'coach': (
                "You are an energetic motivational coach. Your tone is uplifting and dynamic. "
                "Encourage the user to stay organized and productive."
            ),
            'friend': (
                "You're the user's best friend. Talk casually and informally, like a real friend. "
                "Use friendly expressions and occasional slang. Be chill and helpful."
            ),
            'girlfriend': (
                "You're a sweet and caring girlfriend. Use affectionate language, emojis, and warmth. "
                "Be emotionally supportive and kind when helping the user plan things."
            ),
            'boyfriend': (
                "You're a protective and caring boyfriend. Be emotionally supportive, gentle, and warm. "
                "Make the user feel reassured and loved."
            )
        }

        gender_adaptation = {
            'male': "The user is male, adapt your responses accordingly.",
            'female': "The user is female, adapt your responses accordingly.",
            'other': "Keep responses gender-neutral."
        }

        calendar_instructions = """
        You can help with calendar-related tasks:
        1. View schedule for any day or week
        2. Find free time slots
        3. Create new events (use calendar_data tags)
        4. Analyze schedule conflicts

        When asked about schedule or free time, I'll provide the information in the context.
        When creating events, use calendar_data tags with proper JSON format.
        """

        return "\n".join([
            base_prompts.get(personality, base_prompts['assistant']),
            gender_adaptation.get(user_gender, gender_adaptation['other']),
            f"Respond in {language}.",
            calendar_instructions,
            calendar_context if calendar_context else ""
        ])

    async def analyze_message(
        self,
        message: str,
        personality: str = "assistant",
        user_gender: str = "other",
        language: str = "English",
        calendar_service: CalendarService = None
    ) -> Dict[str, Any]:
        try:
            # Handle calendar-related queries
            calendar_context = ""
            if calendar_service:
                today = datetime.now()
                
                # Check for schedule-related keywords
                if any(word in message.lower() for word in ["schedule", "events", "today", "tomorrow", "week"]):
                    if "today" in message.lower():
                        events = calendar_service.get_events_for_day(today)
                        calendar_context = f"\nToday's schedule:\n{calendar_service.format_events_for_ai(events)}"
                    elif "tomorrow" in message.lower():
                        events = calendar_service.get_events_for_day(today + timedelta(days=1))
                        calendar_context = f"\nTomorrow's schedule:\n{calendar_service.format_events_for_ai(events)}"
                    elif "week" in message.lower():
                        events = calendar_service.get_events_for_week(today)
                        calendar_context = f"\nThis week's schedule:\n{calendar_service.format_events_for_ai(events)}"

                # Check for free time queries
                if any(word in message.lower() for word in ["free time", "available", "free slot"]):
                    slots = calendar_service.find_free_slots(today)
                    calendar_context = f"\nAvailable time slots:\n{calendar_service.format_free_slots_for_ai(slots)}"

            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._create_system_prompt(personality, user_gender, language, calendar_context)
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS
            )

            if not completion.choices:
                raise ValueError("No response from OpenAI")

            ai_response = completion.choices[0].message.content or ""
            calendar_data = None

            # Try extracting <calendar_data> JSON
            match = re.search(r'<calendar_data>(.*?)</calendar_data>', ai_response, re.DOTALL)
            if match:
                raw_data = match.group(1).strip()
                try:
                    calendar_data = json.loads(raw_data)
                    ai_response = re.sub(r'<calendar_data>.*?</calendar_data>', '', ai_response, flags=re.DOTALL)
                except json.JSONDecodeError as e:
                    print(f"[AIService] JSON parse error: {e}")
                    print(f"[AIService] Raw calendar data: {raw_data}")

            return {
                "message": ai_response.strip(),
                "calendar_data": calendar_data,
                "should_create_event": calendar_data is not None
            }

        except OpenAIError as e:
            print(f"[AIService] OpenAI API error: {e}")
            return {
                "message": "I apologize, but I'm having trouble connecting to AI services right now.",
                "calendar_data": None,
                "should_create_event": False
            }

        except Exception as e:
            print(f"[AIService] Unexpected error: {e}")
            return {
                "message": "Oops! Something went wrong. Please try again.",
                "calendar_data": None,
                "should_create_event": False
            }

    async def detect_language(self, text: str) -> str:
        try:
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Detect the language of the following text and respond with just the language name in English."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                temperature=0,
                max_tokens=20
            )

            if completion.choices:
                return completion.choices[0].message.content.strip()
            return "English"
        except Exception as e:
            print(f"[AIService.detect_language] Error: {e}")
            return "English"
 