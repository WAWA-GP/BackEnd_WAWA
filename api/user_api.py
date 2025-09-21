# '사용자 프로필' 관련 API 엔드포인트를 정의하는 파일입니다.
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from core.dependencies import get_current_user
from models import user_model
from services import user_service
from database import models as db_models

router = APIRouter(prefix="/user")

# --- 프로필 조회 API ---
@router.get("/profile", response_model=user_model.UserResponse)
def get_user_profile(
        current_user: db_models.User = Depends(get_current_user)
):
    return current_user

# --- 프로필 수정 API ---
@router.put("/profile", response_model=user_model.UserResponse)
def update_user_profile(
        user_update: user_model.UserUpdate,
        db: Session = Depends(get_db),
        current_user: db_models.User = Depends(get_current_user)
):

    updated_user = user_service.update_user(db=db, user_id=current_user.id, user_update=user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user