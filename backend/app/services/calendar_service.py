from __future__ import annotations

from datetime import datetime, timedelta, time, timezone
from typing import List, Mapping
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from dateutil.parser import isoparse
from sqlalchemy.exc import SQLAlchemyError

from app.models import CalendarEvent, User


class CalendarService:
    """
    API вокруг таблицы CalendarEvent для одного пользователя.
    В БД всё хранится в UTC.  На входе/выходе — локализуем.
    """

    # ─────────────────────────── init ────────────────────────────
    def __init__(self, db: Session, user: User) -> None:
        self.db = db
        self.user = user
        self.tz = ZoneInfo(user.timezone)

    # ───────────────────— internal helpers —──────────────────────
    def _window_query(self, start: datetime, end: datetime):
        """фильтр «событие перекрывает [start, end)» (оба UTC)."""
        return (
            CalendarEvent.owner_id == self.user.id,
            CalendarEvent.start_time < end,
            or_(CalendarEvent.end_time.is_(None), CalendarEvent.end_time > start),
        )

    # ───────────────────— чтение расписания —─────────────────────
    def get_events_for_day(self, date_local: datetime) -> List[CalendarEvent]:
        """Все события данного локального дня."""
        loc_start = datetime.combine(date_local.date(), time.min, tzinfo=self.tz)
        utc_start = loc_start.astimezone(timezone.utc)
        utc_end   = utc_start + timedelta(days=1)

        return (
            self.db.query(CalendarEvent)
            .filter(and_(*self._window_query(utc_start, utc_end)))
            .order_by(CalendarEvent.start_time)
            .all()
        )

    def get_events_for_week(self, date_local: datetime) -> List[CalendarEvent]:
        monday = (date_local - timedelta(days=date_local.weekday())).date()
        loc_start = datetime.combine(monday, time.min, tzinfo=self.tz)
        utc_start = loc_start.astimezone(timezone.utc)
        utc_end   = utc_start + timedelta(days=7)

        return (
            self.db.query(CalendarEvent)
            .filter(and_(*self._window_query(utc_start, utc_end)))
            .order_by(CalendarEvent.start_time)
            .all()
        )

    # ───────────────────— свободные окна —────────────────────────
    def find_free_slots(
        self,
        date_from_local: datetime,
        days: int = 7,
        min_minutes: int = 30,
        workday_start: time = time(9, 0),
        workday_end: time = time(18, 0),
    ) -> List[dict]:
        if date_from_local.tzinfo is None:
            date_from_local = date_from_local.replace(tzinfo=self.tz)
        loc_start = datetime.combine(
            date_from_local.astimezone(self.tz).date(),
            workday_start,
            tzinfo=self.tz,
        )
        
        utc_start = loc_start.astimezone(timezone.utc)
        utc_end   = utc_start + timedelta(days=days)

        events = (
            self.db.query(CalendarEvent)
            .filter(and_(*self._window_query(utc_start, utc_end)))
            .order_by(CalendarEvent.start_time)
            .all()
        )

        # превращаем в непересекающиеся отрезки
        merged: List[tuple[datetime, datetime]] = []
        for ev in events:
            # приведение «старых» naive-дат ко времени UTC
            raw_start = ev.start_time
            raw_end   = ev.end_time or (raw_start + timedelta(hours=1))
            if raw_start.tzinfo is None:
                raw_start = raw_start.replace(tzinfo=timezone.utc)
            if raw_end.tzinfo is None:
                raw_end = raw_end.replace(tzinfo=timezone.utc)

            ev_start = max(raw_start, utc_start)
            ev_end   = raw_end
            
            
            if not merged or ev_start > merged[-1][1]:
                merged.append((ev_start, ev_end))
            else:
                merged[-1] = (merged[-1][0], max(merged[-1][1], ev_end))

        free: List[dict] = []
        cursor = utc_start
        wd_start_loc = workday_start
        wd_end_loc   = workday_end

        while cursor < utc_end:
            # переводим курсор в локальное время для сравнения по часам
            cur_loc = cursor.astimezone(self.tz)

            # если до начала рабочего дня — подвинем вперёд
            if cur_loc.time() < wd_start_loc:
                cursor += timedelta(
                    hours=wd_start_loc.hour - cur_loc.hour,
                    minutes=wd_start_loc.minute - cur_loc.minute,
                )
                cur_loc = cursor.astimezone(self.tz)

            # если после конца дня — на след.утро
            if cur_loc.time() >= wd_end_loc:
                next_day = (cur_loc + timedelta(days=1)).date()
                cursor = datetime.combine(next_day, wd_start_loc, tzinfo=self.tz).astimezone(
                    timezone.utc
                )
                continue

            # ближайший занятый интервал
            busy_start, busy_end = merged[0] if merged else (utc_end, utc_end)

            if cursor < busy_start:
                gap = (busy_start - cursor).total_seconds() / 60
                if gap >= min_minutes:
                    free.append(
                        {
                            "start": cursor.astimezone(self.tz),
                            "end":   busy_start.astimezone(self.tz),
                            "duration_minutes": int(gap),
                        }
                    )
                cursor = busy_start
            else:
                cursor = busy_end
                if merged:          # защищаемся от пустого списка
                    merged.pop(0)

        return free

    # ───────────────────— форматирование —────────────────────────
    def format_events_for_ai(
        self,
        events: List[CalendarEvent],
        hide_past: bool = True,
    ) -> str:
        if not events:
            return "— нет событий —"

        tz = ZoneInfo(self.user.timezone)
        now_loc = datetime.now(tz)

        offset_hours = int(tz.utcoffset(now_loc).total_seconds() // 3600)
        tz_header = f"( {self.user.timezone}, UTC{offset_hours:+d} )"

        loc_evt: list[tuple[datetime, datetime | None, str]] = []
        for ev in events:
            # ←––––––––––––––––––––––––––––––––––––––––––––––––––
            #   если tzinfo отсутствует → считаем локальным
            # ––––––––––––––––––––––––––––––––––––––––––––––––––⚠️
            if ev.start_time.tzinfo is None:
                start = ev.start_time.replace(tzinfo=tz)
            else:
                start = ev.start_time.astimezone(tz)

            if ev.end_time:
                if ev.end_time.tzinfo is None:          # ⚠️ то же для end_time
                    end = ev.end_time.replace(tzinfo=tz)
                else:
                    end = ev.end_time.astimezone(tz)
            else:
                end = None
            # –––––––––––––––––––––––––––––––––––––––––––––––––––

            if hide_past and end and end < now_loc:
                continue
            loc_evt.append((start, end, ev.title))

        if not loc_evt:
            return "— нет событий —"

        loc_evt.sort(key=lambda t: t[0])

        lines = [tz_header]
        for start, end, title in loc_evt:
            s = start.strftime("%H:%M")
            e = end.strftime("%H:%M") if end else ""
            lines.append(f"• {s}{'-'+e if e else ''}  {title}")

        return "\n".join(lines)

    @staticmethod
    def format_free_slots_for_ai(slots: List[dict]) -> str:
        if not slots:
            return "Свободных окон нет."
        out = []
        for slot in slots:
            st = slot["start"].strftime("%a %d %b %H:%M")
            en = slot["end"].strftime("%H:%M")
            mins = slot["duration_minutes"]
            dur = f"{mins//60} ч {mins%60} м" if mins >= 60 else f"{mins} мин"
            out.append(f"• {st} – {en}  ({dur})")
        return "\n".join(out)

    # ───────────────────— СОЗДАНИЕ ────────────────────────────────
    def create_event(self, data: Mapping[str, str]) -> CalendarEvent:
        title, start_raw = data.get("title"), data.get("start")
        if not title or not start_raw:
            raise ValueError("Both 'title' and 'start' are required.")

        def _as_utc(s: str) -> datetime:
            dt = isoparse(s)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=self.tz)
            return dt.astimezone(timezone.utc)

        start = _as_utc(start_raw)
        end   = _as_utc(data["end"]) if data.get("end") else None
        if end and end <= start:
            raise ValueError("end must be after start")

        # ―― проверка конфликта ――
        occupied_until = end or (start + timedelta(hours=1))
        conflict = (
            self.db.query(CalendarEvent)
            .filter(and_(*self._window_query(start, occupied_until)))
            .first()
        )
        if conflict:
            raise ValueError(
                f"Overlaps with «{conflict.title}» "
                f"{conflict.start_time.astimezone(self.tz).strftime('%H:%M')}"
            )

        ev = CalendarEvent(
            owner_id=self.user.id,
            title=title,
            start_time=start,
            end_time=end,
            description=data.get("description"),
        )
        try:
            self.db.add(ev)
            self.db.flush()
            
            self.db.refresh(ev)
            self.db.commit() 
            return ev
        except SQLAlchemyError:
            self.db.rollback()
            raise

    # ───────────────────— УДАЛЕНИЕ ────────────────────────────────
    def delete_event_by_title_and_date(self, params: Mapping[str, str]) -> bool:
        title    = params.get("title", "").strip()            # «йога»
        date_raw = params.get("date")                         # '2025-06-18'
        if not title or not date_raw:
            raise ValueError("Both 'title' and 'date' are required")

        # границы дня в UTC
        loc_midnight = datetime.fromisoformat(date_raw).replace(tzinfo=self.tz)
        utc_start = loc_midnight.astimezone(timezone.utc)
        utc_end   = utc_start + timedelta(days=1)

        # DEBUG-лог — покажем, что ищем
        print(f"[DEL] looking for «{title}» between {utc_start} – {utc_end}")

        # ищем первое совпадение по подстроке (регистр-НЕ-чувств.)
        ev = (
            self.db.query(CalendarEvent)
            .filter(
                CalendarEvent.owner_id == self.user.id,
                CalendarEvent.title.ilike(f"%{title}%"),
                CalendarEvent.start_time >= utc_start,
                CalendarEvent.start_time <  utc_end,
            )
            .first()
        )
        if ev:
            print("[DEL] found:", ev.id, ev.title, ev.start_time)
            self.db.delete(ev)
            self.db.commit()
            return True          # удалили
        else:
            print("[DEL] nothing matched")
            return False         # ничего не нашли