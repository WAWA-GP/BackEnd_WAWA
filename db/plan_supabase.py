import os
from typing import Optional, Dict, Any

from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def save_learning_plan_to_db(plan_data: dict):
    try:
        data, count = supabase.table('learning_plans').insert(plan_data).execute()

        return data[1]
    except Exception as e:
        print(f"학습 계획 저장 중 오류 발생: {e}")
        raise e

def get_latest_plan_by_user(user_id: str) -> Optional[Dict[str, Any]]:
    """
    'learning_plans' 테이블에서 특정 사용자의 가장 최근 계획 하나를 조회합니다.
    """
    try:
        response = supabase.table("learning_plans").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(1).maybe_single().execute()
        return response.data
    except Exception as e:
        print(f"최신 학습 계획 조회 중 오류 발생: {e}")
        return None
