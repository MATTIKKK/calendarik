# app/services/chat_service.py
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models import Chat, ChatMessage, User


class ChatService:
    def __init__(self, db: Session, user: User) -> None:
        self.db: Session = db
        self.user: User = user

    def _base_chat_q(self):
        return self.db.query(Chat).filter(Chat.owner_id == self.user.id)

    def create_chat(self, title: str) -> Chat:
        chat = Chat(title=title, owner_id=self.user.id)
        self.db.add(chat)
        self.db.commit()
        self.db.refresh(chat)
        return chat

    def get_or_create_chat(self, title: str = "Personal chat") -> Chat:
        chat = self._base_chat_q().first()
        return chat or self.create_chat(title)

    def add_message(self, chat_id: int, role: str, content: str) -> ChatMessage:
        chat = (
            self._base_chat_q()
            .filter(Chat.id == chat_id)
            .first()
        )

        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        message = ChatMessage(
            chat_id=chat_id,
            role=role,
            content=content,
        )
        self.db.add(message)

        chat.updated_at = datetime.utcnow()

        try:
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            raise

        self.db.refresh(message)
        return message

    def get_chat_messages(
        self,
        chat_id: int,
        limit: int = 50,
        before_id: Optional[int] = None,
    ):
        q = (
            self.db.query(ChatMessage)
            .join(Chat, Chat.id == ChatMessage.chat_id)
            .filter(
                Chat.owner_id == self.user.id,
                ChatMessage.chat_id == chat_id,
            )
        )

        if before_id is not None:
            q = q.filter(ChatMessage.id < before_id)

        messages = (
            q.order_by(ChatMessage.created_at.desc())
            .limit(limit)
            .all()
        )

        return messages
