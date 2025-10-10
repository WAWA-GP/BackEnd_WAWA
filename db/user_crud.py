# db/user_crud.py

from supabase import AsyncClient
from models import user_model
import logging
<<<<<<< HEAD
from typing import Dict, Any, Optional
=======
>>>>>>> origin/master

# --- 사용자 조회 (Username/Email 기준) ---
async def get_user_by_username(db: AsyncClient, username: str):
    """
    'user_account' 테이블에서 이메일을 기준으로 활성 사용자를 안전하게 조회합니다.
    """
    try:
<<<<<<< HEAD
        response = await db.from_("user_account").select("*").eq("email", username).maybe_single().execute()

=======
        # [수정 1] .single()을 .maybe_single()로 변경하여 안정성 확보
        response = await db.from_("user_account").select("*").eq("email", username).maybe_single().execute()

        # maybe_single()은 결과가 없으면 None을 반환하므로, response 자체를 먼저 확인
>>>>>>> origin/master
        if not response or not response.data:
            return None

        user_data = response.data

<<<<<<< HEAD
        if user_data.get('is_active'):
            return user_data
        else:
=======
        # [수정 2] 'is_activate' 오타를 'is_active'로 수정
        if user_data.get('is_active'):
            return user_data
        else:
            # 사용자는 찾았지만 비활성 상태인 경우
>>>>>>> origin/master
            return None

    except Exception as e:
        print(f"사용자 조회 중 오류 발생: {e}")
        return None

# --- 사용자 조회 (ID 기준) ---
<<<<<<< HEAD
async def get_user(db: AsyncClient, user_id: str):  # 👈 int → str로 변경 (UUID인 경우)
    # 👇 실제 컬럼명으로 변경 (예: user_id)
    response = await db.table("user_account").select("*").eq("user_id", user_id).limit(1).single().execute()
    return response.data

# --- 사용자 생성 ---
async def create_user(db: AsyncClient, user_id: str, email: str, name: str, hashed_password: str, is_admin: bool):
    try:
        logging.info(f"=== create_user 함수 시작 ===")

        user_data = {
            "user_id": user_id,
            "email": email,
            "name": name,
            "password": hashed_password,
            "is_admin": is_admin
        }

        logging.info(f"삽입할 데이터: {user_data}")

        # ⚠️ 여기를 수정! insert → upsert
        response = await db.table("user_account").upsert(user_data).execute()

        logging.info(f"DB 응답: {response}")

        return response.data[0] if response.data else None

    except Exception as e:
        logging.error(f"=== create_user 오류 ===")
        logging.error(f"오류: {str(e)}")
        import traceback
        logging.error(f"스택 트레이스:\n{traceback.format_exc()}")
        raise

# --- 사용자 수정 ---
async def update_user(db: AsyncClient, user_id: str, update_data: dict):  # 👈 int → str로 변경
    # 👇 실제 컬럼명으로 변경 (예: user_id)
    response = await db.table("user_account").update(update_data).eq("user_id", user_id).execute()
    return response.data[0] if response.data else None

async def update_password(db: AsyncClient, user_id: str, hashed_password: str):
    """
    사용자의 해싱된 비밀번호를 데이터베이스에 직접 업데이트합니다.
    """
    response = await db.table("user_account").update({"password": hashed_password}).eq("user_id", user_id).execute()
    return response.data[0] if response.data else None

# 사용자 삭제 (회원 탈퇴) 함수
async def delete_user(db: AsyncClient, user_id: str) -> bool:
    """
    user_id를 기준으로 'user_account' 테이블에서 사용자를 삭제합니다.
    """
    try:
        response = await db.from_("user_account").delete().eq("user_id", user_id).execute()
        # 삭제가 성공적으로 이루어지면 response.data에 해당 데이터가 포함됩니다.
        if response.data:
            return True
        return False
    except Exception as e:
        logging.error(f"사용자 삭제 중 오류 발생: {e}")
        return False

async def get_notification_settings(db: AsyncClient, user_id: str) -> Optional[Dict[str, Any]]:
    """user_account 테이블에서 사용자의 알림 설정을 조회합니다."""
    response = await db.table("user_account").select("notification_settings").eq("user_id", user_id).single().execute()
    return response.data.get("notification_settings") if response.data else None

async def update_notification_settings(db: AsyncClient, user_id: str, settings: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """user_account 테이블에서 사용자의 알림 설정을 업데이트합니다."""
    response = await db.table("user_account").update({"notification_settings": settings}).eq("user_id", user_id).execute()
    if response.data:
        return response.data[0].get("notification_settings")
    return None

async def update_user_settings(db: AsyncClient, user_id: str, settings: Dict) -> Optional[Dict]:
    """사용자 ID를 기준으로 특정 설정 값을 업데이트합니다."""
    try:
        # 1. 먼저 데이터를 업데이트합니다. (select 없이)
        update_response = await db.table("user_account").update(settings).eq("user_id", user_id).execute()

        # 업데이트된 행이 있는지 확인 (선택 사항이지만 더 안전함)
        if not update_response.data:
            print("업데이트할 사용자를 찾지 못했습니다.")
            return None

        # 2. 업데이트가 성공하면, 별도의 쿼리로 수정된 사용자 정보를 다시 조회하여 반환합니다.
        select_response = await db.table("user_account").select("*").eq("user_id", user_id).single().execute()

        return select_response.data

    except Exception as e:
        print(f"사용자 설정 업데이트 중 오류 발생: {e}")
        return None
=======
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
>>>>>>> origin/master
