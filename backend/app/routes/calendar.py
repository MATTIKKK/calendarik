from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Mapping
from datetime import datetime, timedelta         
from app.utils.time import to_utc, to_local    
from sqlalchemy import and_, or_       

from app.core.database import get_db
from app.routes.auth import get_current_user
from app.models import User, CalendarEvent
from app.schemas.calendar import CalendarEventCreate, CalendarEventUpdate, CalendarEventResponse

router = APIRouter()

@router.post("/events", response_model=CalendarEventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event: CalendarEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start_utc = to_utc(event.start_time, current_user.timezone)     
    end_utc   = to_utc(event.end_time, current_user.timezone) if event.end_time else None
    if end_utc and end_utc <= start_utc:
        raise HTTPException(status_code=400, detail="end_time must be after start_time")

    db_event = CalendarEvent(
        **event.dict(exclude={"start_time", "end_time"}),  
        start_time=start_utc,
        end_time=end_utc,
        owner_id=current_user.id,
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return to_local(db_event, current_user.timezone)      

@router.get("/events", response_model=List[CalendarEventResponse])
def get_events(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = db.query(CalendarEvent).filter(CalendarEvent.owner_id == current_user.id)
    
    if start_date:
        q = q.filter(CalendarEvent.start_time >=
                    to_utc(start_date, current_user.timezone))      
    if end_date:
        bound = to_utc(end_date, current_user.timezone) + timedelta(days=1)
        q = q.filter(
            CalendarEvent.start_time < bound,                       # начинается до конца окна
            or_(CalendarEvent.end_time.is_(None),                   #   и
                CalendarEvent.end_time >= to_utc(start_date or end_date, current_user.timezone))
        )            

    events = q.order_by(CalendarEvent.start_time).all()
    return [to_local(ev, current_user.timezone) for ev in events] 

@router.get("/events/{event_id}", response_model=CalendarEventResponse)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    event = db.query(CalendarEvent).filter(
        CalendarEvent.id == event_id,
        CalendarEvent.owner_id == current_user.id
    ).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return to_local(event, current_user.timezone)    

@router.put("/events/{event_id}", response_model=CalendarEventResponse)
def update_event(
    event_id: int,
    event_update: CalendarEventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ev = db.query(CalendarEvent).filter(
        CalendarEvent.id == event_id,
        CalendarEvent.owner_id == current_user.id
    ).first()
    if not ev:
        raise HTTPException(404, detail="Event not found")

    data = event_update.dict(exclude_unset=True)
    if "start_time" in data:
        data["start_time"] = to_utc(data["start_time"], current_user.timezone)  # ←
    if "end_time" in data and data["end_time"] is not None:
        data["end_time"] = to_utc(data["end_time"], current_user.timezone)      # ←

    if ("end_time" in data or "start_time" in data) and \
       (data.get("end_time", ev.end_time) is not None) and \
       (data.get("end_time", ev.end_time) <= data.get("start_time", ev.start_time)):
        raise HTTPException(400, detail="end_time must be after start_time")

    for k, v in data.items():
        setattr(ev, k, v)

    db.commit(); db.refresh(ev)
    return to_local(ev, current_user.timezone)  

@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_event = db.query(CalendarEvent).filter(
        CalendarEvent.id == event_id,
        CalendarEvent.owner_id == current_user.id
    ).first()
    
    if not db_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    db.delete(db_event)
    db.commit()
    return None
 