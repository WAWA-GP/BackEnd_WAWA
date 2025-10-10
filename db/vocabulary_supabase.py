# db/vocabulary_supabase.py

from supabase import AsyncClient
from models import vocabulary_model
from typing import List, Optional

# --- Wordbook ---
async def create_wordbook(db: AsyncClient, name: str, user_id: str):
    response = await db.table("wordbooks").insert({"name": name, "user_id": user_id}).execute()
    return response.data[0] if response.data else None

async def get_wordbooks_by_user(db: AsyncClient, user_id: str) -> List[dict]:
    # RPC를 호출하여 단어 개수와 함께 단어장 목록을 가져옵니다.
    response = await db.rpc('get_user_wordbooks_with_count', {'p_user_id': user_id}).execute()
    return response.data

async def get_wordbook_with_words(db: AsyncClient, wordbook_id: int, user_id: str):
    # 단어장 정보와 단어 목록을 한 번에 조회합니다.
    response = await db.table("wordbooks").select("*, user_words(*)").eq("id", wordbook_id).eq("user_id", user_id).single().execute()
    return response.data

# --- UserWord ---
async def add_word_to_wordbook(db: AsyncClient, word: vocabulary_model.UserWordCreate, wordbook_id: int):
    word_data = word.model_dump()
    word_data['wordbook_id'] = wordbook_id
    response = await db.table("user_words").insert(word_data).execute()
    return response.data[0] if response.data else None

async def update_word_details(db: AsyncClient, word_id: int, word_data: dict):
    response = await db.table("user_words").update(word_data).eq("id", word_id).execute()
    return response.data[0] if response.data else None

async def update_word_status(db: AsyncClient, word_id: int, is_memorized: bool):
    response = await db.table("user_words").update({"is_memorized": is_memorized}).eq("id", word_id).execute()
    return response.data[0] if response.data else None

async def delete_word(db: AsyncClient, word_id: int):
    response = await db.table("user_words").delete().eq("id", word_id).execute()
    return response.data

async def add_words_to_wordbook_batch(db: AsyncClient, words: List[dict]):
    # Supabase의 insert는 리스트를 받아 한 번에 모든 데이터를 삽입할 수 있습니다.
    response = await db.table("user_words").insert(words).execute()
    return response.data if response.data else []

async def delete_wordbook(db: AsyncClient, wordbook_id: int, user_id: str):
    # ON DELETE CASCADE 옵션 덕분에, 단어장이 삭제되면 관련된 단어들도 자동으로 함께 삭제됩니다.
    response = await db.table("wordbooks").delete().eq("id", wordbook_id).eq("user_id", user_id).execute()
    return response.data

async def update_word_favorite_status(db: AsyncClient, word_id: int, is_favorite: bool):
    response = await db.table("user_words").update({"is_favorite": is_favorite}).eq("id", word_id).execute()
    return response.data[0] if response.data else None

async def get_favorite_words(db: AsyncClient, user_id: str):
    response = await db.table("user_words").select("*, wordbooks!inner(*)").eq(
        "wordbooks.user_id", user_id
    ).eq(
        "is_favorite", True
    ).order('created_at', desc=True).execute()

    return response.data

async def get_word_stats_by_user(db: AsyncClient, user_id: str):
    response = await db.rpc('get_user_word_stats', {'p_user_id': user_id}).single().execute()
    return response.data

async def get_all_words_by_user(db: AsyncClient, user_id: str, status: Optional[str] = None):
    query = db.table("user_words").select("*, wordbooks!inner(*)").eq("wordbooks.user_id", user_id)

    if status == 'memorized':
        query = query.eq('is_memorized', True)
    elif status == 'not_memorized':
        query = query.eq('is_memorized', False)

    response = await query.order('created_at', desc=True).execute()
<<<<<<< HEAD
    return response.data
=======
    return response.data
>>>>>>> origin/master
