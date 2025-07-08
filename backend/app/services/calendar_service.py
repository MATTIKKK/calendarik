from __future__ import annotations
from datetime import datetime, timedelta, time, timezone
from typing import List, Mapping, Tuple
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from sqlalchemy.exc import SQLAlchemyError
from dateutil.parser import isoparse

from app.models import CalendarEvent, User
from app.utils.time import to_utc, to_local, validate_and_convert_times
from app.core.errors import ConflictError, PastTimeError



class CalendarService:
    """API-обёртка вокруг таблицы CalendarEvent (в БД всё в UTC)."""

    def __init__(self, db: Session, user: User) -> None:
        self.db = db
        self.user = user
        self.tz = ZoneInfo(user.timezone)

    # ───────────────── internal helpers ─────────────────
    def _window_query(self, start: datetime, end: datetime):
        return (
            CalendarEvent.owner_id == self.user.id,
            CalendarEvent.start_time < end,
            or_(CalendarEvent.end_time.is_(None), CalendarEvent.end_time > start)
        )

    # ───────────────── чтение ─────────────────
    def get_events_for_day(self, date_local: datetime) -> List[CalendarEvent]:
        loc_start = datetime.combine(date_local.date(), time.min, tzinfo=self.tz)
        utc_start = loc_start.astimezone(timezone.utc)
        utc_end   = utc_start + timedelta(days=1)
        return (
            self.db.query(CalendarEvent)
            .filter(and_(*self._window_query(utc_start, utc_end)))
            .order_by(CalendarEvent.start_time)
            .all()
        )

    # ───────────────── свободные слоты ─────────────────
    def find_free_slots(
        self,
        date_from_local: datetime,
        days: int = 7,
        min_minutes: int = 30,
        workday_start: time = time(0, 0),
        workday_end:   time = time(23, 59),
    ) -> List[dict]:

        if date_from_local.tzinfo is None:
            date_from_local = date_from_local.replace(tzinfo=self.tz)

        loc_start = datetime.combine(
            date_from_local.astimezone(self.tz).date(), workday_start, tzinfo=self.tz
        )
        utc_start = loc_start.astimezone(timezone.utc)
        utc_end   = utc_start + timedelta(days=days)

        events = (
            self.db.query(CalendarEvent)
            .filter(and_(*self._window_query(utc_start, utc_end)))
            .order_by(CalendarEvent.start_time)
            .all()
        )

        # merge busy intervals
        merged: List[Tuple[datetime, datetime]] = []
        for ev in events:
            s = to_utc(ev.start_time, self.user.timezone)
            e = to_utc(ev.end_time or (ev.start_time + timedelta(hours=1)), self.user.timezone)
            s = max(s, utc_start)
            if not merged or s > merged[-1][1]:
                merged.append((s, e))
            else:
                merged[-1] = (merged[-1][0], max(merged[-1][1], e))

        free: List[dict] = []
        cursor = utc_start
        idx = 0
        wd_start_loc, wd_end_loc = workday_start, workday_end

        while cursor < utc_end:
            cur_loc = cursor.astimezone(self.tz)

            if cur_loc.time() < wd_start_loc:
                cursor = datetime.combine(
                    cur_loc.date(), wd_start_loc, tzinfo=self.tz
                ).astimezone(timezone.utc)
                cur_loc = cursor.astimezone(self.tz)

            if cur_loc.time() >= wd_end_loc:
                next_day = cur_loc.date() + timedelta(days=1)
                cursor = datetime.combine(next_day, wd_start_loc, tzinfo=self.tz).astimezone(timezone.utc)
                continue

            if idx < len(merged):
                busy_start, busy_end = merged[idx]
            else:
                busy_start, busy_end = utc_end, utc_end

            if cursor < busy_start:
                gap_min = int((busy_start - cursor).total_seconds() // 60)
                if gap_min >= min_minutes:
                    free.append({
                        "start": cursor.astimezone(self.tz),
                        "end":   busy_start.astimezone(self.tz),
                        "duration_minutes": gap_min,
                    })
                cursor = busy_start
            else:
                cursor = busy_end
                idx += 1

        return free

    # ───────────────── форматирование ─────────────────
    def format_events_for_ai(
        self,
        events: List[CalendarEvent],
        *,
        lang: str = "ru",
        hide_past: bool = False,
    ) -> str:
        i18n = {
            "ru": {"no":"— нет событий —","past":"Уже прошло:","upc":"Ещё впереди:"},
            "en": {"no":"— no events —","past":"Already done:","upc":"Coming up:"},
        }[lang[:2]]

        if not events:
            return i18n["no"]

        now = datetime.now(self.tz)
        past, upc = [], []
        for ev in events:
            loc = to_local(ev, self.user.timezone)
            (past if loc.end_time and loc.end_time < now else upc).append(loc)

        if hide_past:
            past = []
        if not past and not upc:
            return i18n["no"]

        past.sort(key=lambda e: e.start_time)
        upc.sort(key=lambda e: e.start_time)

        offset = int(self.tz.utcoffset(now).total_seconds() // 3600)
        out = [f"( {self.user.timezone}, UTC{offset:+d} )"]
        if past:
            out.append(f"\n{i18n['past']}")
            out += [f"• {e.start_time:%H:%M}-{e.end_time:%H:%M}  {e.title}" for e in past]
        if upc:
            out.append(f"\n{i18n['upc']}")
            out += [f"• {e.start_time:%H:%M}-{e.end_time:%H:%M}  {e.title}" for e in upc]
        return "\n".join(out)

    @staticmethod
    def format_free_slots_for_ai(slots: List[dict], *, lang: str = "ru") -> str:
        if not slots:
            return "Свободных окон нет." if lang.startswith("ru") else "No free slots."
        lines = []
        for s in slots:
            st = s["start"].strftime("%H:%M")
            en = s["end"].strftime("%H:%M")
            mins = s["duration_minutes"]
            dur = f"{mins//60} ч {mins%60} м" if lang.startswith("ru") else f"{mins//60} h {mins%60} m"
            lines.append(f"• {st} – {en}  ({dur})")
        return "\n".join(lines)

    # ───────────────── СОЗДАНИЕ ─────────────────
    def create_event(self, data: Mapping[str, str]) -> CalendarEvent:
        title, start_raw = data.get("title"), data.get("start")
        if not title or not start_raw:
            raise ValueError("Both 'title' and 'start' are required.")

        start_raw = isoparse(start_raw)
        end_raw   = isoparse(data["end"]) if data.get("end") else None
        start, end = validate_and_convert_times(start_raw, end_raw, self.user.timezone)

        if start < datetime.now(timezone.utc):
            raise PastTimeError(start)

        occupied_until = end or (start + timedelta(hours=1))
        conflict = (
            self.db.query(CalendarEvent)
            .filter(and_(*self._window_query(start, occupied_until)))
            .first()
        )
        if conflict:
            raise ConflictError(conflict)

        ev = CalendarEvent(
            owner_id=self.user.id,
            title=title,
            start_time=start,
            end_time=end,
            description=data.get("description"),
        )
        try:
            self.db.add(ev)
            self.db.commit()
            self.db.refresh(ev)
            return ev
        except SQLAlchemyError:
            self.db.rollback()
            raise

    # ───────────────── УДАЛЕНИЕ ─────────────────
    def delete_event_by_title_and_date(self, params: Mapping[str, str]) -> bool:
        title = params.get("title", "").strip()
        date_raw = params.get("date")
        if not title or not date_raw:
            raise ValueError("Both 'title' and 'date' are required")

        loc_midnight = datetime.fromisoformat(date_raw).replace(tzinfo=self.tz)
        utc_start = loc_midnight.astimezone(timezone.utc)
        utc_end   = utc_start + timedelta(days=1)

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
            self.db.delete(ev)
            self.db.commit()
            return True
        return False


    def list_events_between(self, start: datetime, end: datetime):
        """
        Возвращает все события пользователя, которые хоть как-то
        пересекают интервал [start, end) (в UTC).
        """
        return (
            self.db.query(CalendarEvent)
            .filter(
                CalendarEvent.owner_id == self.user.id,
                # перекрытие интервала:
                or_(
                    and_(CalendarEvent.start_time >= start, CalendarEvent.start_time < end),      # началось внутри
                    and_(CalendarEvent.end_time   >  start, CalendarEvent.end_time   <= end),     # закончилось внутри
                    and_(CalendarEvent.start_time <= start, CalendarEvent.end_time   >= end),     # накрыло полностью
                )
            )
            .order_by(CalendarEvent.start_time)
            .all()
        )