import os
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import Optional, Dict, Any

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def get_user_data_from_supabase(user_id: str) -> Optional[Dict[str, Any]]:
    try:
        response = supabase.table('users').select("*").eq('user_id', user_id).single().execute()
        return response.data
    except Exception as e:
        print(f"사용자 데이터를 가져오는 중 오류 발생 {user_id}: {e}")
        return None