from typing import List, Optional, Tuple
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, exc
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.user import get_current_user
from app.dependencies.calendar import get_existing_event, parse_date_range
from app.models import CalendarEvent, User
from app.schemas.calendar import (
    CalendarEventCreate,
    CalendarEventUpdate,
    CalendarEventResponse,
)

from app.utils.time import validate_and_convert_times, to_local

router = APIRouter()


@router.post(
    "/events",
    response_model=CalendarEventResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_event(
    event_in: CalendarEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CalendarEventResponse:
    # Конвертируем и валидируем времена
    start_utc, end_utc = validate_and_convert_times(
        start_time=event_in.start_time,
        end_time=event_in.end_time,
        user_tz=current_user.timezone,
    )

    # Создаём новый объект
    new_ev = CalendarEvent(
        owner_id=current_user.id,
        start_time=start_utc,
        end_time=end_utc,
        **event_in.dict(exclude={"start_time", "end_time"}),
    )

    # Сохраняем в БД с обработкой ошибок
    try:
        db.add(new_ev)
        db.commit()
        db.refresh(new_ev)
    except exc.SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create event",
        )

    return to_local(new_ev, current_user.timezone)


@router.get(
    "/events",
    response_model=List[CalendarEventResponse],
)
def list_events(
    date_range: Tuple[Optional[datetime],
                      Optional[datetime]] = Depends(parse_date_range),
    db:         Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[CalendarEventResponse]:
    start_utc, end_utc = date_range

    q = db.query(CalendarEvent).filter(
        CalendarEvent.owner_id == current_user.id)

    if start_utc is not None and end_utc is not None:
        q = q.filter(
            CalendarEvent.start_time < end_utc,
            or_(
                CalendarEvent.end_time.is_(None),
                CalendarEvent.end_time >= start_utc,
            ),
        )
    # только начало
    elif start_utc is not None:
        q = q.filter(
            or_(
                CalendarEvent.end_time.is_(None),
                CalendarEvent.end_time >= start_utc,
            )
        )
    # только конец
    elif end_utc is not None:
        q = q.filter(CalendarEvent.start_time < end_utc)

    events = q.order_by(CalendarEvent.start_time).all()
    return [to_local(ev, current_user.timezone) for ev in events]


@router.get(
    "/events/{event_id}",
    response_model=CalendarEventResponse,
)
def get_event(
    ev: CalendarEvent = Depends(get_existing_event),
    current_user: User = Depends(get_current_user),
) -> CalendarEventResponse:
    return to_local(ev, current_user.timezone)


@router.put(
    "/events/{event_id}",
    response_model=CalendarEventResponse,
)
def update_event(
    ev:      CalendarEvent = Depends(get_existing_event),
    upd:     CalendarEventUpdate = Depends(),
    db:      Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CalendarEventResponse:
    tz = current_user.timezone
    data = upd.dict(exclude_unset=True)

    if "start_time" in data:
        data["start_time"] = validate_and_convert_times(
            start_time=data["start_time"],
            end_time=None,
            user_tz=tz,
        )[0]

    if "end_time" in data and data["end_time"] is not None:
        data["end_time"] = validate_and_convert_times(
            start_time=ev.start_time,
            end_time=data["end_time"],
            user_tz=tz,
        )[1]

    # Проверяем корректность интервала
    if (
        ("start_time" in data or "end_time" in data)
        and data.get("end_time", ev.end_time) is not None
        and data["end_time"] <= data.get("start_time", ev.start_time)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end_time must be after start_time",
        )

    for field, val in data.items():
        setattr(ev, field, val)

    try:
        db.commit()
        db.refresh(ev)
    except exc.SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update event",
        )

    return to_local(ev, tz)


@router.delete(
    "/events/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_event(
    ev: CalendarEvent = Depends(get_existing_event),
    db: Session = Depends(get_db),
):
    try:
        db.delete(ev)
        db.commit()
    except exc.SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete event",
        )
    return None
