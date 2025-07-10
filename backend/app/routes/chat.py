from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    Query,
)

from app.dependencies.chat import get_chat_service
from app.dependencies.calendar import get_calendar_service
from app.dependencies.user import get_current_user
from app.models import User, Chat, ChatMessage
from app.schemas.ai import AIMessageRequest, AIMessageResponse
from app.services.ai_service import AIService
from app.services.chat_service import ChatService
from app.services.calendar_service import CalendarService
from app.schemas.chat import ChatMessageResponse, ChatResponse
from sqlalchemy.orm import Session
from app.core.database import get_db


router = APIRouter()
ai_service = AIService()

@router.post("/message", response_model=AIMessageResponse)
async def send_message(
    req: AIMessageRequest,
    chat_svc: ChatService = Depends(get_chat_service),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print("req in send_message", req)

    chat = chat_svc.get_or_create_chat()
    print("chat in send_message", chat)

    chat_svc.add_message(
        chat_id=chat.id,
        role="user",
        content=req.message,
    )

    analysis = await ai_service.analyze_message(
        message=req.message,
        chat_id=chat.id,
        personality=current_user.chat_personality,
        user_gender=current_user.gender,
        language=current_user.preferred_language,
        calendar_service=CalendarService(db, current_user),
    )

    print("analysis in send_message", analysis)

    ai_reply = {
        "message":      analysis["message"],
        "calendar_event_id": analysis.get("calendar_event_id"),
    }

    print("ai_reply in send_message", ai_reply)

    print("AIMessageResponse in send_message", AIMessageResponse(
        message=ai_reply["message"], chat_id=chat.id))
    
    calendar_event_id: Optional[int] = (
        int(analysis["event_id"]) if analysis.get("event_id") else None
    )
    
    chat_svc.add_message(chat.id, "assistant", analysis["message"])
    
    return AIMessageResponse(
        message=analysis["message"],
        chat_id=chat.id,
        calendar_event_id=calendar_event_id,  
    )


@router.get("/me/messages", response_model=List[ChatMessageResponse])
def get_my_messages(
    limit:     int = Query(50, gt=0),
    before_id: Optional[int] = Query(None, gt=0),
    chat_svc:  ChatService = Depends(get_chat_service),
) -> List[ChatMessageResponse]:
    chat = chat_svc.get_or_create_chat()
    return chat_svc.get_chat_messages(
        chat_id=chat.id,
        limit=limit,
        before_id=before_id,
    )


@router.get("/search", response_model=List[ChatMessageResponse])
def search_messages(
    query:   str = Query(..., min_length=1),
    limit:   int = Query(20, gt=0),
    chat_svc: ChatService = Depends(get_chat_service),
) -> List[ChatMessage]:

    chat = chat_svc.get_or_create_chat()
    return chat_svc.search_messages(chat, query=query, limit=limit)


@router.get("/me", response_model=ChatResponse)
def get_my_chat(
    chat_svc: ChatService = Depends(get_chat_service),
) -> ChatResponse:

    return chat_svc.get_or_create_chat()