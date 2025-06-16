from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.routes.auth import get_current_user
from app.models import User, Chat, ChatMessage
from app.schemas.chat import (
    ChatCreate,
    ChatResponse,
    ChatList,
    ChatUpdate,
    AIChatRequest,
    AIChatResponse,
    ChatMessageCreate
)
from app.services.chat_service import ChatService

router = APIRouter()

class ChatResponse(BaseModel):
    id: int
    title: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    id: int
    content: str
    role: str
    created_at: str
    chat_id: int

    class Config:
        from_attributes = True

class ChatListResponse(BaseModel):
    chats: List[ChatResponse]
    total: int

class UpdateChatRequest(BaseModel):
    title: str

@router.post("/", response_model=ChatResponse)
async def create_chat(
    chat: ChatCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_chat = Chat(
        title=chat.title,
        owner_id=current_user.id
    )
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat

@router.get("/", response_model=ChatListResponse)
async def get_chats(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    chat_service = ChatService(db, current_user)
    chats = chat_service.get_user_chats(limit, offset)
    total = db.query(User).filter(User.owner_id == current_user.id).count()
    return {"chats": chats, "total": total}

@router.get("/{chat_id}", response_model=ChatResponse)
async def get_chat(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    chat = db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.owner_id == current_user.id
    ).first()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    return chat

@router.post("/message", response_model=AIChatResponse)
async def send_message(
    request: AIChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Если chat_id не указан, создаем новый чат
    if not request.chat_id:
        chat = Chat(
            title=request.message[:50] + "...",  # Используем начало сообщения как заголовок
            owner_id=current_user.id
        )
        db.add(chat)
        db.commit()
        db.refresh(chat)
    else:
        chat = db.query(Chat).filter(
            Chat.id == request.chat_id,
            Chat.owner_id == current_user.id
        ).first()
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found"
            )

    # Сохраняем сообщение пользователя
    user_message = ChatMessage(
        content=request.message,
        role="user",
        chat_id=chat.id
    )
    db.add(user_message)

    # TODO: Здесь будет интеграция с AI
    ai_response = "Это тестовый ответ от AI. Здесь будет настоящий ответ после интеграции."

    # Сохраняем ответ AI
    ai_message = ChatMessage(
        content=ai_response,
        role="assistant",
        chat_id=chat.id
    )
    db.add(ai_message)
    db.commit()

    return {
        "message": ai_response,
        "chat_id": chat.id,
        "title": chat.title if request.chat_id is None else None
    }

@router.get("/{chat_id}/messages", response_model=List[MessageResponse])
async def get_chat_messages(
    chat_id: int,
    limit: int = 50,
    before_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    chat_service = ChatService(db, current_user)
    if not chat_service.get_chat(chat_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    return chat_service.get_chat_messages(chat_id, limit, before_id)

@router.put("/{chat_id}", response_model=ChatResponse)
async def update_chat(
    chat_id: int,
    request: UpdateChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    chat_service = ChatService(db, current_user)
    chat = chat_service.update_chat_title(chat_id, request.title)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    return chat

@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    chat_service = ChatService(db, current_user)
    if not chat_service.delete_chat(chat_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )

@router.get("/search", response_model=List[MessageResponse])
async def search_messages(
    query: str,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    chat_service = ChatService(db, current_user)
    return chat_service.search_messages(query, limit) 