from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, validator
from datetime import datetime

from app.core.database import get_db
from app.routes.auth import get_current_user
from app.models import User, Chat, ChatMessage, CalendarEvent
from app.services.ai_service import AIService
from app.services.calendar_service import CalendarService

router = APIRouter()
ai_service = AIService()

class AIMessageRequest(BaseModel):
    message: str
    chat_id: Optional[int] = None
    personality: Optional[str] = None
    language: Optional[str] = None

    @validator("personality")
    def validate_personality(cls, v):
        if v is None:
            return v
        valid_personalities = ["assistant", "coach", "friend", "girlfriend", "boyfriend"]
        if v not in valid_personalities:
            raise ValueError(f"Invalid personality. Must be one of: {', '.join(valid_personalities)}")
        return v

    @validator("message")
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()

class AIMessageResponse(BaseModel):
    message: str
    chat_id: int
    calendar_event_id: Optional[int] = None

@router.post("/analyze", response_model=AIMessageResponse)
async def analyze_message(
    request: AIMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        personality = request.personality or current_user.chat_personality

        language = request.language
        if not language:
            language = await ai_service.detect_language(request.message)

        calendar_service = CalendarService(db, current_user)

        chat = None
        if request.chat_id:
            chat = db.query(Chat).filter(
                Chat.id == request.chat_id,
                Chat.owner_id == current_user.id
            ).first()
            if not chat:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Chat not found"
                )
        else:
            chat = Chat(
                title=request.message[:50] + "...",
                owner_id=current_user.id
            )
            db.add(chat)
            db.commit()
            db.refresh(chat)

        analysis = await ai_service.analyze_message(
            message=request.message,
            personality=personality,
            user_gender=current_user.gender,
            language=language,
            calendar_service=calendar_service
        )

        user_message = ChatMessage(
            content=request.message,
            role="user",
            chat_id=chat.id
        )
        db.add(user_message)

        ai_message = ChatMessage(
            content=analysis["message"],
            role="assistant",
            chat_id=chat.id
        )
        db.add(ai_message)

        calendar_event_id = None
        if analysis["calendar_data"] and analysis["should_create_event"]:
            try:
                calendar_data = analysis["calendar_data"]
                if not all(key in calendar_data for key in ["title", "startTime"]):
                    raise ValueError("Missing required calendar data fields")

                start_time = datetime.fromisoformat(calendar_data["startTime"].replace('Z', '+00:00'))
                end_time = None
                if "endTime" in calendar_data:
                    end_time = datetime.fromisoformat(calendar_data["endTime"].replace('Z', '+00:00'))

                event = CalendarEvent(
                    title=calendar_data["title"],
                    description=calendar_data.get("description"),
                    start_time=start_time,
                    end_time=end_time,
                    owner_id=current_user.id
                )
                db.add(event)
                db.commit()
                db.refresh(event)
                calendar_event_id = event.id
            except (ValueError, KeyError) as e:
                print(f"[AI Route] Calendar event creation error: {e}")
                pass

        db.commit()

        return {
            "message": analysis["message"],
            "chat_id": chat.id,
            "calendar_event_id": calendar_event_id
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[AI Route] Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message"
        )
