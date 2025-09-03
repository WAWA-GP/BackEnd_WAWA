import os
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
        print(f"Supabase 저장 중 오류 발생: {e}")
        raise e

