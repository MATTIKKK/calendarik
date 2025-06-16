from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class User(BaseModel):
    """User model for authentication and profile information."""
    __tablename__ = "users"

    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    timezone = Column(String, default="UTC")
    gender = Column(String, default="other")
    chat_personality = Column(String, default="assistant")
    is_active = Column(Boolean, default=True)
    
     # 1-к-1: ссылка на единственный чат
    main_chat = relationship(
        "Chat",
        uselist=False,          # «возвращай один объект, а не список»
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    # остальные связи
    events = relationship("CalendarEvent", back_populates="owner")