# db/user_crud.py

from supabase import AsyncClient
from models import user_model
import logging

# --- 사용자 조회 (Username/Email 기준) ---
async def get_user_by_username(db: AsyncClient, username: str):
    """
    'user_account' 테이블에서 이메일을 기준으로 활성 사용자를 안전하게 조회합니다.
    """
    try:
        # [수정 1] .single()을 .maybe_single()로 변경하여 안정성 확보
        response = await db.from_("user_account").select("*").eq("email", username).maybe_single().execute()

        # maybe_single()은 결과가 없으면 None을 반환하므로, response 자체를 먼저 확인
        if not response or not response.data:
            return None

        user_data = response.data

        # [수정 2] 'is_activate' 오타를 'is_active'로 수정
        if user_data.get('is_active'):
            return user_data
        else:
            # 사용자는 찾았지만 비활성 상태인 경우
            return None

    except Exception as e:
        print(f"사용자 조회 중 오류 발생: {e}")
        return None

# --- 사용자 조회 (ID 기준) ---
async def get_user(db: AsyncClient, user_id: int):
    # [수정] 'users' 대신 'user_account' 테이블을 조회합니다.
    response = await db.table("user_account").select("*").eq("id", user_id).limit(1).single().execute()
    return response.data

# --- 사용자 생성 ---
async def create_user(db: AsyncClient, user: user_model.UserCreate, hashed_password: str):
    # 'username' 필드가 Supabase 테이블에 'email'로 저장될 수 있으니 확인이 필요하지만,
    # 우선 user_account 테이블을 바라보도록 수정합니다.
    user_data = {
        "email": user.username, # Supabase auth는 email을 사용하므로 통일
        "password": hashed_password,
        "is_admin": user.is_admin
        # user_account 테이블에 맞는 다른 필드들을 여기에 추가해야 할 수 있습니다. (예: name)
    }
    response = await db.table("user_account").insert(user_data).execute()
    return response.data[0] if response.data else None

# --- 사용자 수정 ---
async def update_user(db: AsyncClient, user_id: int, update_data: dict):
    # [수정] 'users' 대신 'user_account' 테이블을 수정합니다.
    response = await db.table("user_account").update(update_data).eq("id", user_id).execute()
    return response.data[0] if response.data else None
