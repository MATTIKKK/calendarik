from pydantic import BaseModel, EmailStr
from typing import Optional

class RegisterData(BaseModel):
    email: str
    password: str
    full_name: str
    timezone: str
    gender: str
    preferred_language: str = "ru"
    chat_personality: str = "assistant"

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    gender: Optional[str] = None
    timezone: Optional[str] = None
    chat_personality: Optional[str] = "assistant"
    preferred_language: Optional[str] = "ru"
class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: str
    exp: int
    type: str

class RefreshToken(BaseModel):
    refresh_token: str 