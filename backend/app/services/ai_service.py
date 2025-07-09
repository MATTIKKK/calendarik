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

    def build_calendar_context(self, calendar_service, target_date_local: Optional[datetime.date] = None, is_weekly_request: bool = False) -> str:
        """
        Builds a formatted calendar context for the AI, showing events for a specific day or week.
        
        Args:
            calendar_service: An instance of CalendarService.
            target_date_local: The specific date (in user's local timezone) for which to fetch events.
                               If None, defaults to the current local date.
            is_weekly_request: If True, fetches and formats events for the current week (7 days from target_date_local).
        
        Returns:
            A string containing formatted calendar events.
        """
        user_tz = ZoneInfo(calendar_service.user.timezone)
        now_local = datetime.now(user_tz)

        if target_date_local is None:
            target_date_local = now_local.date() # Ensure it's a date object

        if is_weekly_request:
            weekly_context_parts = []
            start_of_week_date = target_date_local # Start from the target_date for the week
            end_of_week_date = start_of_week_date + timedelta(days=6) # 7 days total

            current_day_iter = start_of_week_date
            while current_day_iter <= end_of_week_date:
                start_of_current_day_local = datetime.combine(current_day_iter, datetime.min.time(), tzinfo=user_tz)
                end_of_current_day_local = datetime.combine(current_day_iter, datetime.max.time(), tzinfo=user_tz)
                
                start_utc = start_of_current_day_local.astimezone(timezone.utc)
                end_utc = end_of_current_day_local.astimezone(timezone.utc)

                events_for_day = calendar_service.list_events_between(start_utc, end_utc)
                
                formatted_day_events = calendar_service.format_events_for_ai(
                    events_for_day, 
                    lang=calendar_service.user.preferred_language, 
                    hide_past=False,
                    target_date=current_day_iter # Pass the specific date for the header
                )
                weekly_context_parts.append(formatted_day_events)
                current_day_iter += timedelta(days=1)
            
            # Combine parts with a distinct separator for the LLM
            return "\n\n---\n\n".join(weekly_context_parts) + "\n"
            
        else: # Single day request
            start_of_target_day_local = datetime.combine(target_date_local, datetime.min.time(), tzinfo=user_tz)
            end_of_target_day_local = datetime.combine(target_date_local, datetime.max.time(), tzinfo=user_tz)
            
            start_utc = start_of_target_day_local.astimezone(timezone.utc)
            end_utc = end_of_target_day_local.astimezone(timezone.utc)

            events = calendar_service.list_events_between(start_utc, end_utc)

            formatted_events = calendar_service.format_events_for_ai(
                events, 
                lang=calendar_service.user.preferred_language, 
                hide_past=False,
                target_date=target_date_local # Pass the specific date for the header
            )
            
            # The format_events_for_ai now handles the full header including "no events" or event list
            # So, we just return its result directly, followed by a newline for consistency.
            return formatted_events + "\n"

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
        """
        Creates the system prompt for the AI model, defining its persona, language,
        and providing detailed instructions for calendar interaction.
        """
        personas = {
            "assistant": (
                "You are a professional, highly efficient, and concise AI assistant. "
                "Your tone is formal, objective, and focused on delivering information clearly and directly, "
                "without unnecessary conversational fillers or emotional expressions. "
                "Prioritize accuracy and brevity in your responses."
            ),
            "coach": (
                "You are an energetic, inspiring, and motivational coach. "
                "Your tone is uplifting, dynamic, and action-oriented. "
                "Encourage and empower the user, using positive affirmations and enthusiastic language. "
                "Focus on progress, goals, and overcoming challenges. "
                "Feel free to use exclamation points and encouraging phrases."
            ),
            "friend": (
                "You're the user's best friend. Your tone is casual, informal, and supportive, like a real friend. "
                "Use everyday language, slang where appropriate, and express genuine care and understanding. "
                "Feel free to share brief, relatable opinions or observations. "
                "Focus on empathy, camaraderie, and friendly advice."
            ),
            "girlfriend": (
                "You're a sweet and caring girlfriend. Be emotionally supportive and warm. "
                "Feel free to add emojis at the start of each bullet to show affection and warmth. "
                "Your language is gentle, affectionate, and reassuring. "
                "Show genuine interest in the user's feelings and well-being, offering comfort and understanding."
            ),
            "boyfriend": (
                "You're a protective and caring boyfriend. Make the user feel reassured and loved. "
                "Feel free to add emojis at the start of each bullet to show care and support. "
                "Your tone is steady, reliable, and thoughtful. "
                "Offer practical support and a sense of security, always prioritizing the user's comfort and safety."
            ),
        }

        gender = {
            "male":   "The user is male; adapt your responses accordingly.",
            "female": "The user is female; adapt your responses accordingly.",
            "other":  "Keep responses gender-neutral.",
        }

        calendar_instr = (
            f"{today_line}" # This is crucial for the LLM to know the current date
            "Calendar skills:\n"
            "• Your primary goal regarding the calendar is to provide the user with **relevant calendar information** or **facilitate event creation/deletion**.\n"
            "• When the user asks about their schedule, plans, or events, **identify the exact date or date range they are interested in.**\n"
            "  **If no specific date or period is mentioned but the user asks about 'plans', 'schedule', 'tasks', or 'calendar', default to TODAY.**\n"
            "  **If they ask about 'weekly plans' or 'plans for the week', default to the CURRENT WEEK (today + next 6 days).**\n"
            "  **Recognize temporal phrases like 'today', 'tomorrow', 'yesterday', 'this week', 'next week', 'Friday', 'August 1st', etc.** and adjust the context you request accordingly.\n"
            "• The `calendar_context` provided contains the requested events. It is already filtered, categorized (Past, Current, Upcoming), and includes a date header (e.g., '09 июля, 2025').\n"
            "  **If `calendar_context` contains events for multiple days (e.g., a week), each day's events will be separated by a '---' line.**\n"
            "  **Do not add any additional date headers, categorization, or formatting for events; just present the provided `calendar_context` content naturally in your reply.**\n"
            "• Only return <calendar_data> if the user explicitly asks to ADD/BOOK/SCHEDULE an event.\n"
            "• The schedules you see ARE ALREADY in the user's local time zone. Repeat the times exactly as they appear; DO NOT convert or shift them.\n"
            "• Always present times in **24-hour format** (e.g., 15:00, not 3 PM) and list each event on a new line, preceded by “- ”.\n"
            "  If the persona is 'girlfriend' or 'boyfriend', you may prepend a fitting emoji to each bullet.\n"
            "• Suggest free/available time slots.\n"
            "• Replies must be concise; avoid filler phrases such as “I'm always here” or similar supportive lines.\n"
            "• Remember you are an AI, not a living being, and cannot perform real-world actions or meetings.\n"
            "• Create events **or delete events**:\n"
            "    1) For creation, return JSON with keys: title, start, end (optional), duration (optional, e.g., \"2 days\", \"3h\").\n"
            "       Wrap exactly like <calendar_data>{ ... }</calendar_data>\n"
            "    2) For deletion, return JSON with keys: title, date (YYYY-MM-DD).\n"
            "       Wrap exactly like <calendar_delete>{ ... }</calendar_delete>\n"
            "    2b) To delete a *specific* event on that date, add either:\n"
            "        • \"start\": ISO-datetime of the event’s start (e.g., \"2025-07-09T11:00\") **or**\n"
            "        • \"event_id\": numeric id of the event (preferred if shown).\n"
            "    2c) If neither \"start\" nor \"event_id\" is provided and multiple matches exist,\n"
            "        ask the user to clarify which one to delete before returning <calendar_delete>.\n"
            "    3) After a blank line, write the friendly reply. **Never** mention the tags or JSON.\n"
        )
        
        parts = [
            personas.get(personality, personas["assistant"]),
            gender.get(user_gender, gender["other"]),
            f"Respond in {language}.",
            calendar_instr,
        ]
        if calendar_context:
            # We want to send the full context to the LLM for better understanding.
            # If token limits become an issue, we'd need a more advanced summarization strategy.
            parts.append(calendar_context) 
        return "\n".join(parts)

    def _parse_duration(self, duration_str: str) -> timedelta:
        """
        Parses a duration string (e.g., "2 days", "3h", "1d 5h") into a timedelta object.
        """
        total_duration = timedelta(0)

        # Days
        days_match = re.search(
            r'(\d+)\s*(?:d|день|дня|дней)', duration_str, re.IGNORECASE)
        if days_match:
            total_duration += timedelta(days=int(days_match.group(1)))

        # Hours
        hours_match = re.search(
            r'(\d+)\s*(?:h|час|часа|часов)', duration_str, re.IGNORECASE)
        if hours_match:
            total_duration += timedelta(hours=int(hours_match.group(1)))

        # Minutes (Optional, add if needed)
        minutes_match = re.search(
            r'(\d+)\s*(?:m|мин|минут|минуты)', duration_str, re.IGNORECASE)
        if minutes_match:
            total_duration += timedelta(minutes=int(minutes_match.group(1)))

        return total_duration

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
        """
        Analyzes the user's message, interacts with the AI model, and processes calendar actions.
        """
        try:
            # 1) Determine language
            detected = await self.detect_language(message)
            lang = detected if detected in (
                "English", "Russian") else "English"

            # 3) Get current local time and today's string for system prompt
            user_tz = ZoneInfo(
                calendar_service.user.timezone) if calendar_service else timezone.utc
            now_local = datetime.now(user_tz)
            today_str = now_local.strftime("%Y-%m-%d")
            today_line = f"Today is {today_str} in the user's timezone.\n"

            # --- CRITICAL CHANGE: Dynamic context building based on LLM's understanding ---
            # Instead of parsing keywords here, we rely on the LLM to determine the date/period.
            # We prepare a base system prompt without calendar_context first.
            # Then we let the LLM generate a response, which might implicitly tell us
            # what date/period it *thinks* it needs context for, or if it needs to create/delete.

            # Step 1: Initial LLM call to understand intent and date/period
            # We send history and a general calendar instruction for it to understand context.
            # We'll then decide *what* calendar_context to inject for the final LLM call.

            # Preliminary AI call to allow LLM to decide on date/period
            # This is a simplification. A more robust way uses function calling.
            # For now, we'll give the LLM the prompt and let it respond.
            # If the response contains indicators for a specific date/week, we'll use that.
            # Otherwise, we'll default to today.

            # IMPORTANT: The core idea is to let the LLM decide which day/period the user refers to.
            # However, your current architecture only allows us to inject the *calendar_context*
            # *before* the main ask_gpt call.
            # So, we cannot have the LLM "tell us" what date it wants context for *during* the call.
            # We must infer it from the user's message *before* the call.

            # Re-implementing dynamic context to match prompt instructions (for pre-injection)
            target_date_for_context = now_local.date() # Default to today
            is_weekly_request = False
            message_lower = message.lower()

            if "неделю" in message_lower or "на этой неделе" in message_lower or "планы на неделю" in message_lower:
                is_weekly_request = True
                # target_date_for_context remains now_local.date() as it's the start of the week
            elif "завтра" in message_lower:
                target_date_for_context = (now_local + timedelta(days=1)).date()
            elif "сегодня" in message_lower:
                target_date_for_context = now_local.date()
            # If specific day is requested (e.g., "пятницу", "1 августа"),
            # this would ideally be handled by a more robust date parser or LLM tool-use.
            # For now, if no specific keyword for tomorrow/week is found, and it's a "plan" query, it defaults to today.
            elif any(keyword in message_lower for keyword in ["планы", "расписание", "дела", "календарь"]):
                 target_date_for_context = now_local.date() # Already defaulted to today, explicit for clarity

            # Build calendar context based on the inferred date/period
            calendar_context = ""
            if calendar_service:
                calendar_context = self.build_calendar_context(
                    calendar_service, 
                    target_date_local=target_date_for_context, 
                    is_weekly_request=is_weekly_request
                )
                
            history = self.memory.get(chat_id)[:]
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

            # 7) Parse JSON objects
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

            # --- Logic for handling duration and calculating end time ---
            if calendar_data:
                title = calendar_data.get("title")
                start_time_str = calendar_data.get("start")
                duration_str = calendar_data.get("duration")
                end_time_str = calendar_data.get("end")

                if not title or not start_time_str:
                    return {
                        "message": "Для создания события требуется название и время начала.",
                        "calendar_data": None,
                        "should_create_event": False,
                        "event_id": None,
                        "was_deleted": False,
                    }

                if duration_str and not end_time_str:
                    try:
                        start_dt = datetime.fromisoformat(start_time_str)
                        duration_delta = self._parse_duration(duration_str)

                        if duration_delta == timedelta(0) and duration_str not in ["0", "0h", "0m"]:
                            return {
                                "message": f"Не удалось определить продолжительность '{duration_str}'. Пожалуйста, уточните, сколько времени займет событие или укажите время окончания.",
                                "calendar_data": None,
                                "should_create_event": False,
                                "event_id": None,
                                "was_deleted": False,
                            }

                        calendar_data["end"] = (
                            start_dt + duration_delta).isoformat()
                    except ValueError as ve:
                        return {
                            "message": f"Произошла ошибка при обработке времени начала или продолжительности: {ve}. Пожалуйста, проверьте формат.",
                            "calendar_data": None,
                            "should_create_event": False,
                            "event_id": None,
                            "was_deleted": False,
                        }
                    except Exception as e:
                        print(f"Error calculating end time: {e}")
                        return {
                            "message": "Произошла ошибка при расчете времени окончания. Пожалуйста, попробуйте еще раз или укажите точное время окончания.",
                            "calendar_data": None,
                            "should_create_event": False,
                            "event_id": None,
                            "was_deleted": False,
                        }
                elif not end_time_str and not duration_str:
                    return {
                        "message": "Пожалуйста, уточните продолжительность события или время окончания.",
                        "calendar_data": None,
                        "should_create_event": False,
                        "event_id": None,
                        "was_deleted": False,
                    }

            should_save = calendar_data and all(
                k in calendar_data for k in ("title", "start", "end"))

            # 9) Apply to DB
            event_id = None
            was_deleted = False

            if calendar_service:
                # — Create
                if calendar_data and should_save:
                    try:
                        ev = calendar_service.create_event(calendar_data)
                        event_id = str(ev.id)
                    except ValueError as err:
                        return {
                            "message": f"Не могу добавить событие: {err}",
                            "calendar_data": None,
                            "should_create_event": False,
                            "event_id": None,
                            "was_deleted": False,
                        }
                # — Delete
                if delete_params:
                    try:
                        # Prioritize deletion by event_id if provided by LLM
                        if "event_id" in delete_params:
                            event_id_to_delete = int(delete_params["event_id"])
                            was_deleted = calendar_service.delete_event_by_id(event_id_to_delete)
                        elif "start" in delete_params:
                            # If 'start' is provided, try more precise deletion
                            was_deleted = calendar_service.delete_event_by_title_date_start(delete_params)
                        else:
                            # Fallback to deletion by title and date (first match)
                            was_deleted = calendar_service.delete_event_by_title_and_date(delete_params)
                        
                        if not was_deleted:
                            return {
                                "message": "Не удалось найти событие для удаления. Пожалуйста, уточните название, дату или время начала.",
                                "calendar_data": None,
                                "should_create_event": False,
                                "event_id": None,
                                "was_deleted": False,
                            }

                    except ValueError as err:
                        return {
                            "message": f"Не могу удалить событие: {err}",
                            "calendar_data": None,
                            "should_create_event": False,
                            "event_id": None,
                            "was_deleted": False,
                        }
                    except Exception as e:
                        print(f"Error during delete operation: {e}")
                        return {
                            "message": "Произошла ошибка при попытке удаления события. Пожалуйста, попробуйте еще раз.",
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
        """
        Detects the language of the given text using the AI model.
        """
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