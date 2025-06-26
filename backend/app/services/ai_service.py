from __future__ import annotations
from fastapi import HTTPException
import json
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, List, Tuple
from zoneinfo import ZoneInfo
from dateutil.parser import parse as parse_dt

from openai import AsyncOpenAI, OpenAIError

from app.core.config import settings
from app.services.calendar_service import CalendarService
from app.services.chat_service import ChatService
from app.schemas.ai import AIMessageRequest
from app.models import User, Chat, ChatMessage, CalendarEvent


class AIService:
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
            "girlfriend": "You're a sweet and caring girlfriend. Be emotionally supportive and warm.",
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
            "• You are an AI (not a living being). Even in persona (“girlfriend”/“boyfriend”), never mention meeting up or imply you have a physical presence—you simply speak in that style.\n"
            "• When the user asks about their schedule (today, tomorrow, this week, next weekend, etc.), return <calendar_data> with exactly the events from the provided context; do not invent or add anything.\n"
            "  – Inside the JSON, split into two lists: “past” (events before now) and “upcoming” (events after now).\n"
            "• Keep your human‐facing reply **very short** (one or two sentences) and use **simple, friendly language**—no technical jargon or long explanations.\n"
            "• When asked to add or delete an event, follow these steps:\n"
            "  1) If any detail (title, date, time) is missing, ask a direct follow-up question.\n"
            "  2) Once you have all details, emit exactly one JSON blob wrapped in <calendar_data>…</calendar_data> (for creation) or <calendar_delete>…</calendar_delete> (for deletion), then a one-sentence confirmation.\n"
        )

        parts = [
            personas.get(personality, personas["assistant"]),
            gender.get(user_gender, gender["male"]),
            f"Respond in {language}.",
            calendar_instr,
        ]
        if calendar_context:
            parts.append(calendar_context[:1000])
        return "\n".join(parts)

    async def handle_analysis(self, request: AIMessageRequest, db, user: User):
        chat_service = ChatService(db, user)
        calendar_service = CalendarService(db, user)

        print("request in handle_analysis", request)

        personality = user.chat_personality
        language = user.preferred_language

        chat = chat_service.get_or_create_chat(
            title=request.message[:50] + "..."
        )

        chat_service.add_message(
            chat_id=chat.id,
            role="user",
            content=request.message,
        )

        history = chat_service.get_chat_messages(
            chat_id=chat.id,
            limit=10,
            before_id=None
        )

        analysis = await self.analyze_message(
            message=request.message,
            personality=personality,
            user_gender=user.gender,
            language=language,
            calendar_service=calendar_service,
            history=history
        )

        chat_service.add_message(
            chat_id=chat.id,
            role="assistant",
            content=analysis["message"],
        )

        calendar_event_id = None
        if analysis["calendar_data"] and analysis["should_create_event"]:
            try:
                calendar_event_id = calendar_service.try_create_event_from_ai(
                    analysis["calendar_data"]
                )
                
            except Exception:
                calendar_event_id = None

        return {
            "message": analysis["message"],
            "chat_id": chat.id,
            "calendar_event_id": calendar_event_id
        }

    async def analyze_message(
        self,
        message: str,
        *,
        personality: str,
        user_gender: str,
        language: str,
        calendar_service: CalendarService,
        history: List[ChatMessage],
    ) -> Dict[str, Any]:

        text = message.lower().strip()
        now = datetime.now(ZoneInfo(calendar_service.user.timezone))

        intent, date_range = self._detect_intent_and_dates(text, now)

        calendar_context = ""
        if intent in ("view", "free"):
            start, end = date_range
            if intent == "view":
                evs = calendar_service.get_events_for_range(start, end)
            else:
                evs = calendar_service.find_free_slots(
                    start, days=(end - start).days or 1)
            calendar_context = self._format_calendar_context(
                evs, intent, start, end)

        system_prompt = self._build_system_prompt(
            personality, user_gender, language, now, calendar_context
        )

        messages = [
            {"role": "system", "content": system_prompt},
            *[
                {"role": m.role, "content": m.content}
                for m in history
            ],
            {"role": "user", "content": message},
        ]

        try:
            resp = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=800,
            )
            raw = resp.choices[0].message.content
        except OpenAIError:
            logger.error(f"OpenAIError in analyze_message: {e}")
            return {"message": "Извините, AI-сервис недоступен.", **self._no_action()}

        data = self._extract_tags(raw)
        clean = self._strip_tags(raw)

        should_create = intent == "create" and data.get("create")
        should_delete = intent == "delete" and data.get("delete")

        return {
            "message": clean,
            "calendar_data": data.get("create") or data.get("view"),
            "should_create_event": should_create,
            "should_delete_event": should_delete,
            "raw_json": data,
        }

    def _detect_intent_and_dates(
        self, text: str, now: datetime
    ) -> Tuple[str, Tuple[Optional[datetime], Optional[datetime]]]:
        """
        Возвращает intent ∈ {view, free, create, delete, chat}
        и tuple(start_datetime, end_datetime) — границы запроса.
        """
        # Ключевые слова
        if any(w in text for w in ["добав", "заплан", "schedule", "add", "book"]):
            intent = "create"
        elif any(w in text for w in ["удал", "delete", "remove"]):
            intent = "delete"
        elif any(w in text for w in ["свобод", "free time", "available"]):
            intent = "free"
        elif any(w in text for w in ["планы", "распис", "schedule", "какие у меня"]):
            intent = "view"
        else:
            intent = "chat"

        # Разбор даты/диапазона
        start = end = None
        # точные слова
        if "сегодня" in text:
            start, end = now.replace(hour=0, minute=0), now + timedelta(days=1)
        elif "завтра" in text:
            t = now + timedelta(days=1)
            start, end = t.replace(hour=0, minute=0), t + timedelta(days=1)
        elif m := re.search(r"(\d{1,2}[./-]\d{1,2}(?:[./-]\d{2,4})?)", text):
            # например "25.06" или "2025-06-25"
            dt = parse_dt(m.group(1), dayfirst=True)
            start = dt.replace(hour=0, minute=0)
            end = start + timedelta(days=1)
        elif any(w in text for w in ["недел", "week"]):
            # с понедельника этой недели по конец текущей недели
            monday = now - timedelta(days=now.weekday())
            start = monday.replace(hour=0, minute=0)
            end = start + timedelta(days=7)
        elif any(w in text for w in ["выходн", "weekend"]):
            # следующий уикенд (сб-вс)
            sat = now + timedelta((5 - now.weekday()) % 7)
            start = sat.replace(hour=0, minute=0)
            end = start + timedelta(days=2)
        else:
            # fallback — границы не заданы
            start = now
            end = now + timedelta(days=1)

        return intent, (start, end)

    def _build_system_prompt(
        self,
        personality: str,
        user_gender: str,
        language: str,
        now: datetime,
        calendar_context: str,
    ) -> str:
        today = now.strftime("%Y-%m-%d")
        instr = [
            f"Today is {today} in the user's timezone.",
            "You are an AI (not a living being). Even in persona, do NOT imply a physical presence.",
            "Speak in the chosen style but never propose personal meetups.",
            "Use simple friendly language, keep replies very short.",
        ]
        if calendar_context:
            instr.append("Here is the calendar data:\n" + calendar_context)
        instr.append("If user asks to add/delete, ask for missing details, then return JSON in <calendar_data> or <calendar_delete> tags, then one‐line confirmation.")
        return "\n".join(instr)

    def _format_calendar_context(
        self,
        evs: list,
        intent: str,
        start: datetime,
        end: datetime
    ) -> str:
        """Готовит JSON-контекст для system prompt, поддерживая CalendarEvent и dict."""

        now_utc = datetime.now(timezone.utc)

        def get_start(e):
            if isinstance(e, dict):
                val = e.get("start")
                if isinstance(val, datetime):
                    return val
                if isinstance(val, str):
                    return parse_dt(val)
                raise ValueError(f"Unsupported start type: {type(val)}")
            # ORM-объект
            return e.start_time

        def get_end(e):
            if isinstance(e, dict):
                val = e.get("end")
                if isinstance(val, datetime):
                    return val
                if isinstance(val, str) and val:
                    return parse_dt(val)
                return None
            return e.end_time

        def get_title(e):
            return e.get("title") if isinstance(e, dict) else e.title

        past = []
        upcoming = []
        for e in evs:
            s = get_start(e)
            if s < now_utc:
                past.append(e)
            else:
                upcoming.append(e)

        def fmt_list(lst):
            items = []
            for e in lst:
                s = get_start(e)
                en = get_end(e)
                items.append({
                    "title": get_title(e),
                    "start": s.isoformat(),
                    "end":   en.isoformat() if en else "",
                })
            return items

        data = {
            "past":     fmt_list(past),
            "upcoming": fmt_list(upcoming),
        }
        return json.dumps(data, ensure_ascii=False, indent=2)

    def _extract_tags(self, raw: str) -> Dict[str, Any]:
        """Ищет <calendar_data> и <calendar_delete> и парсит JSON внутри."""
        out: Dict[str, Any] = {}
        m1 = re.search(r"<calendar_data>(\{.*?\})</calendar_data>", raw, re.S)
        if m1:
            out["create"] = json.loads(m1.group(1))
            out["view"] = json.loads(m1.group(1))
        m2 = re.search(
            r"<calendar_delete>(\{.*?\})</calendar_delete>", raw, re.S)
        if m2:
            out["delete"] = json.loads(m2.group(1))
        return out

    def _strip_tags(self, raw: str) -> str:
        return re.sub(r"</?calendar_[^>]+>", "", raw).strip()

    def _no_action(self) -> Dict[str, Any]:
        return {
            "calendar_data": None,
            "should_create_event": False,
            "should_delete_event": False,
        }
