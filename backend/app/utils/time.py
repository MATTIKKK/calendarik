from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, status
from zoneinfo import ZoneInfo
from app.schemas.calendar import CalendarEventResponse
from app.models import CalendarEvent
from typing import Optional, Tuple


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
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo(user_tz))
    return dt.astimezone(timezone.utc)


def validate_and_convert_times(
    start_time: datetime,
    end_time: Optional[datetime],
    user_tz: str
) -> Tuple[datetime, datetime]:
    # конвертируем start
    start_utc = to_utc(start_time, user_tz)

    # если end_time не передали — дефолт +1 час
    if end_time is None:
        end_utc = start_utc + timedelta(hours=1)
    else:
        end_utc = to_utc(end_time, user_tz)
        if end_utc <= start_utc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="`end_time` must be after `start_time`."
            )

    return start_utc, end_utc
