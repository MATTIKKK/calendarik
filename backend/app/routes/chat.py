from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

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

router = APIRouter()

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

@router.get("/", response_model=ChatList)
async def get_chats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    chats = db.query(Chat).filter(Chat.owner_id == current_user.id).all()
    return {"chats": chats}

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

@router.put("/{chat_id}", response_model=ChatResponse)
async def update_chat(
    chat_id: int,
    chat_update: ChatUpdate,
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
    
    for field, value in chat_update.dict(exclude_unset=True).items():
        setattr(chat, field, value)
    
    db.commit()
    db.refresh(chat)
    return chat

@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(
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
    
    db.delete(chat)
    db.commit()
    return None 