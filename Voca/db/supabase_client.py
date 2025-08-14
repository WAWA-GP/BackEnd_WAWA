import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")


try:
    supabase: Client = create_client(url, key)
    print("Supabase Client 초기화 완료")
except Exception as e:
    print(f"Supabase Client 초기화 실패")
    supabase = None

def search_word_in_dictionary(word: str) -> dict | None:
    if not supabase:
        return None
    try:
        response = supabase.table('dictionary').select('*').eq('word', word.lower()).single().execute()
        return response.data
    except Exception as e:
        print(f"LOG: 단어 검색 실패")
        return None

def get_user_voca_from_db(user_id: str) -> list:
    if not supabase:
        return []
    try:
        response = supabase.table('profiles').select('voca_data').eq('id', user_id).single().execute()
        return response.data.get('voca_data', []) if response.data and response.data.get('voca_data') else []
    except Exception as e:
        print(f"LOG: 단어장 조회 실패")
        return []

def update_user_voca_in_db(user_id: str, new_voca_data: list) -> bool:
    if not supabase:
        return False
    try:
        supabase.table('profiles').update({'voca_data': new_voca_data}).eq('id', user_id).execute()
        return True
    except Exception as e:
        print(f"LOG: 단어장 업데이트 실패")
        return False