from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class ChatMessageBase(BaseModel):
    content: str
    role: str

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageResponse(ChatMessageBase):
    id: int
    chat_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ChatBase(BaseModel):
    title: str

class ChatCreate(ChatBase):
    pass

class ChatUpdate(ChatBase):
    title: Optional[str] = None

class ChatResponse(ChatBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessageResponse]

    class Config:
        from_attributes = True

class ChatList(BaseModel):
    chats: List[ChatResponse]

class AIChatRequest(BaseModel):
    message: str
    chat_id: Optional[int] = None  # None для нового чата

class AIChatResponse(BaseModel):
    message: str
    chat_id: int
    title: Optional[str] = None  # Для нового чата 