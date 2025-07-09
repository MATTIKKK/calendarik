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
            # ИСПРАВЛЕНИЕ: ev.start_time и ev.end_time уже в UTC из БД.
            # to_utc здесь избыточен и может привести к ошибкам, если datetime уже осознанный (tz-aware).
            s = ev.start_time
            e = ev.end_time or (ev.start_time + timedelta(hours=1)) # Если end_time None, задаем дефолтную длительность (1 час)
            s = max(s, utc_start) # Убедимся, что занятый интервал не начинается раньше запрошенного окна
            if not merged or s > merged[-1][1]:
                # Добавляем новый интервал, если он не пересекается с последним объединенным
                merged.append((s, e))
            else:
                # Расширяем последний объединенный интервал, если есть пересечение
                merged[-1] = (merged[-1][0], max(merged[-1][1], e))

        free: List[dict] = []
        cursor = utc_start # Указатель на текущее время, с которого ищем свободный слот
        idx = 0 # Индекс для перебора объединенных занятых интервалов
        wd_start_loc, wd_end_loc = workday_start, workday_end # Начало и конец рабочего дня в локальном времени

        while cursor < utc_end:
            cur_loc = cursor.astimezone(self.tz) # Текущая позиция курсора в локальном времени пользователя

            # Пропускаем время до начала рабочего дня
            if cur_loc.time() < wd_start_loc:
                cursor = datetime.combine(
                    cur_loc.date(), wd_start_loc, tzinfo=self.tz
                ).astimezone(timezone.utc)
                cur_loc = cursor.astimezone(self.tz) # Обновляем cur_loc после перемещения курсора

            # Пропускаем время после окончания рабочего дня и переходим на следующий день
            if cur_loc.time() >= wd_end_loc:
                next_day = cur_loc.date() + timedelta(days=1)
                cursor = datetime.combine(next_day, wd_start_loc, tzinfo=self.tz).astimezone(timezone.utc)
                continue # Начинаем новый цикл со следующего дня

            # Получаем текущий занятый интервал
            if idx < len(merged):
                busy_start, busy_end = merged[idx]
            else:
                # Если все занятые интервалы пройдены, весь оставшийся период считается свободным
                busy_start, busy_end = utc_end, utc_end

            # Если между курсором и началом занятого интервала есть свободное время
            if cursor < busy_start:
                gap_min = int((busy_start - cursor).total_seconds() // 60)
                if gap_min >= min_minutes:
                    # Добавляем свободный слот, конвертируя время обратно в локальный часовой пояс
                    free.append({
                        "start": cursor.astimezone(self.tz),
                        "end":   busy_start.astimezone(self.tz),
                        "duration_minutes": gap_min,
                    })
                cursor = busy_start # Передвигаем курсор к концу найденного свободного слота
            else:
                # Если курсор находится внутри занятого интервала или после него,
                # перемещаем курсор к концу занятого интервала
                cursor = busy_end
                idx += 1 # Переходим к следующему занятому интервалу

        return free
    # ───────────────── форматирование ─────────────────
    def format_events_for_ai(
        self,
        events: List[CalendarEvent],
        *,
        lang: str = "ru",
        hide_past: bool = False,
        target_date: Optional[datetime.date] = None # Добавлен новый аргумент
    ) -> str:
        i18n = {
            "ru": {"no": "— нет событий —", "past": "Уже прошло:", "cur": "Идёт сейчас:", "upc": "Ещё впереди:"}, # Добавил "cur"
            "en": {"no": "— no events —", "past": "Already done:", "cur": "Currently ongoing:", "upc": "Coming up:"}, # Добавил "cur"
        }[lang[:2]]

        now = datetime.now(self.tz) # Текущее время в локальном часовом поясе пользователя

        # Формируем заголовок с датой
        display_date = target_date if target_date else now.date() # Используем target_date, если передан, иначе - текущую дату
        if lang.startswith("ru"):
            # Пример: "09 июля, 2025" (с правильными падежами для месяцев)
            date_header = display_date.strftime("%d %B, %Y").replace(
                "январь", "января").replace("февраль", "февраля").replace("март", "марта").replace("апрель", "апреля").replace("май", "мая").replace("июнь", "июня").replace("июль", "июля").replace("август", "августа").replace("сентябрь", "сентября").replace("октябрь", "октября").replace("ноябрь", "ноября").replace("декабрь", "декабря")
        else: # English
            date_header = display_date.strftime("%B %d, %Y")

        if not events:
            # Если событий нет, возвращаем только заголовок с датой и сообщение "нет событий"
            return f"{date_header}\n\n{i18n['no']}"

        past, current, upcoming = [], [], []
        for ev in events:
            loc_event = to_local(ev, self.user.timezone) # Конвертируем событие в локальное время для сравнения
            
            # Определяем статус события относительно текущего локального времени
            if loc_event.end_time and loc_event.end_time < now:
                past.append(loc_event)
            elif loc_event.start_time <= now and (loc_event.end_time is None or loc_event.end_time > now):
                # Событие началось и ещё не закончилось (или не имеет конца)
                current.append(loc_event)
            else:
                # Событие в будущем
                upcoming.append(loc_event)

        # Применяем фильтр hide_past
        if hide_past:
            past = []
        
        # Если после фильтрации событий не осталось
        if not past and not current and not upcoming:
             return f"{date_header}\n\n{i18n['no']}"

        # Сортировка событий в каждой категории
        past.sort(key=lambda e: e.start_time)
        current.sort(key=lambda e: e.start_time)
        upcoming.sort(key=lambda e: e.start_time)

        # Вычисляем смещение UTC для отображения в скобках
        offset = int(self.tz.utcoffset(now).total_seconds() // 3600)
        
        # Формируем итоговый список строк
        out = [
            f"{date_header}", # Дата в первой строке, как просил промпт для LLM
            f"( {self.user.timezone}, UTC{offset:+d} )" # Информация о часовом поясе
        ]

        if past:
            out.append(f"\n{i18n['past']}")
            out += [f"• {e.start_time:%H:%M}-{e.end_time:%H:%M}  {e.title}" for e in past]
        if current:
            out.append(f"\n{i18n['cur']}")
            out += [f"• {e.start_time:%H:%M}-{e.end_time:%H:%M}  {e.title}" for e in current]
        if upcoming:
            out.append(f"\n{i18n['upc']}")
            out += [f"• {e.start_time:%H:%M}-{e.end_time:%H:%M}  {e.title}" for e in upcoming]
            
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
        title = data.get("title")
        start_raw = data.get("start")
        end_raw = data.get("end") # end_raw теперь может быть None, если LLM передала duration

        if not title or not start_raw:
            # AIService.analyze_message уже делает эту проверку, но дублирование для безопасности не повредит
            raise ValueError("Both 'title' and 'start' are required to create an event.")

        start = isoparse(start_raw)
        # Если end_raw не предоставлен, то здесь end будет None.
        # В AIService.analyze_message мы гарантируем, что 'end' уже будет вычислен на основе 'duration'.
        # Поэтому на этом этапе 'end' уже должен быть datetime-объектом, если все дошло досюда.
        end = isoparse(end_raw) if end_raw else None 

        # validate_and_convert_times:
        # 1. Применяет часовой пояс пользователя к start/end, если они не осознанные (naive).
        # 2. Конвертирует start/end в UTC.
        # 3. Проверяет, что start не в прошлом (если это не так, выбрасывает PastTimeError).
        # 4. Если end_time не предоставлен, устанавливает его как start_time + 1 час.
        #    (Это важный аспект, если LLM не всегда предоставит duration/end.)
        start_utc, end_utc = validate_and_convert_times(start, end, self.user.timezone)

        # Проверка на то, что событие не в прошлом, уже выполняется в validate_and_convert_times.
        # Этот if можно убрать, так как PastTimeError будет выброшен раньше.
        # if start_utc < datetime.now(timezone.utc):
        #     raise PastTimeError(start_utc)

        # Интервал, который событие будет занимать.
        # Используем end_utc, которое уже гарантированно будет установлено (либо из LLM, либо 1 час по умолчанию)
        occupied_until = end_utc
        
        # Проверяем на конфликты с существующими событиями
        conflict = (
            self.db.query(CalendarEvent)
            .filter(and_(*self._window_query(start_utc, occupied_until)))
            .first()
        )
        if conflict:
            raise ConflictError(conflict)

        ev = CalendarEvent(
            owner_id=self.user.id,
            title=title,
            start_time=start_utc,
            end_time=end_utc, # Используем end_utc
            description=data.get("description"),
        )
        try:
            self.db.add(ev)
            self.db.commit()
            self.db.refresh(ev)
            return ev
        except SQLAlchemyError:
            self.db.rollback()
            raise # Перевыбрасываем исключение после отката транзакции

    # ───────────────── УДАЛЕНИЕ ─────────────────
    def delete_event_by_id(self, event_id: int) -> bool:
        """
        Удаляет событие по его числовому идентификатору (event_id).
        """
        ev = (
            self.db.query(CalendarEvent)
            .filter(
                CalendarEvent.owner_id == self.user.id,
                CalendarEvent.id == event_id
            )
            .first()
        )
        if ev:
            self.db.delete(ev)
            self.db.commit()
            return True
        return False

    # НОВЫЙ МЕТОД: Удаление события по названию, дате и точному времени начала
    def delete_event_by_title_and_date(self, params: Mapping[str, str]) -> bool:
        """
        Удаляет событие по его названию, дате и точному времени начала.
        Используется, если delete_event_by_title_and_date нашел несколько совпадений.
        """
        title = params.get("title", "").strip()
        date_raw = params.get("date")
        start_raw = params.get("start") # Точное время начала (ISO-формат)

        if not title or not date_raw or not start_raw:
            raise ValueError("Title, date, and start time are all required for precise deletion.")

        loc_midnight = datetime.fromisoformat(date_raw).replace(tzinfo=self.tz)
        utc_start_of_day = loc_midnight.astimezone(timezone.utc)
        utc_end_of_day   = utc_start_of_day + timedelta(days=1)

        try:
            # Парсим точное время начала события в UTC
            specific_start_utc = isoparse(start_raw).astimezone(timezone.utc)
        except ValueError:
            raise ValueError("Invalid start time format provided for deletion.")

        ev = (
            self.db.query(CalendarEvent)
            .filter(
                CalendarEvent.owner_id == self.user.id,
                CalendarEvent.title.ilike(f"%{title}%"),
                CalendarEvent.start_time == specific_start_utc, # Точное совпадение времени начала
                CalendarEvent.start_time >= utc_start_of_day, # Убеждаемся, что в пределах дня
                CalendarEvent.start_time <  utc_end_of_day,
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
                    and_(CalendarEvent.start_time >= start, CalendarEvent.start_time < end),      # началось внутри интервала [start, end)
                    and_(CalendarEvent.end_time   >  start, CalendarEvent.end_time   <= end),     # закончилось внутри интервала (start, end]
                    and_(CalendarEvent.start_time <= start, CalendarEvent.end_time   >= end),     # накрыло полностью интервал [start, end]
                    # Добавляем случай, когда end_time is None (бесконечное событие, которое пересекает start)
                    and_(CalendarEvent.start_time < end, CalendarEvent.end_time.is_(None))
                )
            )
            .order_by(CalendarEvent.start_time)
            .all()
        )