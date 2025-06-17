from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.services.ai_service import AIService   # импортируем класс
ai_service = AIService()    

from app.core.database import get_db
from app.routes.auth import get_current_user
from app.models import User, Chat, ChatMessage
from app.schemas.chat import AIChatRequest, AIChatResponse, ChatMessageResponse, ChatResponse
from app.services.calendar_service import CalendarService

router = APIRouter(prefix="/chat", tags=["chat"])

def get_or_create_chat(db: Session, user: User) -> Chat:
    chat = (
        db.query(Chat)
        .filter(Chat.owner_id == user.id)
        .order_by(Chat.created_at.asc())
        .first()
    )
    if chat:
        return chat

    chat = Chat(title="Bro", owner_id=user.id, created_at=datetime.utcnow())
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat


@router.post("/message", response_model=AIChatResponse)
async def send_message(
    req: AIChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chat = get_or_create_chat(db, current_user)

    # сохраняем сообщение пользователя
    user_msg = ChatMessage(content=req.message, role="user", chat_id=chat.id)
    db.add(user_msg)

    # вызываем AI-сервис
    ai_reply = await ai_service.analyze_message(
        message=req.message,
        personality=req.personality or current_user.chat_personality,
        user_gender=current_user.gender,
        language=req.language or "Russian",
        calendar_service=CalendarService(db, current_user),
    )
    
    # сохраняем ответ ассистента
    print("ai_reply", ai_reply)
    assistant_msg = ChatMessage(
        content=ai_reply["message"], role="assistant", chat_id=chat.id
    )
    db.add(assistant_msg)
    db.commit()

    return AIChatResponse(message=ai_reply["message"], chat_id=chat.id)


@router.get("/{chat_id}/messages", response_model=List[ChatMessageResponse])
async def get_chat_messages(
    chat_id: int,
    limit: int = 50,
    before_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # проверяем, что чат принадлежит юзеру
    exists = (
        db.query(Chat)
        .filter(Chat.id == chat_id, Chat.owner_id == current_user.id)
        .first()
    )
    if not exists:
        raise HTTPException(status_code=404, detail="Chat not found")

    query = (
        db.query(ChatMessage)
        .filter(ChatMessage.chat_id == chat_id)
        .order_by(ChatMessage.created_at.desc())
    )
    if before_id:
        query = query.filter(ChatMessage.id < before_id)

    return query.limit(limit).all()



@router.get("/search", response_model=List[ChatMessageResponse])
async def search_messages(
    query: str,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chat = get_or_create_chat(db, current_user)

    return (
        db.query(ChatMessage)
        .filter(
            ChatMessage.chat_id == chat.id,
            ChatMessage.content.ilike(f"%{query}%"),
        )
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
        .all()
    )

@router.get("/me", response_model=ChatResponse)      # ← новый энд-поинт
async def get_my_chat(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Вернуть личный чат пользователя (создать, если ещё не существует).
    """
    chat = get_or_create_chat(db, current_user)
    return chat