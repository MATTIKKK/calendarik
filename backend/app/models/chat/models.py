from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Chat(BaseModel):
    __tablename__ = "chats"

    title     = Column(String, nullable=False, default="Bro")
    owner_id  = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,            # ← гарантирует «у пользователя только один чат»
        nullable=False,
    )

    # соседние связи
    owner    = relationship("User", back_populates="main_chat")
    messages = relationship(
        "ChatMessage",
        back_populates="chat",
        cascade="all, delete-orphan",
    )


class ChatMessage(BaseModel):
    __tablename__ = "chat_messages"

    content = Column(Text, nullable=False)
    role    = Column(String, nullable=False)  # 'user' | 'assistant'
    chat_id = Column(Integer, ForeignKey("chats.id", ondelete="CASCADE"))

    chat = relationship("Chat", back_populates="messages")
