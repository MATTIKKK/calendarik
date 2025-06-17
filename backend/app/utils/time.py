from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from app.schemas.calendar import CalendarEventResponse
from app.models import CalendarEvent

def to_local(event: CalendarEvent, user_tz: str) -> CalendarEventResponse:
    tz = ZoneInfo(user_tz)
    return CalendarEventResponse(
        id=event.id,
        title=event.title,
        owner_id=event.owner_id,  
        description=event.description,
        start_time=event.start_time.astimezone(tz),
        end_time=event.end_time.astimezone(tz) if event.end_time else None,
        created_at=event.created_at.astimezone(tz),
        updated_at=event.updated_at.astimezone(tz),
    )

def to_utc(dt: datetime, user_tz: str) -> datetime:
    """Если dt без смещения, трактуем как время в user_tz, затем переводим в UTC."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo(user_tz))
    return dt.astimezone(timezone.utc)