from __future__ import annotations
from fastapi import HTTPException
import json
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from zoneinfo import ZoneInfo

from openai import AsyncOpenAI, OpenAIError

from app.core.config import settings
from app.services.calendar_service import CalendarService
from app.services.chat_service import ChatService
from app.schemas.ai import AIMessageRequest
from app.models import User, Chat, ChatMessage, CalendarEvent




class AIService:
    """Wrapper around OpenAI Chat API with calendar awareness."""

    def __init__(self) -> None:
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url="https://api.openai.com/v1"  
        )
        self.model: str = settings.OPENAI_MODEL

    def _create_system_prompt(
        self,
        personality: str,
        user_gender: str,
        language: str,
        today_line: str,
        calendar_context: str = "",
    ) -> str:
        personas = {
            "assistant": "You are a professional AI assistant. Your tone is formal and efficient.",
            "coach":     "You are an energetic motivational coach. Your tone is uplifting and dynamic.",
            "friend":    "You're the user's best friend. Talk casually and informally, like a real friend.",
            "girlfriend":"You're a sweet and caring girlfriend. Be emotionally supportive and warm.",
            "boyfriend": "You're a protective and caring boyfriend. Make the user feel reassured and loved.",
        }
        gender = {
            "male":   "The user is male; adapt your responses accordingly.",
            "female": "The user is female; adapt your responses accordingly.",
            "other":  "Keep responses gender-neutral.",
        }

        calendar_instr = (
            f"{today_line}"
            "Calendar skills:\n"
            "• Only return <calendar_data> if the user explicitly asks to ADD/BOOK/SCHEDULE an event.\n"
            "• Show schedules for today, tomorrow, a weekday, or the current week.\n"
            "• Suggest free/available time slots.\n"
            "• Create events **or delete events**:\n"
            "    1) For creation, return JSON with keys: title, start, end, description (optional).\n"
            "       Wrap exactly like <calendar_data>{ ... }</calendar_data>\n"
            "    2) For deletion, return JSON with keys: title, date (YYYY-MM-DD).\n"
            "       Wrap exactly like <calendar_delete>{ ... }</calendar_delete>\n"
            "    3) After a blank line, write the friendly reply. Never mention the tags or JSON.\n"
        )

        parts = [
            personas.get(personality, personas["assistant"]),
            gender.get(user_gender, gender["other"]),
            f"Respond in {language}.",
            calendar_instr,
        ]
        if calendar_context:
            parts.append(calendar_context[:1000])
        return "\n".join(parts)
    
    async def handle_analysis(self, request: AIMessageRequest, db, user: User):
        chat_service = ChatService(db, user)
        calendar_service = CalendarService(db, user)

        personality = request.personality or user.chat_personality
        language = request.language or await self.detect_language(request.message)

        # 1. Get/create chat
        if request.chat_id:
            chat = chat_service.get_chat(request.chat_id)
            if not chat:
                raise HTTPException(404, "Chat not found")
        else:
            chat = chat_service.create_chat(request.message[:50] + "...")

        # 2. Save message
        chat_service.add_message(chat.id, request.message, "user")

        # 3. AI reply
        analysis = await self.analyze_message(
            message=request.message,
            personality=personality,
            user_gender=user.gender,
            language=language,
            calendar_service=calendar_service
        )

        chat_service.add_message(chat.id, analysis["message"], "assistant")

        # 4. Try create event
        calendar_event_id = None
        if analysis["calendar_data"] and analysis["should_create_event"]:
            calendar_event_id = calendar_service.try_create_event_from_ai(analysis["calendar_data"])

        return {
            "message": analysis["message"],
            "chat_id": chat.id,
            "calendar_event_id": calendar_event_id
        }

    async def analyze_message(
        self,
        message: str,
        *,
        personality: str = "assistant",
        user_gender: str = "other",
        language: str = "English",
        calendar_service: Optional[CalendarService] = None,
    ) -> Dict[str, Any]:
        try:
            # 1) Определяем язык
            detected = await self.detect_language(message)
            lang = detected if detected in ("English", "Russian") else "English"

            # 2) Ключевые слова
            KW = {
                "English": {
                    "sched": ["schedule", "event", "events", "plan", "plans"],
                    "today": ["today"],     "tomorrow": ["tomorrow"],
                    "week": ["week"],       "free": ["free time", "available", "free slot"],
                    "next": ["next", "coming"],
                    "weekday": {
                        "monday":0,"tuesday":1,"wednesday":2,
                        "thursday":3,"friday":4,"saturday":5,"sunday":6,
                    },
                },
                "Russian": {
                    "sched": ["расписание","планы","дела","события"],
                    "today": ["сегодня"],   "tomorrow": ["завтра"],
                    "week": ["неделя","на неделе"], "free": ["окно","свободно","есть ли время"],
                    "next": ["следующ"],
                    "weekday": {
                        "понедельник":0,"пн":0,"вторник":1,"вт":1,"среда":2,"ср":2,
                        "четверг":3,"чт":3,"пятница":4,"пт":4,"суббота":5,"сб":5,"воскресенье":6,"вс":6,
                    },
                },
            }
            keys = KW[lang]
            lower_msg = message.lower()
            has = lambda arr: any(w in lower_msg for w in arr)

            # 3) Сейчас по часовому поясу пользователя
            user_tz = ZoneInfo(calendar_service.user.timezone) if calendar_service else timezone.utc
            now = datetime.now(user_tz)
            today_str  = now.strftime("%Y-%m-%d")
            today_line = f"Today is {today_str} in the user's timezone.\n"

            # 4) На какую дату спрашивают?
            target_date: Optional[datetime] = None
            if has(keys["today"]):    target_date = now
            elif has(keys["tomorrow"]): target_date = now + timedelta(days=1)
            else:
                next_flag = has(keys["next"])
                for word, idx in keys["weekday"].items():
                    if word in lower_msg:
                        delta = (idx - now.weekday()) % 7 or 7
                        if next_flag: delta += 7
                        target_date = now + timedelta(days=delta)
                        break

            # 5) Собираем контекст календаря
            calendar_context = ""
            if calendar_service and target_date:
                evs = calendar_service.get_events_for_day(target_date)
                day_str = target_date.strftime("%A, %d %B")
                calendar_context = f"\nSchedule for {day_str}:\n"\
                                   f"{calendar_service.format_events_for_ai(evs)}"
            elif calendar_service and has(keys["week"]):
                evs = calendar_service.get_events_for_week(now)
                calendar_context = "\nThis week's schedule:\n"\
                                   f"{calendar_service.format_events_for_ai(evs)}"
            if calendar_service and has(keys["free"]):
                slots = calendar_service.find_free_slots(now)
                calendar_context += "\nAvailable time slots:\n"\
                                    f"{calendar_service.format_free_slots_for_ai(slots)}"

            # 6) Запрос к OpenAI
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role":"system", "content": self._create_system_prompt(
                        personality, user_gender, language, today_line, calendar_context
                    )},
                    {"role":"user",   "content": message},
                ],
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS,
            )
            ai_raw = completion.choices[0].message.content or ""

            # 7) Парсинг JSON-объектов
            r_create = re.compile(r'<calendar_data>(\{.*?\})</calendar_data>', re.S)
            r_delete = re.compile(r'<calendar_delete>(\{.*?\})</calendar_delete>', re.S)
            m_c = r_create.search(ai_raw)
            m_d = r_delete.search(ai_raw)

            calendar_data = json.loads(m_c.group(1)) if m_c else None
            delete_params = json.loads(m_d.group(1)) if m_d else None

            clean_text = r_delete.sub('', r_create.sub('', ai_raw)).strip()

            # 8) Триггер на сохранение
            CREATE_TRIGGERS = ["add","schedule","book","plan","добав","заплан","запиши"]
            should_save = any(stem in lower_msg for stem in CREATE_TRIGGERS)

            # 9) Применение в БД
            event_id = None
            was_deleted = False
            if calendar_service:
                # — создаём
                if calendar_data and should_save:
                    try:
                        ev = calendar_service.create_event(calendar_data)
                        event_id = str(ev.id)
                    except ValueError as err:
                        # конфликт по времени или валидация
                        return {
                            "message": f"Не могу добавить событие: {err}",
                            "calendar_data": None,
                            "should_create_event": False,
                            "event_id": None,
                            "was_deleted": False,
                        }
                # — удаляем
                elif delete_params:
                    try:
                        was_deleted = calendar_service.delete_event_by_title_and_date(delete_params)
                    except ValueError as err:
                        return {
                            "message": f"Не могу удалить событие: {err}",
                            "calendar_data": None,
                            "should_create_event": False,
                            "event_id": None,
                            "was_deleted": False,
                        }

            return {
                "message": clean_text,
                "calendar_data": calendar_data,
                "should_create_event": bool(calendar_data and should_save),
                "event_id": event_id,
                "was_deleted": was_deleted,
            }

        except OpenAIError as e:
            print("[AIService] OpenAI API error:", e)
            return {
                "message": "Проблемы с доступом к AI-сервису.",
                "calendar_data": None,
                "should_create_event": False,
            }
        except Exception as e:
            print("[AIService] Unexpected error:", e)
            return {
                "message": "Что-то пошло не так, попробуйте ещё раз.",
                "calendar_data": None,
                "should_create_event": False,
            }

    async def detect_language(self, text: str) -> str:
        try:
            resp = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role":"system","content":
                     "Detect the language of the following text and respond with just the language name in English."},
                    {"role":"user","content":text},
                ],
                temperature=0, max_tokens=10
            )
            return resp.choices[0].message.content.strip()
        except:
            return "English"
