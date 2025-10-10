# '사용자 프로필' 관련 API 엔드포인트를 정의하는 파일입니다.
<<<<<<< HEAD
from fastapi import APIRouter, Depends, HTTPException, status
from supabase import AsyncClient
from core.database import get_db
from core.dependencies import get_current_user
from db import user_crud
from models import user_model
from models.login_model import UserProfileResponse
from services import user_service
import logging
from models.user_model import UserSettingsRequest
from db.user_crud import update_user_settings

# prefix를 제거하거나 빈 문자열로 설정
router = APIRouter()  # 👈 prefix="/user" 제거
=======
from fastapi import APIRouter, Depends, HTTPException
from supabase import AsyncClient # 👈 Session 대신 AsyncClient를 import
from core.database import get_db
from core.dependencies import get_current_user
from models import user_model
from services import user_service

router = APIRouter(prefix="/user")
>>>>>>> origin/master

# --- 프로필 조회 API ---
@router.get("/profile", response_model=user_model.UserResponse)
async def get_user_profile(
<<<<<<< HEAD
        db: AsyncClient = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    """
    데이터베이스에서 사용자의 최신 프로필 정보를 조회하여 반환합니다.
    """
    user_id = current_user.get('id')
    if not user_id:
        raise HTTPException(status_code=401, detail="인증 정보를 찾을 수 없습니다.")

    # user_crud를 사용하여 DB에서 최신 사용자 정보를 가져옵니다.
    user_data = await user_crud.get_user(db, user_id)

    if not user_data:
        raise HTTPException(status_code=404, detail="사용자 정보를 찾을 수 없습니다.")

    # UserResponse 모델에 맞게 데이터를 반환합니다.
    # user_data에 beginner_mode가 포함되어 있으므로 정상적으로 전달됩니다.
    return user_data
=======
        current_user: dict = Depends(get_current_user)
):
    return current_user
>>>>>>> origin/master

# --- 프로필 수정 API ---
@router.put("/profile", response_model=user_model.UserResponse)
async def update_user_profile(
        user_update: user_model.UserUpdate,
        db: AsyncClient = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
<<<<<<< HEAD
=======
    # current_user는 dict이므로 'id' 키로 접근
>>>>>>> origin/master
    updated_user = await user_service.update_user(db=db, user_id=current_user['id'], user_update=user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user
<<<<<<< HEAD

@router.patch("/update-name")
async def update_user_name(
        name_update: user_model.UserNameUpdate,
        db: AsyncClient = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    """사용자 이름만 수정"""
    logging.info(f"이름 수정 요청 - current_user: {current_user}, new_name: {name_update.name}")

    # 👇 current_user에서 실제로 사용되는 키 확인
    user_id = current_user.get('user_id') or current_user.get('id') or current_user.get('uuid')

    if not user_id:
        logging.error(f"User ID를 찾을 수 없음. current_user 내용: {current_user}")
        raise HTTPException(status_code=400, detail="User ID not found")

    try:
        update_data = {"name": name_update.name}
        updated_user = await user_service.update_user_name(db=db, user_id=user_id, update_data=update_data)

        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")

        logging.info(f"이름 수정 성공 - user_id: {user_id}")
        return updated_user
    except Exception as e:
        logging.error(f"이름 수정 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 비밀번호 변경 엔드포인트
@router.patch("/update-password")
async def update_password_endpoint(
        pass_update: user_model.PasswordUpdate,
        db: AsyncClient = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get('user_id') or current_user.get('id')
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID not found in token")

    await user_service.update_password(db=db, user_id=user_id, pass_update=pass_update)

    # 204 대신 200과 메시지 반환
    return {
        "success": True,
        "message": "비밀번호가 정상적으로 변경되었습니다"
    }


# 회원 탈퇴 엔드포인트
@router.post("/delete-account")
async def delete_account_endpoint( # 함수 이름 변경 (중복 방지)
        account_delete: user_model.AccountDelete,
        db: AsyncClient = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get('user_id') or current_user.get('id')
    logging.info(f"회원 탈퇴 요청 - user_id: {user_id}")
    logging.info(f"current_user 전체: {current_user}")
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID not found in token")

    # ✅ user_service 호출 시 `db` 객체를 전달합니다.
    return await user_service.delete_account(db=db, user_id=user_id, account_delete=account_delete)

@router.patch("/settings", response_model=UserProfileResponse)
async def update_settings_endpoint(
        settings: UserSettingsRequest,
        current_user: dict = Depends(get_current_user),
        db: AsyncClient = Depends(get_db)
):
    """사용자의 설정을 업데이트합니다 (예: 초보자 모드)."""
    user_id = current_user.get('user_id')
    if not user_id:
        raise HTTPException(status_code=401, detail="인증되지 않은 사용자입니다.")

    # settings.model_dump(exclude_unset=True)는 None이 아닌 값만 딕셔너리로 만듭니다.
    updated_profile = await update_user_settings(db, user_id, settings.model_dump(exclude_unset=True))

    if not updated_profile:
        raise HTTPException(status_code=500, detail="설정 업데이트에 실패했습니다.")

    return updated_profile
=======
>>>>>>> origin/master
