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

    def _get_localized_welcome_message(self) -> str:
        welcome_texts = {
            'ru': 'Привет! Я твой ассистент по распределению твоего времени. Я могу помочь тебе планировать события, добавлять встречи и напоминания в календарь, а также отвечать на твои вопросы. Чтобы тебе было комфортно, ты также можешь выбрать стиль моего общения с тобой (например, как профессиональный ассистент, дружелюбный приятель или даже личный коуч). Чем могу помочь?',
            'en': 'Hello! I am your personal time management assistant. I can help you plan events, add meetings and reminders to your calendar, and answer your questions. To make you feel comfortable, you can also choose my communication style (for example, as a professional assistant, a friendly companion, or even a personal coach). How can I help you today?',
            'kk': 'Сәлеметсіз бе! Мен сіздің жеке уақытты басқару бойынша көмекшіңізбін. Мен сізге іс-шараларды жоспарлауға, күнтізбеге кездесулер мен ескертулер қосуға, сондай-ақ сұрақтарыңызға жауап беруге көмектесе аламын. Өзіңізді ыңғайлы сезіну үшін, сіз менімен қарым-қатынас стилін таңдай аласыз (мысалы, кәсіби көмекші, достық серік немесе тіпті жеке коуч ретінде). Бүгін қалай көмектесе аламын?',
        }
        # Используем preferred_language пользователя или fallback
        lang_code = self.user.preferred_language[:2] if self.user.preferred_language and len(self.user.preferred_language) >= 2 else 'ru'
        return welcome_texts.get(lang_code, welcome_texts['ru'])
    

    def _base_chat_q(self):
        return self.db.query(Chat).filter(Chat.owner_id == self.user.id)

    def create_chat(self, title: str, welcome_message_content: str = "") -> Chat:
        chat = Chat(title=title, owner_id=self.user.id)
        self.db.add(chat)
        self.db.flush() # Используем flush, чтобы получить id чата до коммита

        welcome_message_content = self._get_localized_welcome_message()
        if welcome_message_content: # Всегда будет true, но на всякий случай
            welcome_message = ChatMessage(
                chat_id=chat.id,
                role="assistant",
                content=welcome_message_content,
                created_at=datetime.utcnow()
            )
            self.db.add(welcome_message)

        try:
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            raise

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
