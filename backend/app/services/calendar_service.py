from __future__ import annotations

from datetime import datetime, timedelta, time, timezone
from typing import List, Optional, Mapping
from zoneinfo import ZoneInfo    

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from uuid import uuid4 
from dateutil.parser import isoparse

from app.models import CalendarEvent, User
from sqlalchemy.exc import SQLAlchemyError 


class CalendarService:
    """
    High-level API вокруг таблицы CalendarEvent для одного пользователя.
    Все методы работают в UTC (или в той TZ, в которой хранятся даты в БД).
    """

    # ———————————————————————————————— init ————————————————————————————————
    def __init__(self, db: Session, user: User) -> None:
        self.db = db
        self.user = user

    # —————————————————————— internal helpers ————————————————————————
    def _window_query(self, start: datetime, end: datetime):
        """
        Возвращает SQL-фильтр «событие перекрывает [start, end)».
        
        Учтены случаи, когда end_time == None (all-day / open-ended).
        """
        return (
            CalendarEvent.owner_id == self.user.id,
            # событие начинается до конца окна  И  (заканчивается после начала окна ИЛИ end_time=None)
            CalendarEvent.start_time < end,
            or_(CalendarEvent.end_time.is_(None), CalendarEvent.end_time > start),
        )

    # ——————————————————— чтение расписания ————————————————————————
    def get_events_for_day(self, date: datetime) -> List[CalendarEvent]:
        # 00:00 UTC той же даты
        start = datetime.combine(date.date(), time.min, tzinfo=timezone.utc)
        end   = start + timedelta(days=1)

        return (
            self.db.query(CalendarEvent)
            .filter(and_(*self._window_query(start, end)))
            .order_by(CalendarEvent.start_time)
            .all()
        )

    def get_events_for_week(self, date: datetime) -> List[CalendarEvent]:
        monday = (date - timedelta(days=date.weekday())).date()
        start  = datetime.combine(monday, time.min, tzinfo=timezone.utc)
        end    = start + timedelta(days=7)

        return (
            self.db.query(CalendarEvent)
            .filter(and_(*self._window_query(start, end)))
            .order_by(CalendarEvent.start_time)
            .all()
        )

    # ——————————————————— свободные интервалы ————————————————————————
    def find_free_slots(
        self,
        date_from: datetime,
        days: int = 7,
        min_minutes: int = 30,
        workday_start: time = time(9, 0),
        workday_end: time = time(18, 0),
    ) -> List[dict]:
        """
        Возвращает список свободных слотов в рабочие часы.

        • Перекрывающиеся события “склеиваются”.  
        • Если у события нет end_time → считаем его 1-часовым.  
        • Возвращаются интервалы >= min_minutes.
        """
        window_start = datetime.combine(date_from.date(), workday_start)
        window_end = window_start + timedelta(days=days)

        events = (
            self.db.query(CalendarEvent)
            .filter(and_(*self._window_query(window_start, window_end)))
            .order_by(CalendarEvent.start_time)
            .all()
        )

        # превратим в непересекающиеся отрезки
        merged: List[tuple[datetime, datetime]] = []
        for ev in events:
            ev_start = max(ev.start_time, window_start)
            ev_end = (
                ev.end_time
                if ev.end_time is not None
                else ev_start + timedelta(hours=1)
            )
            if not merged or ev_start > merged[-1][1]:
                merged.append((ev_start, ev_end))
            else:
                # расширяем последний отрезок
                merged[-1] = (merged[-1][0], max(merged[-1][1], ev_end))

        free: List[dict] = []
        cursor = window_start

        for busy_start, busy_end in merged:
            if cursor < busy_start:
                gap = (busy_start - cursor).total_seconds() / 60
                if gap >= min_minutes:
                    free.append(
                        {
                            "start": cursor,
                            "end": busy_start,
                            "duration_minutes": int(gap),
                        }
                    )
            cursor = max(cursor, busy_end)

            # если перешагнули окончание рабочего дня — переносим курсор на утро
            if cursor.time() >= workday_end:
                next_day = cursor.date() + timedelta(days=1)
                cursor = datetime.combine(next_day, workday_start)

        # последний слот до конца окна
        if cursor < window_end:
            gap = (window_end - cursor).total_seconds() / 60
            if gap >= min_minutes:
                free.append(
                    {
                        "start": cursor,
                        "end": window_end,
                        "duration_minutes": int(gap),
                    }
                )

        return free

    # ——————————————————— форматирование для LLM ———————————————————————
    @staticmethod
    def format_events_for_ai(events: List[CalendarEvent]) -> str:
        if not events:
            return "— нет событий —"

        lines = []
        for ev in events:
            s = ev.start_time.strftime("%H:%M")
            e = ev.end_time.strftime("%H:%M") if ev.end_time else ""
            time_block = f"{s}-{e}" if e else s
            desc = f"• {time_block}  {ev.title}"
            if ev.description:
                desc += f" ({ev.description})"
            lines.append(desc)
        return "\n".join(lines)

    @staticmethod
    def format_free_slots_for_ai(slots: List[dict]) -> str:
        if not slots:
            return "Свободных окон нет."

        out = []
        for slot in slots:
            start = slot["start"].strftime("%a %d %b %H:%M")
            end = slot["end"].strftime("%H:%M")
            mins = slot["duration_minutes"]
            dur = f"{mins // 60} ч {mins % 60} м" if mins >= 60 else f"{mins} мин"
            out.append(f"• {start} – {end}  ({dur})")
        return "\n".join(out)
    
    def create_event(self, data: Mapping[str, str]) -> CalendarEvent:
        """
        Сохраняет событие, присланное ИИ, и возвращает его.
        `data` должен содержать как минимум поля 'title' и 'start'.
        Формат даты — ISO-8601, без или с смещением.  Сохраняем в UTC.
        """
        # ── базовая валидация ─────────────────────────────────────────
        
        print("[TZ]", self.user.timezone)    

        title = data.get("title")
        start_raw = data.get("start")
        if not title or not start_raw:
            raise ValueError("Both 'title' and 'start' fields are required.")

        def _as_utc(dt_str: str) -> datetime:
            """
            Преобразует ISO-строку в datetime UTC.
            • Если в строке есть смещение (+05:00, Z и т.п.) – просто переводим в UTC.
            • Если смещения нет – считаем, что это время в поясе пользователя
            (self.user.timezone), после чего переводим в UTC.
            """
            dt = isoparse(dt_str)
            if dt.tzinfo is None:                          # naive
                dt = dt.replace(tzinfo=ZoneInfo(self.user.timezone))
                return dt.astimezone(timezone.utc)

        start = _as_utc(start_raw)
        end: datetime | None = _as_utc(data["end"]) if data.get("end") else None

        if end and end <= start:
            raise ValueError("end must be after start")

        # ── (опционально) проверка на пересечение ────────────────────
        # if self.db.query(CalendarEvent).filter(
        #         and_(*self._window_query(start, end or start))
        # ).first():
        #     raise ValueError("Time slot already occupied.")

        # ── создание объекта ─────────────────────────────────────────
        ev = CalendarEvent(
            owner_id=self.user.id,
            title=title,
            start_time=start,
            end_time=end,
            description=data.get("description"),
        )

        # ── сохранение ───────────────────────────────────────────────
        try:
            self.db.add(ev)
            self.db.flush()          # commit оставляем роутеру / UoW
            self.db.refresh(ev)
            return ev
        except (SQLAlchemyError, Exception):
            self.db.rollback()
            raise

