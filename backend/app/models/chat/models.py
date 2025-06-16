from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Chat(BaseModel):
    """Chat model for storing conversations."""
    __tablename__ = "chats"

    title = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    owner = relationship("User", back_populates="chats")
    messages = relationship("ChatMessage", back_populates="chat", cascade="all, delete-orphan")

class ChatMessage(BaseModel):
    """Chat message model for storing individual messages."""
    __tablename__ = "chat_messages"

    content = Column(Text, nullable=False)
    role = Column(String, nullable=False)  # 'user' или 'assistant'
    chat_id = Column(Integer, ForeignKey("chats.id"))
    
    # Relationships
    chat = relationship("Chat", back_populates="messages") 