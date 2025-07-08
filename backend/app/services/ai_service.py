from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from zoneinfo import ZoneInfo

from openai import AsyncAzureOpenAI, OpenAIError
from app.services.openai_service import ask_gpt

from app.core.config import settings
from app.services.calendar_service import CalendarService
from app.services.memory_service import MemoryStore




class AIService:
    """Wrapper around OpenAI Chat API with calendar awareness."""
    
    def build_calendar_context(self, calendar_service, until_hours: int = 24) -> str:
        user_tz = ZoneInfo(calendar_service.user.timezone)
        now_local   = datetime.now(user_tz)
        until_local = now_local + timedelta(hours=until_hours)

        # берём события за ближайшие N часов
        events = calendar_service.list_events_between(now_local, until_local)

        # сортируем по началу
        events.sort(key=lambda ev: ev.start_time)

        # форматируем
        lines = []
        for ev in events:
            start = ev.start_time.astimezone(user_tz)
            end   = ev.end_time.astimezone(user_tz) if ev.end_time else None
            if end:
                lines.append(f"{start:%Y-%m-%d %H:%M}–{end:%H:%M} – {ev.title}")
            else:
                lines.append(f"{start:%Y-%m-%d %H:%M} – {ev.title}")
        return "\n".join(lines)
    
    
    def __init__(self) -> None:
        self.model: str = settings.DEPLOYMENT_NAME
        self.memory = MemoryStore()     

    def _create_system_prompt(
        self,
        personality: str,
        user_gender: str,
        language: str,
        today_line: str,
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
                "You're a sweet and caring girlfriend. Be emotionally supportive and warm. "
                "Feel free to add emojis at the start of each bullet to show affection."
            ),
            "boyfriend": (
                "You're a protective and caring boyfriend. Make the user feel reassured and loved. "
                "Feel free to add emojis at the start of each bullet to show care."
            ),
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
            "• The schedules you see ARE ALREADY in the user's local time zone.\n"
            "  Repeat the times exactly as they appear; DO NOT convert or shift them.\n"
            "• Show schedules for today, tomorrow, a weekday, or the current week.\n"
            "• If the user asks about a specific time, show the schedule for that time.\n"
            "• If the user asks about a specific day, show the schedule for that day.\n"
            "• Always present times in **24-hour format** (e.g., 15:00, not 3 PM) and list each event on a new line, preceded by “- ”.\n"
            "  If the persona is 'girlfriend' or 'boyfriend', you may prepend a fitting emoji to each bullet.\n"
            "• Suggest free/available time slots.\n"
            "• Replies must be concise; avoid filler phrases such as “I'm always here” or similar supportive lines.\n"
            "• Remember you are an AI, not a living being, and cannot perform real-world actions or meetings.\n"
            "• Create events **or delete events**:\n"
            "    1) For creation, return JSON with keys: title, start, end, description (optional).\n"
            "       Wrap exactly like <calendar_data>{ ... }</calendar_data>\n"
            "    2) For deletion, return JSON with keys: title, date (YYYY-MM-DD).\n"
            "       Wrap exactly like <calendar_delete>{ ... }</calendar_delete>\n"
            "    2b) To delete a *specific* event on that date, add either:\n"
            "        • \"start\": ISO-datetime of the event’s start (e.g., \"2025-07-09T11:00\") **or**\n"
            "        • \"event_id\": numeric id of the event (preferred if shown).\n"
            "    2c) If neither \"start\" nor \"event_id\" is provided and multiple matches exist,\n"
            "        ask the user to clarify which one to delete before returning <calendar_delete>.\n"
            "    3) After a blank line, write the friendly reply. **Never** mention the tags or JSON.\n"
            "before showing list of events show date of the day in first line with format like 17 then name of month, and year"
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

    async def analyze_message(
        self,
        message: str,
        *,
        chat_id: int,
        personality: str = "assistant",
        user_gender: str = "other",
        language: str = "English",
        calendar_service: Optional[CalendarService] = None,
    ) -> Dict[str, Any]:
        try:
            # 1) Определяем язык
            detected = await self.detect_language(message)
            lang = detected if detected in (
                "English", "Russian") else "English"


            # 3) Сейчас по часовому поясу пользователя
            user_tz = ZoneInfo(
                calendar_service.user.timezone) if calendar_service else timezone.utc
            now = datetime.now(user_tz)
            today_str = now.strftime("%Y-%m-%d")
            today_line = f"Today is {today_str} in the user's timezone.\n"

            
            # 5) Собираем контекст календаря
            calendar_context = ""
            
            if calendar_service:
                calendar_context = self.build_calendar_context(calendar_service, until_hours=24)
                if calendar_context:
                    calendar_context = (
                        "Here are the user's upcoming events (local time):\n"
                        + calendar_context + "\n"
                    )
            
            history = self.memory.get(chat_id)[:]        # копия (чтобы не портить память)
            history.append({"role": "user", "content": message})
   

            ai_raw = await ask_gpt(
                messages=[
                    {"role": "system", "content": self._create_system_prompt(
                        personality, user_gender, lang, today_line, calendar_context
                    )},
                    *history, 
                ],
                model=self.model,
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS,
            )

            # 7) Парсинг JSON-объектов
            r_create = re.compile(
                r'<calendar_data>(\{.*?\})</calendar_data>', re.S)
            r_delete = re.compile(
                r'<calendar_delete>(\{.*?\})</calendar_delete>', re.S)
            m_c = r_create.search(ai_raw)
            m_d = r_delete.search(ai_raw)

            try:
                calendar_data = json.loads(m_c.group(1)) if m_c else None
            except json.JSONDecodeError:
                calendar_data = None
            try:
                delete_params = json.loads(m_d.group(1)) if m_d else None
            except json.JSONDecodeError:
                delete_params = None

            clean_text = r_delete.sub('', r_create.sub('', ai_raw)).strip()
            
            self.memory.add(chat_id, "assistant", clean_text)  

            should_save = calendar_data and all(k in calendar_data for k in ("title","start","end"))

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
                if delete_params:
                    try:
                        was_deleted = calendar_service.delete_event_by_title_and_date(
                            delete_params)
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
            lang = await ask_gpt(
                messages=[
                    {"role": "system", "content":
                     "Detect the language of the following text and respond with just the language name in English."},
                    {"role": "user", "content": text},
                ],
                max_tokens=10,
                temperature=0
            )
            return lang.strip()
        
        except:
            return "English"
