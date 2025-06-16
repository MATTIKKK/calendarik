from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.models import Chat, ChatMessage, User

class ChatService:
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user

    def create_chat(self, title: str) -> Chat:
        """Create a new chat."""
        chat = Chat(
            title=title,
            owner_id=self.user.id
        )
        self.db.add(chat)
        self.db.commit()
        self.db.refresh(chat)
        return chat

    def get_chat(self, chat_id: int) -> Optional[Chat]:
        """Get a chat by ID."""
        return self.db.query(Chat).filter(
            Chat.id == chat_id,
            Chat.owner_id == self.user.id
        ).first()

    def get_user_chats(self, limit: int = 50, offset: int = 0) -> List[Chat]:
        """Get all user's chats with pagination."""
        return self.db.query(Chat).filter(
            Chat.owner_id == self.user.id
        ).order_by(Chat.updated_at.desc()).offset(offset).limit(limit).all()

    def add_message(self, chat_id: int, content: str, role: str) -> ChatMessage:
        """Add a new message to a chat."""
        message = ChatMessage(
            content=content,
            role=role,
            chat_id=chat_id
        )
        self.db.add(message)
        
        # Update chat's updated_at timestamp
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
        before_id: Optional[int] = None
    ) -> List[ChatMessage]:
        """Get chat messages with pagination."""
        query = self.db.query(ChatMessage).filter(
            ChatMessage.chat_id == chat_id
        )
        
        if before_id:
            query = query.filter(ChatMessage.id < before_id)
            
        return query.order_by(ChatMessage.created_at.desc()).limit(limit).all()

    def update_chat_title(self, chat_id: int, title: str) -> Optional[Chat]:
        """Update chat title."""
        chat = self.get_chat(chat_id)
        if chat:
            chat.title = title
            self.db.commit()
            self.db.refresh(chat)
        return chat

    def delete_chat(self, chat_id: int) -> bool:
        """Delete a chat and all its messages."""
        chat = self.get_chat(chat_id)
        if chat:
            self.db.delete(chat)
            self.db.commit()
            return True
        return False

    def get_latest_messages(self, chat_id: int, limit: int = 10) -> List[ChatMessage]:
        """Get the most recent messages from a chat."""
        return self.db.query(ChatMessage).filter(
            ChatMessage.chat_id == chat_id
        ).order_by(ChatMessage.created_at.desc()).limit(limit).all()

    def search_messages(self, query: str, limit: int = 10) -> List[ChatMessage]:
        """Search through user's messages."""
        return self.db.query(ChatMessage).join(Chat).filter(
            Chat.owner_id == self.user.id,
            ChatMessage.content.ilike(f"%{query}%")
        ).order_by(ChatMessage.created_at.desc()).limit(limit).all() 