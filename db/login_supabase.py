import os
from supabase import create_async_client, AsyncClient
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

# 👇 [수정] get_supabase_client 함수를 비동기 클라이언트를 생성하고 반환하도록 변경합니다.
async def get_supabase_client() -> AsyncClient:
    supabase: AsyncClient = await create_async_client(url, key)
    return supabase
