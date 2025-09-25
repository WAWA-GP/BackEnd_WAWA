# '사용자 프로필' 관련 API 엔드포인트를 정의하는 파일입니다.
from fastapi import APIRouter, Depends, HTTPException
from supabase import AsyncClient # 👈 Session 대신 AsyncClient를 import
from core.database import get_db
from core.dependencies import get_current_user
from models import user_model
from services import user_service

router = APIRouter(prefix="/user")

# --- 프로필 조회 API ---
@router.get("/profile", response_model=user_model.UserResponse)
async def get_user_profile(
        current_user: dict = Depends(get_current_user)
):
    return current_user

# --- 프로필 수정 API ---
@router.put("/profile", response_model=user_model.UserResponse)
async def update_user_profile(
        user_update: user_model.UserUpdate,
        db: AsyncClient = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    # current_user는 dict이므로 'id' 키로 접근
    updated_user = await user_service.update_user(db=db, user_id=current_user['id'], user_update=user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user
