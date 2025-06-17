from __future__ import annotations

import json, re
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from openai import AsyncOpenAI, OpenAIError

from app.core.config import settings
from app.services.calendar_service import CalendarService


class AIService:
    """Wrapper around OpenAI Chat API with calendar awareness."""

    def __init__(self) -> None:
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model: str = settings.OPENAI_MODEL

    # ───────────────────── system prompt ──────────────────────────────
    def _create_system_prompt(
        self,
        personality: str,
        user_gender: str,
        language: str,
        calendar_context: str = "",
    ) -> str:
        personas = {
            "assistant": (
                "You are a professional AI assistant. Your tone is formal and efficient."
            ),
            "coach": (
                "You are an energetic motivational coach. Your tone is uplifting and dynamic."
            ),
            "friend": (
                "You're the user's best friend. Talk casually and informally, like a real friend."
            ),
            "girlfriend": (
                "You're a sweet and caring girlfriend. Be emotionally supportive and warm."
            ),
            "boyfriend": (
                "You're a protective and caring boyfriend. Make the user feel reassured and loved."
            ),
        }
        gender = {
            "male": "The user is male; adapt your responses accordingly.",
            "female": "The user is female; adapt your responses accordingly.",
            "other": "Keep responses gender-neutral.",
        }

        calendar_instr = (
            # ───── calendar abilities ────────────────────────────
            "Calendar skills:\n"
            "• Show schedules for today, tomorrow, or the current week.\n"
            "• Suggest free/available time slots.\n"
            "• Create events:\n"
            "    1) Return a single JSON object with exactly these top-level keys:\n"
            "       title, start, end, description (optional).\n"
            "       └─ For start/end use ISO 8601 - either\n"
            "          {\"dateTime\": \"2025-06-16T09:00:00\"}   or   \"2025-06-16T09:00:00\".\n"
            "    2) Put that JSON on its own line, wrapped **exactly** like\n"
            "       <calendar_data>{ ... }</calendar_data>\n"
            "    3) After a blank line, write the friendly reply for the user.\n"
            "       Never mention the tag, the JSON, or any technical details.\n"
        )

        parts = [
            personas.get(personality, personas["assistant"]),
            gender.get(user_gender, gender["other"]),
            f"Respond in {language}.",
            calendar_instr,
        ]
        if calendar_context:
            # не даём контексту разрастись >1К символов
            parts.append(calendar_context[:1000])

        return "\n".join(parts)

    # ───────────────────── main entry ─────────────────────────────────
    async def analyze_message(
        self,
        message: str,
        *,
        personality: str = "assistant",
        user_gender: str = "other",
        language: str = "English",
        calendar_service: Optional[CalendarService] = None,
    ) -> Dict[str, Any]:
        """
        Returns dict: { message, calendar_data, should_create_event }
        """
        try:
            # ── detect language & choose keywords ─────────────────────
            detected = await self.detect_language(message)
            lang = detected if detected in ("English", "Russian") else "English"

            KW = {
                "English": {
                    "sched": ["schedule", "event", "events", "plan", "plans"],
                    "today": ["today"],
                    "tomorrow": ["tomorrow"],
                    "week": ["week"],
                    "free": ["free time", "available", "free slot"],
                },
                "Russian": {
                    "sched": ["расписание", "планы", "дела", "события"],
                    "today": ["сегодня"],
                    "tomorrow": ["завтра"],
                    "week": ["неделя", "на неделе"],
                    "free": ["окно", "свободно", "есть ли время"],
                },
            }

            keys = KW[lang]
            lower_msg = message.lower()

            # ── calendar context building ────────────────────────────
            calendar_context = ""
            if calendar_service:
                now = datetime.now()

                def has(words):  # helper
                    return any(w in lower_msg for w in words)

                if has(keys["sched"] + keys["today"]):
                    events = calendar_service.get_events_for_day(now)
                    calendar_context = (
                        "\nToday's schedule:\n"
                        f"{calendar_service.format_events_for_ai(events)}"
                    )
                elif has(keys["tomorrow"]):
                    events = calendar_service.get_events_for_day(now + timedelta(days=1))
                    calendar_context = (
                        "\nTomorrow's schedule:\n"
                        f"{calendar_service.format_events_for_ai(events)}"
                    )
                elif has(keys["week"]):
                    events = calendar_service.get_events_for_week(now)
                    calendar_context = (
                        "\nThis week's schedule:\n"
                        f"{calendar_service.format_events_for_ai(events)}"
                    )

                if has(keys["free"]):
                    slots = calendar_service.find_free_slots(now)
                    calendar_context = (
                        "\nAvailable time slots:\n"
                        f"{calendar_service.format_free_slots_for_ai(slots)}"
                    )

            # ── call OpenAI ───────────────────────────────────────────
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._create_system_prompt(
                            personality, user_gender, language, calendar_context
                        ),
                    },
                    {"role": "user", "content": message},
                ],
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS,
            )
            if not completion.choices:
                raise ValueError("No response from OpenAI")

            ai_raw: str = completion.choices[0].message.content or ""

            # 1. паттерн
            pattern = re.compile(
                r'(?s)<calendar_data>(\{.*?\})</calendar_data>|'
                r'calendar_data\s*(\{.*?\})(?=$|\n)'
            )

            # 2. поиск + вырезка
            match = pattern.search(ai_raw)
            calendar_data = None
            if match:
                # забираем первую непустую группу
                raw_json = next(g for g in match.groups() if g)
                try:
                    calendar_data = json.loads(raw_json)
                except json.JSONDecodeError as exc:
                    print(f"[AIService] bad JSON in calendar_data: {exc}\n{raw_json}")

            # чистим текст ровно один раз
            clean_text = pattern.sub('', ai_raw).strip()

            event_id = None
            if calendar_data and calendar_service:
                try:
                    ev = calendar_service.create_event(calendar_data)
                    event_id = str(ev.id)          # UUID -> str для JSON-сериализации
                except Exception as exc:
                    # Логируем, но не ломаем ответ пользователю
                    print(f"[AIService] Failed to create event: {exc}")

            return {
                "message": clean_text,
                "calendar_data": calendar_data,
                "should_create_event": calendar_data is not None,
                "event_id": event_id,
            }

        # ───── error handling ─────────────────────────────────────────
        except OpenAIError as err:
            print(f"[AIService] OpenAI API error: {err}")
            return {
                "message": "I’m having trouble reaching the AI service right now.",
                "calendar_data": None,
                "should_create_event": False,
            }

        except Exception as err:
            print(f"[AIService] Unexpected error: {err}")
            return {
                "message": "Oops! Something went wrong. Please try again.",
                "calendar_data": None,
                "should_create_event": False,
            }

    # ─────────────────── language detection helper ───────────────────
    async def detect_language(self, text: str) -> str:
        try:
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Detect the language of the following text and respond with just the language name in English.",
                    },
                    {"role": "user", "content": text},
                ],
                temperature=0,
                max_tokens=10,
            )
            if completion.choices:
                return completion.choices[0].message.content.strip()
            return "English"
        except Exception as exc:
            print(f"[AIService.detect_language] Error: {exc}")
            return "English"
