# '사용자 프로필' 관련 비즈니스 로직을 처리하는 파일입니다.
from supabase import AsyncClient
from models import user_model
from db import user_crud
from core import security

# --- 사용자 정보 수정 서비스 ---
async def update_user(db: AsyncClient, user_id: int, user_update: user_model.UserUpdate):
    update_data = user_update.dict(exclude_unset=True)

    if "password" in update_data and update_data["password"]:
        hashed_password = security.hash_password(update_data["password"])
        update_data["password"] = hashed_password

    return await user_crud.update_user(db=db, user_id=user_id, update_data=update_data)
