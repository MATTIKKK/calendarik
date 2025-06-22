from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.user import get_current_user
from app.models import User, Chat, ChatMessage
from app.schemas.chat import (
    AIChatRequest,
    AIChatResponse,
    ChatMessageResponse,
    ChatResponse,
)
from app.services.ai_service import AIService
from app.services.chat_service import ChatService
from app.services.calendar_service import CalendarService

router = APIRouter()

def get_chat_service(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatService:
    return ChatService(db, current_user)


def get_calendar_service(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CalendarService:
    return CalendarService(db, current_user)


ai_service = AIService()


@router.post("/message", response_model=AIChatResponse)
async def send_message(
    req: AIChatRequest,
    chat_svc: ChatService      = Depends(get_chat_service),
    cal_svc: CalendarService  = Depends(get_calendar_service),
):
    # Получаем или создаём чат
    chat = chat_svc.get_or_create_chat()

    # Сохраняем входящее сообщение
    chat_svc.add_message(chat, req.message, role="user")

    # Запрашиваем ответ у AI
    ai_reply = await ai_service.analyze_message(
        message=req.message,
        personality=req.personality or chat_svc.user.chat_personality,
        user_gender=chat_svc.user.gender,
        language=req.language or "Russian",
        calendar_service=cal_svc,
    )

    # Сохраняем ответ ассистента
    chat_svc.add_message(chat, ai_reply["message"], role="assistant")

    return AIChatResponse(message=ai_reply["message"], chat_id=chat.id)


@router.get("/{chat_id}/messages", response_model=List[ChatMessageResponse])
def get_chat_messages(
    chat_id:    int,
    limit:      int               = Query(50, gt=0),
    before_id:  Optional[int]     = Query(None, gt=0),
    chat_svc:   ChatService       = Depends(get_chat_service),
) -> List[ChatMessage]:
    # Проверяем, что чат существует и принадлежит пользователю
    chat_svc.ensure_ownership(chat_id)

    # Получаем сообщения
    return chat_svc.get_messages(chat_id, limit=limit, before_id=before_id)


@router.get("/search", response_model=List[ChatMessageResponse])
def search_messages(
    query:   str             = Query(..., min_length=1),
    limit:   int             = Query(20, gt=0),
    chat_svc: ChatService    = Depends(get_chat_service),
) -> List[ChatMessage]:
    # Всегда работает с «личным» чатом
    chat = chat_svc.get_or_create_chat()
    return chat_svc.search_messages(chat, query=query, limit=limit)


@router.get("/me", response_model=ChatResponse)
def get_my_chat(
    chat_svc: ChatService = Depends(get_chat_service),
) -> Chat:
    """
    Возвращает данные личного чата (создаёт, если ещё нет).
    """
    return chat_svc.get_or_create_chat()
