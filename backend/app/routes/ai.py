from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.user import get_current_user
from app.models import User
from app.services.ai_service import AIService
from app.schemas.ai import AIMessageRequest, AIMessageResponse

router = APIRouter()
ai_service = AIService()

@router.post("/analyze", response_model=AIMessageResponse)
async def analyze_message(
    request: AIMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        result = await ai_service.handle_analysis(request, db, current_user)
        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"[AI Route] Error: {e}")
        raise HTTPException(500, "Failed to process message")