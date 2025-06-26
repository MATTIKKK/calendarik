from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.user import get_current_user
from app.models import User
from app.services.chat_service import ChatService



def get_chat_service(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatService:
    return ChatService(db, current_user)