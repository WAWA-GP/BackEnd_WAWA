import os
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import Optional, Dict, Any

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def get_user_data_from_supabase(user_id: str) -> Optional[Dict[str, Any]]:
    """user_account 테이블에서 사용자 데이터를 가져옵니다."""
    try:
        response = supabase.table('user_account').select("*").eq('user_id', user_id).single().execute()
        return response.data
    except Exception as e:
        print(f"사용자 데이터를 가져오는 중 오류 발생 {user_id}: {e}")
        return None

def update_user_learning_goal(user_id: str, goal_data: Dict[str, Any]) -> None:
    """user_account 테이블에서 user_id가 일치하는 사용자의 learning_goals를 업데이트합니다."""
    try:
        supabase.table('user_account').update({'learning_goals': goal_data}).eq('user_id', user_id).execute()
        print(f"사용자 {user_id}의 학습 목표 업데이트 성공")
    except Exception as e:
        print(f"학습 목표 업데이트 중 오류 발생: {e}")
        raise e
