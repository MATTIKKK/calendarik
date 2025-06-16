from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, not_
from typing import List, Optional
from app.models import CalendarEvent, User

class CalendarService:
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user

    def get_events_for_day(self, date: datetime) -> List[CalendarEvent]:
        """Get all events for a specific day."""
        start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        
        return self.db.query(CalendarEvent).filter(
            CalendarEvent.owner_id == self.user.id,
            CalendarEvent.start_time >= start,
            CalendarEvent.start_time < end
        ).order_by(CalendarEvent.start_time).all()

    def get_events_for_week(self, start_date: datetime) -> List[CalendarEvent]:
        """Get all events for a week starting from start_date."""
        start = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=7)
        
        return self.db.query(CalendarEvent).filter(
            CalendarEvent.owner_id == self.user.id,
            CalendarEvent.start_time >= start,
            CalendarEvent.start_time < end
        ).order_by(CalendarEvent.start_time).all()

    def find_free_slots(self, start_date: datetime, days: int = 7, 
                       min_duration: int = 30) -> List[dict]:
        """Find free time slots in the calendar.
        
        Args:
            start_date: Starting date to look from
            days: Number of days to look ahead
            min_duration: Minimum duration in minutes
        """
        start = start_date.replace(hour=9, minute=0, second=0, microsecond=0)  # Start at 9 AM
        end = start + timedelta(days=days)
        
        # Get all events in the range
        events = self.db.query(CalendarEvent).filter(
            CalendarEvent.owner_id == self.user.id,
            CalendarEvent.start_time >= start,
            CalendarEvent.start_time < end
        ).order_by(CalendarEvent.start_time).all()

        free_slots = []
        current_time = start

        for event in events:
            # If there's enough time before the event
            if (event.start_time - current_time).total_seconds() / 60 >= min_duration:
                free_slots.append({
                    "start": current_time,
                    "end": event.start_time,
                    "duration_minutes": int((event.start_time - current_time).total_seconds() / 60)
                })
            current_time = event.end_time or (event.start_time + timedelta(hours=1))

        # Add final slot if there's time left
        if (end - current_time).total_seconds() / 60 >= min_duration:
            free_slots.append({
                "start": current_time,
                "end": end,
                "duration_minutes": int((end - current_time).total_seconds() / 60)
            })

        return free_slots

    def format_events_for_ai(self, events: List[CalendarEvent]) -> str:
        """Format events in a human-readable way for AI responses."""
        if not events:
            return "No events found."

        result = []
        for event in events:
            time_str = event.start_time.strftime("%I:%M %p")
            if event.end_time:
                time_str += f" - {event.end_time.strftime('%I:%M %p')}"
            
            desc = f"• {time_str}: {event.title}"
            if event.description:
                desc += f" ({event.description})"
            result.append(desc)

        return "\n".join(result)

    def format_free_slots_for_ai(self, slots: List[dict]) -> str:
        """Format free time slots in a human-readable way for AI responses."""
        if not slots:
            return "No free time slots found."

        result = []
        for slot in slots:
            start_str = slot["start"].strftime("%A, %B %d at %I:%M %p")
            end_str = slot["end"].strftime("%I:%M %p")
            duration_hours = slot["duration_minutes"] / 60
            
            if duration_hours >= 1:
                duration = f"{duration_hours:.1f} hours"
            else:
                duration = f"{slot['duration_minutes']} minutes"
                
            result.append(f"• {start_str} - {end_str} ({duration} available)")

        return "\n".join(result) 