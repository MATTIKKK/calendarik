from pydantic import BaseModel, validator
from typing import Optional

class AIMessageRequest(BaseModel):
    message: str
    chat_id: Optional[int] = None
    # personality: Optional[str] = None
    # language: Optional[str] = None

    # @validator("personality")
    # def validate_personality(cls, v):
    #     if v is None:
    #         return v
    #     valid_personalities = ["assistant", "coach", "friend", "girlfriend", "boyfriend"]
    #     if v not in valid_personalities:
    #         raise ValueError(f"Invalid personality. Must be one of: {', '.join(valid_personalities)}")
    #     return v

    @validator("message")
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()

class AIMessageResponse(BaseModel):
    message: str
    chat_id: int
    calendar_event_id: Optional[int] = None
