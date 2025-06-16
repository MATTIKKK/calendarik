# app/services/chat_service.py
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Chat, ChatMessage, User


class ChatService:
    """Инкапсулирует всю работу с чатами конкретного пользователя."""

    def __init__(self, db: Session, user: User) -> None:
        self.db: Session = db
        self.user: User = user

    # --------------------------------------------------------------------- #
    # Low-level helpers
    # --------------------------------------------------------------------- #
    def _base_chat_q(self):
        return self.db.query(Chat).filter(Chat.owner_id == self.user.id)

    def get_or_404(self, chat_id: int) -> Chat:
        """Вернуть чат или бросить 404, если он не принадлежит пользователю."""
        chat = self.get_chat(chat_id)
        if not chat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Chat not found")
        return chat

    # --------------------------------------------------------------------- #
    # Chats
    # --------------------------------------------------------------------- #
    def create_chat(self, title: str) -> Chat:
        """Создать чат и сразу вернуть ORM-объект."""
        chat = Chat(title=title, owner_id=self.user.id)
        self.db.add(chat)
        self.db.flush()      # chat.id доступен до commit
        self.db.commit()
        self.db.refresh(chat)
        return chat

    def get_chat(self, chat_id: int) -> Optional[Chat]:
        """Вернуть чат без исключения (или None)."""
        return (
            self._base_chat_q()
            .filter(Chat.id == chat_id)
            .first()
        )

    def get_or_create_by_owner(self, title: str = "Personal chat") -> Chat:
        """Найти личный чат пользователя или создать новый."""
        chat = self._base_chat_q().first()
        return chat or self.create_chat(title)

    def get_user_chats(self, limit: int = 50, offset: int = 0) -> List[Chat]:
        """Вернуть список чатов пользователя (с пагинацией)."""
        return (
            self._base_chat_q()
            .order_by(Chat.updated_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def update_chat_title(self, chat_id: int, title: str) -> Optional[Chat]:
        chat = self.get_chat(chat_id)
        if chat:
            chat.title = title
            self.db.commit()
            self.db.refresh(chat)
        return chat

    def delete_chat(self, chat_id: int) -> bool:
        chat = self.get_chat(chat_id)
        if chat:
            self.db.delete(chat)
            self.db.commit()
            return True
        return False

    # --------------------------------------------------------------------- #
    # Messages
    # --------------------------------------------------------------------- #
    def add_message(self, chat_id: int, role: str, content: str) -> ChatMessage:
        """Сохранить сообщение и обновить timestamp чата."""
        message = ChatMessage(chat_id=chat_id, role=role, content=content)
        self.db.add(message)

        chat = self.get_chat(chat_id)
        if chat:
            chat.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(message)
        return message

    def get_chat_messages(
        self,
        chat_id: int,
        limit: int = 50,
        before_id: Optional[int] = None,
    ):
        """Запрос (!) сообщений чата.  
        Возвращается `Query`, чтобы можно было навесить сортировку/фильтр перед `.all()`"""
        q = self.db.query(ChatMessage).filter(ChatMessage.chat_id == chat_id)

        if before_id:
            q = q.filter(ChatMessage.id < before_id)

        return q.order_by(ChatMessage.created_at.asc())  # ⬆️ по возрастанию

    def get_latest_messages(self, chat_id: int, limit: int = 10) -> List[ChatMessage]:
        return (
            self.db.query(ChatMessage)
            .filter(ChatMessage.chat_id == chat_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
            .all()
        )

    def search_messages(self, query: str, limit: int = 10) -> List[ChatMessage]:
        """Полнотекстовый поиск по сообщениям пользователя."""
        return (
            self.db.query(ChatMessage)
            .join(Chat, Chat.id == ChatMessage.chat_id)
            .filter(
                Chat.owner_id == self.user.id,
                ChatMessage.content.ilike(f"%{query}%"),
            )
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
            .all()
        )
