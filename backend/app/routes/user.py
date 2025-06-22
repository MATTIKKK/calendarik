from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.user import get_current_user
from app.models import User
from app.schemas.auth import UserResponse
from app.schemas.user import UpdatePersonalityRequest

router = APIRouter()

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me/personality", response_model=UserResponse)
async def update_personality(
    request: UpdatePersonalityRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    valid_personalities = ["assistant", "coach", "friend", "girlfriend", "boyfriend"]
    if request.personality not in valid_personalities:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid personality. Must be one of: {', '.join(valid_personalities)}"
        )

    current_user.chat_personality = request.personality
    db.commit()
    db.refresh(current_user)
    return current_user
