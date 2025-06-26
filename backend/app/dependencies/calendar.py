from datetime import datetime, timedelta
from typing import Optional, Tuple

from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.user import get_current_user
from app.models import CalendarEvent, User
from app.utils.time import to_utc
from app.services.calendar_service import CalendarService

def get_calendar_service(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CalendarService:
    return CalendarService(db, current_user)



def get_existing_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CalendarEvent:
    ev = (
        db.query(CalendarEvent)
        .filter_by(id=event_id, owner_id=current_user.id)
        .first()
    )
    if not ev:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Event not found")
    return ev

def parse_date_range(
    start_date: Optional[datetime] = Query(None),
    end_date:   Optional[datetime] = Query(None),
    user:       User = Depends(get_current_user),
) -> Tuple[Optional[datetime], Optional[datetime]]:
    """
    Инжектит в роутер уже переведённые в UTC границы (или None).
    """
    tz = user.timezone
    start_utc = to_utc(start_date, tz) if start_date else None
    end_utc   = to_utc(end_date, tz) + timedelta(days=1) if end_date else None
    return start_utc, end_utc

